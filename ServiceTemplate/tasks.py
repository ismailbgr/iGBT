from celery import Celery
import base64
import uuid

# Create the Celery app

app = Celery(
    "videoparser", broker="amqp://rabbitmq:5672", backend="redis://redis:6379/0"
)


@app.task(name="example")
def example(input_file):
    uuidname = str(uuid.uuid4())
    with open(f"/tmp/{uuidname}.txt", "wb") as f:
        f.write(base64.b64decode(input_file))
    input_file = f"/tmp/{uuidname}.txt"
    output_file = f"/tmp/{uuidname}.txt"
    with open(output_file, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data)
    return b64
