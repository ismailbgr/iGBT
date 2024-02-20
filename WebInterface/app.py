from io import StringIO
import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
    UserMixin,
)
from queries import *
from celery import Celery, signature

import pandas as pd
import json
import yaml
import uuid
import yt_dlp
import builtins

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


def print(*args, **kwargs):
    if config["verbose"]:
        return builtins.print(*args, flush=True, **kwargs)
    else:
        if "force" in kwargs:
            if kwargs["force"]:
                return builtins.print(*args, flush=True, **kwargs)
        else:
            return


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
        ("tts", {"queue": "tts"}),
    ],
)
available_llms = [
    {"name": "Ollama", "isApiRequired": False},
    {"name": "Chat GPT", "isApiRequired": True},
    {"name": "Bard", "isApiRequired": True},
]

convert_llm_name = {
    "Ollama": "ollama",
    "Chat GPT": "gpt3",
    "Bard": "bard",
}

############################################################################################################
######################################### DATABASE##########################################################
############################################################################################################

init_db()

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
            user_data = pd.read_json(StringIO(from_server))
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


@flask_app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


############################################################################################################
############################################ HOME ###########################################################
############################################################################################################


# create a route for home page
@flask_app.route("/")
def home():
    return render_template("index.html", llms=available_llms)


############################################################################################################
############################################ ABOUT US #######################################################
############################################################################################################


# create a route for about us page
@flask_app.route("/about_us")
def about():
    return render_template("about_us.html")


############################################################################################################
############################################ PROFILE ########################################################
############################################################################################################


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
        if get_user_from_database_by_username(current_user.email, password) == "[]":
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
    results = results.rename(columns={"task_name": "name", "thumbnail": "url"})
    results = json.loads(results.to_json(orient="records"))

    for i in range(len(results)):
        if len(results[i]["name"]) > 20:
            results[i]["name"] = results[i]["name"][:17] + "..."
    return render_template("profile_tasks.html", tasks=results)


############################################################################################################
############################################ SIGNUP - SIGNIN ###############################################
############################################################################################################


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

        check_user = get_user_from_database_by_username(username, password)

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


############################################################################################################
############################################ UPLOAD ENDPOINTS ##############################################
############################################################################################################


@flask_app.route("/upload_video", methods=["POST"])
@login_required
def upload_video():
    if request.method == "POST":
        llm = request.form["llm"]
        print(llm)

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
        model_name = request.form["llm"]
        api_key = request.form["apikey"]
        # send the task to celery
        chain = signature(
            "convert_video_to_mp3", args=[fpath], queue="videoparser", app=celery
        )
        chain |= signature("speech2text", queue="speechtexter", app=celery)
        chain |= signature(
            "summarize",
            kwargs={"model_name": convert_llm_name[model_name], "api_key": api_key},
            queue="llm",
            app=celery,
        )
        res = chain.apply_async()
        task_id = res.id

        llm_id = res.id
        speech_texter_id = res.parent.id
        video_parser_id = res.parent.parent.id

        add_task_with_thumbnail(task_id, thumbnail, file_name, "video", "PARSING VIDEO")
        add_entry_to_usertask(task_id, current_user.id)
        add_task_graph(llm_id, speech_texter_id, video_parser_id, task_id)

        celery.send_task(
            "check_task", args=[task_id, current_user.id], queue="taskchecker"
        )
        # redirect to the check status page
        return redirect(url_for("upload_video_result", task_id=task_id))
    return render_template("upload_video.html")


@flask_app.route("/upload_text", methods=["GET", "POST"])
@login_required
def upload_text():
    if request.method == "POST":
        text = request.form["w3review"]
        print(text)

        if len(text) < 2:
            flash("Lütfen en az 2 karakter giriniz.", category="error")
            return redirect("/")
        model_name = request.form["llm"]
        print(model_name)
        api_key = request.form["apikey"]
        res = celery.send_task(
            "summarize",
            args=[text],
            kwargs={"model_name": convert_llm_name[model_name], "api_key": api_key},
            queue="llm",
        )
        task_id = res.id

        file_name = text[:20] + "..."

        add_task_without_thumbnail(task_id, file_name, "text", text)
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

        try:
            with yt_dlp.YoutubeDL() as ydl:
                info_dict = ydl.extract_info(url, download=False)
                title = info_dict.get("title", None)
        except:
            flash("Invalid youtube link.", category="error")
            return redirect("/")

        model_name = request.form["llm"]
        api_key = request.form["apikey"]
        # res = celery.send_task("summarize", args=[text])
        chain = signature("youtube_dl", args=[url], queue="videoparser", app=celery)
        chain |= signature("speech2text", queue="speechtexter", app=celery)
        chain |= signature(
            "summarize",
            kwargs={"model_name": convert_llm_name[model_name], "api_key": api_key},
            queue="llm",
            app=celery,
        )

        res = chain.apply_async()
        task_id = res.id
        llm_id = res.id
        speech_texter_id = res.parent.id
        video_parser_id = res.parent.parent.id
        title = str(title).replace("'", "&#39;").replace('"', "&#34;")

        add_task_without_thumbnail(task_id, title, "video", "PARSING VIDEO")
        add_entry_to_usertask(task_id, current_user.id)
        add_task_graph(llm_id, speech_texter_id, video_parser_id, task_id)

        celery.send_task(
            "check_task", args=[task_id, current_user.id], queue="taskchecker"
        )
        # return render_template("upload_text.html", task_id=task_id)
        return redirect(url_for("upload_video_result", task_id=task_id))
    return render_template("upload_video.html")


############################################################################################################
############################################ RESULTS ########################################################
############################################################################################################


@flask_app.route("/video/<task_id>", methods=["GET"])
@login_required
def upload_video_result(task_id):
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
            "upload_video.html",
            task_id=task_id,
            input_text=input_text,
            start_date=start_date,
            last_edit_date=last_edit_date,
        )
    else:
        flash("You do not have permission to view this task.", category="error")
        return redirect("/")


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


############################################################################################################
##################################### UPDATE ENDPOINTS #####################################################
############################################################################################################


@flask_app.route("/check/<task_id>")
@login_required
def check(task_id):
    task = celery.AsyncResult(task_id)
    if check_if_user_has_task(current_user.id, task_id):
        task_database = get_task_by_id(task_id).iloc[0]
        values = {}
        values["start_date"] = task_database["task_start_date"].strftime(
            "%d/%m/%Y %H:%M:%S"
        )
        values["last_edit_date"] = (
            task_database["task_last_edit_date"].strftime("%d/%m/%Y %H:%M:%S")
            if task_database["task_last_edit_date"] is not None
            else time.strftime("%d/%m/%Y %H:%M:%S")
        )
        if task.state == "PENDING" and task_database["result"] != "0":
            print("RESULT: ", task_database["result"])
            values["result"] = task_database["result"]
            values["input_text"] = task_database["input_text"]
            return values, 286
        elif task.state == "SUCCESS" or task.state == "FAILURE":
            values["result"] = task.get()
            values["input_text"] = task_database["input_text"]
            print(values)
            return values, 286
        else:
            values["result"] = task.state
            values["input_text"] = task_database["input_text"]
            print(values)
            return values
    else:
        flash("You do not have permission to view this task.", category="error")
        return redirect("/")


@flask_app.route("/check_tts/<task_id>")
@login_required
def check_tts(task_id):
    file_path = "/data/" + task_id + ".wav"
    if os.path.exists(file_path):
        print("File exists")

        return {"isFinished": "True"}, 286
    else:
        return {"isFinished": "False"}, 420


@flask_app.route("/get_tts/<task_id>")
@login_required
def get_tts(task_id):
    file_path = "/data/" + task_id + ".wav"
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404


############################################################################################################
############################################ RETRY #########################################################
############################################################################################################


@flask_app.route("/retry_text/<task_id>", methods=["GET", "POST"])
@login_required
def retry_text(task_id):
    # if task is not finished, return
    if not get_task_attribute(task_id, "is_finished").iloc[0]["is_finished"]:
        flash("You can only retry finished tasks.", category="error")
        return redirect("/text/" + task_id)
    # print form
    new_text = request.form["input_text"]
    print(new_text)
    # send task to
    remove_text_from_db(task_id)

    old_task = celery.AsyncResult(task_id)
    old_task.forget()

    celery.send_task("summarize", args=[new_text], queue="llm", task_id=task_id)

    file_name = new_text[:20] + "..."

    add_task_without_thumbnail(task_id, file_name, "text", new_text)
    add_entry_to_usertask(task_id, current_user.id)

    celery.send_task("check_task", args=[task_id, current_user.id], queue="taskchecker")

    return redirect("/text/" + task_id)


@flask_app.route("/retry_video/<task_id>", methods=["GET", "POST"])
@login_required
def retry_video(task_id):
    # if task is not finished, return
    if not get_task_attribute(task_id, "is_finished").iloc[0]["is_finished"]:
        flash("You can only retry finished tasks.", category="error")
        return redirect("/video/" + task_id)
    new_text = request.form["input_text"]
    print(new_text)

    old_task = celery.AsyncResult(task_id)
    old_task.forget()

    title = get_task_attribute(task_id, "task_name").iloc[0]["task_name"]
    thumbnail = get_task_attribute(task_id, "thumbnail").iloc[0]["thumbnail"]

    task_graph = get_task_graph(task_id)

    remove_video_from_db(task_id)
    # TODO: WebInterface: Previous text affects new text
    # assignees: ismailgbr
    # labels: bug

    llm_id = task_graph["llm"][0]
    speech_texter_id = task_graph["speech_texter"][0]
    video_parser_id = task_graph["video_parser"][0]

    add_task_with_thumbnail(task_id, thumbnail, title, "video", new_text)
    add_entry_to_usertask(task_id, current_user.id)
    add_task_graph(llm_id, speech_texter_id, video_parser_id, task_id)
    update_task_attribute(task_id, "is_finished", "True")

    celery.send_task("summarize", args=[new_text], queue="llm", task_id=task_id)

    celery.send_task("check_task", args=[task_id, current_user.id], queue="taskchecker")
    return redirect("/video/" + task_id)


############################################################################################################
############################################ REMOVE ########################################################
############################################################################################################


@flask_app.route("/remove_text/<task_id>", methods=["GET", "POST"])
@login_required
def remove_task(task_id):
    print(task_id)
    # revoke task
    celery.AsyncResult(task_id).revoke(terminate=True)
    remove_text_from_db(task_id)
    flash("Task removed.", category="success")
    return redirect("/profile/tasks")


@flask_app.route("/remove_video/<task_id>", methods=["GET", "POST"])
@login_required
def remove_video(task_id):
    print(task_id)
    celery.AsyncResult(task_id).revoke(terminate=True)
    remove_video_from_db(task_id)
    flash("Task removed.", category="success")
    return redirect("/profile/tasks")


############################################################################################################
############################################ TTS ############################################################
############################################################################################################


@flask_app.route("/tts/<task_id>", methods=["GET", "POST"])
@login_required
def tts(task_id):
    print(task_id)
    return render_template("tts.html", task_id=task_id)


@flask_app.route("/tts/<task_id>/send", methods=["GET", "POST"])
@login_required
def tts_send(task_id):
    print(task_id)
    print(request.form)
    input_text = request.form["input_text"]
    async_res = celery.send_task(
        "tts", args=["TTS", input_text, "en", task_id], queue="tts"
    )
    new_task_id = async_res.id
    print(new_task_id)
    return redirect("/tts/" + task_id)


############################################################################################################
############################################ MAIN ##########################################################
############################################################################################################

if __name__ == "app" or __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0")
