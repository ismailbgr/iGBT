# imports
from flask import Flask, render_template, request, redirect, url_for
from celery import Celery
import base64
import time

# creates a Flask object
flask_app = Flask(__name__)


# creates a Celery object
celery = Celery(
    flask_app.name,
    broker="amqp://rabbitmq:5672/",
    backend="redis://redis:6379/0",
)
celery.conf.update(flask_app.config)

celery.conf.task_routes = (
    [
        ("summarize", {"queue": "llm"}),
    ],
)


@flask_app.route("/")
def index():
    return render_template("index.html")


@flask_app.route("/upload_video", methods=["GET", "POST"])
def upload_video():
    if request.method == "POST":
        # Check if the post request has the file part
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)
        # convert the file to base64
        data = file.read()
        b64 = base64.b64encode(data)
        # send the file to the celery task
        res = celery.send_task("convert_video_to_mp3", args=[b64])
        # wait for the task to finish
        while not res.ready():
            print("waiting...")
            time.sleep(1)
            # we will show a loading screen
            # while the task is running
            loading = True
        # get the result
        b64 = res.get()
        # decode the result
        data = base64.b64decode(b64)
        print(data)
        return redirect(url_for("upload_video"))
    return render_template("upload_video.html")


@flask_app.route("/upload_text", methods=["GET", "POST"])
def upload_text():
    if request.method == "POST":
        text = request.form["text"]
        print(text)

        res = celery.send_task("summarize", args=[text])
        task_id = res.id

        return render_template("upload_text.html", task_id=task_id)
    return render_template("upload_text.html")


# TODO: return progress if available
@flask_app.route("/check_status/<task_id>")
def check_status(task_id):
    task = celery.AsyncResult(task_id)
    if task.state == "SUCCESS":
        return task.get(), 286
    return task.state


# create a route for about us page
@flask_app.route("/about_us")
def about():
    return render_template("about_us.html")


# create a route for home page
@flask_app.route("/home")
def home():
    return render_template("index.html")


if __name__ == "app" or __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0")
