from celery import Celery, current_task, states
import base64
import uuid
from llm import LLM
import yaml

# Load config
config = None
with open("/app/config/config.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

print("config: ", config)

# Create the Celery app

app = Celery(
    "llm", broker=config["celery"]["broker"], backend=config["celery"]["backend"]
)

# app.conf.task_routes = {"summarize_text": {"queue": "llm"}}


print("initializing llm...")
llm = LLM(config["llm"]["model"])
print("llm initialized")


@app.task(name="summarize")
def summarize(text, model_name='ollama', api_key=None):
    print("summarizing...")
    print("text: ", text)

    llm = LLM(model_name, api_key)
    
    # change task state to started
    try:
        current_task.update_state(state=states.STARTED)
    except Exception as e:
        print(f" State update failed: {e}", flush=True)

    answer = llm.get_answer(text)

    return answer
