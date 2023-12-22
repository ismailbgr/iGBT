from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import json
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
    UserMixin,
)
import psycopg2

from celery import Celery
from celery import signature
import base64

import time
import yaml
import uuid

############################################################################################################
######################################### INITIALIZE APPS ##################################################
############################################################################################################


# creates a Flask object
flask_app = Flask(__name__)
flask_app.secret_key = "secret key"


# Load config
config = None
with open("/app/config/config.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

if config is None:
    raise Exception("Config file not found")

print("config: ", config)

# Create the Celery app

celery = Celery(
    "llm", broker=config["celery"]["broker"], backend=config["celery"]["backend"]
)

celery.conf.update(flask_app.config)

celery.conf.task_routes = (
    [
        ("summarize", {"queue": "llm"}),
        ("convert_video_to_mp3", {"queue": "videoparser"}),
        ("speech2text", {"queue": "speechtexter"}),
        ("taskchecker", {"queue": "taskchecker"}),
    ],
)


############################################################################################################
######################################### DATABASE##########################################################
############################################################################################################

import queries
from queries import *

queries.init_db()


############################################################################################################
######################################### LOGIN ############################################################
############################################################################################################

login_manager = LoginManager()
login_manager.init_app(flask_app)


class User(UserMixin):
    def __init__(self, id, name, surname, email, telephone, is_admin=False):
        self.id = int(id)
        self.ad = name
        self.soyad = surname
        self.email = email
        self.telefon = telephone
        self.is_admin = is_admin

    def __repr__(self):
        return "%d" % (self.id)

    def get_id(self):
        return "%d" % (self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_by_id(userid):
        from_server = get_data_from_db_userid(userid)

        if from_server == "ERRORAUTHENTICATION":
            return None
        else:
            user_data = pd.read_json(from_server)
            user = User(
                user_data["user_id"][0],
                user_data["ad"][0],
                user_data["soyad"][0],
                user_data["email"][0],
                user_data["telefon"][0],
                is_admin=user_data["is_admin"][0],
            )
            return user


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@login_manager.unauthorized_handler
def unauthorized_callback():
    flash("Please log in to access this page.", category="error")
    return redirect("/signin")


# create a route for home page
@flask_app.route("/")
def home():
    return render_template("index.html")


# create a route for about us page
@flask_app.route("/about_us")
def about():
    return render_template("about_us.html")


@flask_app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@flask_app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@flask_app.route("/profile/update", methods=["GET", "POST"])
@login_required
def profile_update():
    print("Profile update")
    if request.method == "POST":
        name = request.form["name"]
        surname = request.form["surname"]
        phone = request.form["phone"]
        password = request.form["password"]
        password = encrypt_string(str(password))
        if check_user_from_database(current_user.email, password) == "[]":
            flash("Şifre hatalı.", category="error")
            return redirect("/profile/update")
        else:
            update_user(current_user.id, name, surname, phone)
            flash("Güncelleme başarılı.", category="success")
            return redirect("/profile")

    return render_template("profile_update.html")


@flask_app.route("/profile/tasks", methods=["GET"])
@login_required
def profile_tasks():
    print("Profile tasks")
    tasks = get_tasks_of_user_by_id(current_user.id)
    results = tasks[
        [
            "task_id",
            "task_name",
            "thumbnail",
            "type",
            "task_start_date",
            "task_last_edit_date",
        ]
    ]
    results = results.sort_values(by="task_start_date", ascending=False)

    results = results.rename(columns={"task_name": "name", "thumbnail": "url"})
    # print(results.columns, flush=True)
    # print("RESULTS: ", results, flush=True)
    results = results.rename(columns={"task_name": "name", "thumbnail": "url"})
    # print(results.columns, flush=True)
    # print("RESULTS: ", results, flush=True)
    results = json.loads(results.to_json(orient="records"))
    # print("SHAPE: ", len(results), flush=True)
    for i in range(len(results)):
        if len(results[i]["name"]) > 20:
            results[i]["name"] = results[i]["name"][:17] + "..."
    return render_template("profile_tasks.html", tasks=results)


@flask_app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        surname = request.form["surname"]
        email = request.form["username"]
        telephone = request.form["phone"]
        password = request.form["password"]

        data = pd.DataFrame(
            {
                "ad": [name],
                "soyad": [surname],
                "email": [email],
                "saltedpassword": [password],
                "telefon": [telephone],
            }
        )

        if not check_email_available(email):
            flash("Bu e-mail adresi zaten kullanımda.", category="error")
            print("Email is not available.")
            return redirect("/signup")
        else:
            print("Email is available.")
            print("Name: ", name)
            print("Surname: ", surname)
            print("Email: ", email)
            print("Telephone: ", telephone)
            print("Password: ", password)
            personname = name
            personsurname = surname
            telephoneno = telephone
            password = password
            saltedpassword = encrypt_string(str(password))
            try:
                add_user_to_db(
                    email,
                    personname,
                    personsurname,
                    telephoneno,
                    saltedpassword,
                    False,
                )
                flash("Kayıt başarılı.", category="success")
                print("User added to database.")
                return redirect("/signin")
            except Exception as e:
                import traceback

                print(traceback.format_exc())
                flash("Kayıt başarısız.", category="error")
                return redirect("/signup")
    return render_template("signup.html")


@flask_app.route("/signin", methods=["GET", "POST"])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for("profile"))
    if request.method == "POST":
        username = request.form["username"]
        password = encrypt_string(str(request.form["password"]))
        print("Username: ", username)
        print("Password: ", password)

        check_user = check_user_from_database(username, password)

        if check_user == "[]":
            flash("Kullanıcı adı veya şifre hatalı.", category="error")
            return render_template("signin.html")

        user_data = pd.read_json(check_user)
        user_data["user_id"] = user_data["user_id"].astype(str)

        user = User(
            user_data["user_id"][0],
            user_data["ad"][0],
            user_data["soyad"][0],
            user_data["email"][0],
            user_data["telefon"][0],
            user_data["is_admin"][0],
        )

        login_user(user)
        return redirect(url_for("home"))

    return render_template("signin.html")


@flask_app.route("/upload_video", methods=["GET", "POST"])
@login_required
def upload_video():
    if request.method == "POST":
        # Check if the post request has the file part
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)
        file_name = file.filename
        # read the file
        uuid_str = str(uuid.uuid4())
        fpath = f"/data/{uuid_str}.mp4"
        file.save(fpath)

        thumbnail = request.form["thumbnail"]
        thumbnail = thumbnail.split(",")[1]

        # send the task to celery
        chain = signature(
            "convert_video_to_mp3", args=[fpath], queue="videoparser", app=celery
        )
        chain |= signature("speech2text", queue="speechtexter", app=celery)
        chain |= signature("summarize", queue="llm", app=celery)
        res = chain.apply_async()
        task_id = res.id

        llm_id = res.id
        speech_texter_id = res.parent.id
        video_parser_id = res.parent.parent.id

        add_task_with_thumbnail(task_id, thumbnail, file_name, "video", "PARSING VIDEO")
        add_entry_to_usertask(task_id, current_user.id)
        add_task_graph(llm_id, speech_texter_id, video_parser_id, task_id)

        check_task = celery.send_task(
            "check_task", args=[task_id, current_user.id], queue="taskchecker"
        )
        # redirect to the check status page
        return redirect(url_for("upload_video_result", task_id=task_id))
    return render_template("upload_video.html")


@flask_app.route("/video/<task_id>", methods=["GET"])
@login_required
def upload_video_result(task_id):
    if check_if_user_has_task(current_user.id, task_id):
        # TODO: create an endpoint to check the status of the task
        task = get_task_by_id(task_id)
        input_text = task.iloc[0]["input_text"]
        start_date = task.iloc[0]["task_start_date"].strftime("%d/%m/%Y %H:%M:%S")
        last_edit_date = (
            task.iloc[0]["task_last_edit_date"].strftime("%d/%m/%Y %H:%M:%S")
            if task.iloc[0]["task_last_edit_date"] is not None
            else None
        )
        return render_template(
            "upload_text.html",
            task_id=task_id,
            input_text=input_text,
            start_date=start_date,
            last_edit_date=last_edit_date,
        )
    else:
        flash("You do not have permission to view this task.", category="error")
        return redirect("/")


@flask_app.route("/upload_text", methods=["GET", "POST"])
@login_required
def upload_text():
    if request.method == "POST":
        text = request.form["w3review"]
        print(text)

        if len(text) < 2:
            flash("Lütfen en az 2 karakter giriniz.", category="error")
            return redirect("/")

        res = celery.send_task("summarize", args=[text])
        task_id = res.id

        thumbnail = "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"

        file_name = text[:20] + "..."

        add_task_with_thumbnail(task_id, thumbnail, file_name, "text", text)
        add_entry_to_usertask(task_id, current_user.id)

        celery.send_task(
            "check_task", args=[task_id, current_user.id], queue="taskchecker"
        )
        # return render_template("upload_text.html", task_id=task_id)
        return redirect(url_for("upload_text_result", task_id=task_id))
    return render_template("upload_text.html")


@flask_app.route("/upload_youtube", methods=["GET", "POST"])
@login_required
def upload_youtube():
    if request.method == "POST":
        url = request.form["youtube_link"]
        print(url)

        # res = celery.send_task("summarize", args=[text])
        chain = signature("youtube_dl", args=[url], queue="videoparser", app=celery)
        chain |= signature("speech2text", queue="speechtexter", app=celery)
        chain |= signature("summarize", queue="llm", app=celery)

        res = chain.apply_async()
        task_id = res.id

        thumbnail = "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"

        # TODO: Get youtube title without importing pytube in webinterface
        from pytube import YouTube

        title = YouTube(url).title

        llm_id = res.id
        speech_texter_id = res.parent.id
        video_parser_id = res.parent.parent.id

        add_task_with_thumbnail(task_id, thumbnail, title, "video", "PARSING VIDEO")
        add_entry_to_usertask(task_id, current_user.id)
        add_task_graph(llm_id, speech_texter_id, video_parser_id, task_id)

        celery.send_task(
            "check_task", args=[task_id, current_user.id], queue="taskchecker"
        )
        # return render_template("upload_text.html", task_id=task_id)
        return redirect(url_for("upload_video_result", task_id=task_id))
    return render_template("upload_video.html")


@flask_app.route("/text/<task_id>", methods=["GET", "POST"])
@login_required
def upload_text_result(task_id):
    if check_if_user_has_task(current_user.id, task_id):
        task = get_task_by_id(task_id)
        input_text = task.iloc[0]["input_text"]
        start_date = task.iloc[0]["task_start_date"].strftime("%d/%m/%Y %H:%M:%S")
        last_edit_date = (
            task.iloc[0]["task_last_edit_date"].strftime("%d/%m/%Y %H:%M:%S")
            if task.iloc[0]["task_last_edit_date"] is not None
            else None
        )
        return render_template(
            "upload_text.html",
            task_id=task_id,
            input_text=input_text,
            start_date=start_date,
            last_edit_date=last_edit_date,
        )
    else:
        flash("You do not have permission to view this task.", category="error")
        return redirect("/")


# TODO: return progress if available
@flask_app.route("/check_text_status/<task_id>")
@login_required
def check_text_status(task_id):
    task = celery.AsyncResult(task_id)

    if task.state == "PENDING" and check_if_user_has_task(current_user.id, task_id):
        result = get_task_by_id(task_id).iloc[0]["result"]
        print("RESULT: ", result, flush=True)
        if result != "0":
            return result, 286

    print(task.state)
    if task.state == "SUCCESS" or task.state == "FAILURE":
        return task.get(), 286
    return task.state


@flask_app.route("/check_video_status/<task_id>")
@login_required
def check_video_status(task_id):
    task = celery.AsyncResult(task_id)

    if task.state == "PENDING" and check_if_user_has_task(current_user.id, task_id):
        result = get_task_by_id(task_id).iloc[0]["result"]
        print("RESULT: ", result, flush=True)
        if result != "0":
            return result, 286

    print(task.state)
    if task.state == "SUCCESS":
        return task.get(), 286
    elif task.state == "FAILURE":
        return "", 286
    return task.state


if __name__ == "app" or __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0")
