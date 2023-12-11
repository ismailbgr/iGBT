# imports
from flask import Flask, render_template, request, redirect, url_for
from celery import Celery
from celery import signature
import base64
import time
import yaml
import uuid

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
    ],
)


@flask_app.route("/upload_video", methods=["GET", "POST"])
def upload_video():
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
        # send the task to celery
        chain = signature(
            "convert_video_to_mp3", args=[fpath], queue="videoparser", app=celery
        )
        chain |= signature("speech2text", queue="speechtexter", app=celery)
        chain |= signature("summarize", queue="llm", app=celery)
        res = chain.apply_async()
        # get the task id
        task_id = res.id

        # redirect to the check status page
        return redirect(url_for("upload_video_result", id=task_id))
    return render_template("upload_video.html")


@flask_app.route("/video/<id>", methods=["GET", "POST"])
def upload_video_result(id):
    return render_template("upload_video.html", task_id=id)


@flask_app.route("/upload_text", methods=["GET", "POST"])
def upload_text():
    if request.method == "POST":
        text = request.form["w3review"]
        print(text)

        res = celery.send_task("summarize", args=[text])
        task_id = res.id

        # return render_template("upload_text.html", task_id=task_id)
        return redirect(url_for("upload_text_result", id=task_id))
    return render_template("upload_text.html")


@flask_app.route("/text/<id>", methods=["GET", "POST"])
def upload_text_result(id):
    return render_template("upload_text.html", task_id=id)


# TODO: return progress if available
@flask_app.route("/check_text_status/<task_id>")
def check_text_status(task_id):
    task = celery.AsyncResult(task_id)
    print(task.state)
    if task.state == "SUCCESS" or task.state == "FAILURE":
        return task.get(), 286
    return task.state


@flask_app.route("/check_video_status/<task_id>")
def check_video_status(task_id):
    task = celery.AsyncResult(task_id)
    print(task.state)
    if task.state == "SUCCESS":
        return task.get(), 286
    elif task.state == "FAILURE":
        return 286
    return task.state


# create a route for about us page
@flask_app.route("/about_us")
def about():
    return render_template("about_us.html")


# create a route for home page
@flask_app.route("/")
def home():
    return render_template("index.html")


if __name__ == "app" or __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0")
