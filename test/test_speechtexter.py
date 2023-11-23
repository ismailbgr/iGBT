import time
import base64
from celery import Celery

app = Celery(
    "speechtexter", broker="amqp://localhost:5672", backend="redis://localhost:6379/0"
)


app.conf.task_routes = ([("speech2text", {"queue": "speechtexter"})],)

b64 = ""
with open("test.mp3", "rb") as f:
    data = f.read()
    b64 = base64.b64encode(data)

res = app.send_task("speech2text", args=[b64])

while not res.ready():
    print(res.state)
    print("waiting...")
    time.sleep(1)

print(res.get())

with open("test.txt", "wb") as f:
    f.write(base64.b64decode(res.get()))
