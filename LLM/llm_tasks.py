from celery import Celery, current_task, states
import base64
import uuid
from llm import LLM

# Create the Celery app

app = Celery("llm", broker="amqp://rabbitmq:5672/", backend="redis://redis:6379/0")

# app.conf.task_routes = {"summarize_text": {"queue": "llm"}}


print("initializing llm...")
llm = LLM("ollama")
print("llm initialized")


@app.task(name="summarize")
def summarize(text):
    print("summarizing...")
    print("text: ", text)
    # change task state to started
    current_task.update_state(state=states.STARTED)
    return llm.get_answer(text)
