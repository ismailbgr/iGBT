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
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from celery import Celery
from celery import signature
import base64
import hashlib
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


try:
    engine = create_engine("postgresql://igbt:bitircez@postgres/igbt")
    print("Connected to database.")
except Exception as e:
    print("Connection Error.")
    exit()


def encrypt_string(hash_string):
    sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature


def get_data_from_db_userid(userid):
    query = 'select * from "user" where user_id = ' + str(userid)
    print(query)
    user = pd.read_sql_query(query, con=engine)
    # set userid to string
    user["user_id"] = user["user_id"].astype(str)
    test_data = user.to_json(orient="records")
    return test_data


def check_user_from_database(username, password):
    query = (
        'select * from "user" where email = \''
        + username
        + "' and saltedpassword = '"
        + password
        + "'"
    )
    print(query)
    user = pd.read_sql_query(query, con=engine)
    user["user_id"] = user["user_id"].astype(str)
    test_data = user.to_json(orient="records")
    return test_data


def check_email_available(email):
    query = 'select * from "user" where email = \'' + email + "'"
    print(query)
    user = pd.read_sql_query(query, con=engine)
    # if user is empty then email is available
    print(user.empty)
    if user.empty:
        return True
    else:
        return False


def add_user_to_db(
    e_mail,
    personname,
    personsurname,
    telephoneno,
    saltedpassword,
    is_admin,
):
    if telephoneno == "":
        telephoneno = "NULL"
    else:
        telephoneno = "'" + telephoneno + "'"
    query = (
        'insert into "user"(ad, soyad, email, telefon, saltedpassword, is_admin) values(\''
        + personname
        + "','"
        + personsurname
        + "','"
        + e_mail
        + "',"
        + telephoneno
        + ",'"
        + saltedpassword
        + "',"
        + str(is_admin)
        + ");"
    )

    query = str(query)

    print(query)
    engine.execute(text(query))


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
        global client
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
        # TODO: update user info
        return render_template("profile.html")


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
def upload_video():
    global client
    if request.method == "POST":
        # Check if the post request has the file part
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)
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
        # get the task id
        task_id = res.id

        # save the thumbnail as base64
        query = f"insert into \"Task\" (task_id, thumbnail) values ('{task_id}', '{thumbnail}')"

        engine.execute(text(query))

        celery.send_task(
            "check_task", args=[task_id, current_user.id], queue="taskchecker"
        )
        # redirect to the check status page
        return redirect(url_for("upload_video_result", id=task_id))
    return render_template("upload_video.html")


@flask_app.route("/video/<id>", methods=["GET", "POST"])
def upload_video_result(id):
    global client
    return render_template("upload_video.html", task_id=id)


@flask_app.route("/upload_text", methods=["GET", "POST"])
def upload_text():
    global client
    if request.method == "POST":
        text = request.form["w3review"]
        print(text)

        res = celery.send_task("summarize", args=[text])
        task_id = res.id
        celery.send_task(
            "check_task", args=[task_id, current_user.id], queue="taskchecker"
        )
        # return render_template("upload_text.html", task_id=task_id)
        return redirect(url_for("upload_text_result", id=task_id))
    return render_template("upload_text.html")


@flask_app.route("/text/<id>", methods=["GET", "POST"])
def upload_text_result(id):
    global client
    return render_template("upload_text.html", task_id=id)


# TODO: return progress if available
@flask_app.route("/check_text_status/<task_id>")
def check_text_status(task_id):
    global client
    task = celery.AsyncResult(task_id)
    print(task.state)
    if task.state == "SUCCESS" or task.state == "FAILURE":
        return task.get(), 286
    return task.state


@flask_app.route("/check_video_status/<task_id>")
def check_video_status(task_id):
    global client
    task = celery.AsyncResult(task_id)
    print(task.state)
    if task.state == "SUCCESS":
        return task.get(), 286
    elif task.state == "FAILURE":
        return 286
    return task.state


if __name__ == "app" or __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0")
