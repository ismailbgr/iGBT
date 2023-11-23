import time
import base64
from celery import Celery

app = Celery(
    "videoparser", broker="amqp://localhost:5672", backend="redis://localhost:6379/0"
)

app.conf.task_routes = (
    [
        ("convert_video_to_mp3", {"queue": "videoparser"}),
        ("youtube_dl", {"queue": "videoparser"}),
    ],
)

b64 = ""
with open("test.mp4", "rb") as f:
    data = f.read()
    b64 = base64.b64encode(data)

res = app.send_task("convert_video_to_mp3", args=[b64])

while not res.ready():
    print("waiting...")
    time.sleep(1)

print(res.get())

with open("test.mp3", "wb") as f:
    f.write(base64.b64decode(res.get()))
