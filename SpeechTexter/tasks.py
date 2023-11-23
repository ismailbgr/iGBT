from celery import Celery
import base64
import uuid
from speech_texter import Speech2Text

# Create the Celery app

app = Celery(
    "speechtexter", broker="amqp://rabbitmq:5672", backend="redis://redis:6379/0"
)


@app.task(name="speech2text")
def speech2text(input_file, language_code="en-US", model_name="local"):
    input_file_name = str(uuid.uuid4()) + ".mp3"
    output_file = str(uuid.uuid4()) + ".txt"

    with open(input_file_name, "wb") as f:
        f.write(base64.b64decode(input_file))

    Speech2Text(
        input_file_name, output_file, language_code, model_name
    ).speech_to_text()
    with open(output_file, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
