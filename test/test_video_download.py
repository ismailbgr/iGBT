import time
import base64
from celery import Celery

app = Celery(
    "videoparser", broker="amqp://localhost:5672", backend="redis://localhost:6379/0"
)
# debug app
app.conf.task_routes = (
    [
        ("convert_video_to_mp3", {"queue": "videoparser"}),
        ("youtube_dl", {"queue": "videoparser"}),
    ],
)

url = "https://www.youtube.com/watch?v=AxAlCTcjjP0"

res = app.send_task("youtube_dl", args=[url])

while not res.ready():
    print("waiting...")
    print(res.state)
    time.sleep(1)

print(res.get())

with open("dltest.mp4", "wb") as f:
    f.write(base64.b64decode(res.get()))
