from celery import Celery, current_task, states
import base64
import uuid
from llm import LLM
import yaml
import requests
import threading

# Load config
config = None
with open("/app/config/config.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

print("config: ", config)

# Create the Celery app

app = Celery(
    "llm", broker=config["celery"]["broker"], backend=config["celery"]["backend"]
)


def create_model():
    model_config = {
        "name": "summarizer",
        "modelfile": "FROM zephyr:latest\nSYSTEM Can you provide a comprehensive summary of the given video script? The summary should cover all the key points and main ideas presented in the original text, while also condensing the information into a concise and easy-to-understand format. Please ensure that the summary includes relevant details and examples that support the main ideas, while avoiding any unnecessary information or repetition. The length of the summary should be appropriate for the length and complexity of the original text, providing a clear and accurate overview without omitting any important information.",
    }
    threading.Thread(target=requests.post, args=("http://ollama:11434/api/create",), kwargs={"json": model_config}).start()

create_model()

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
