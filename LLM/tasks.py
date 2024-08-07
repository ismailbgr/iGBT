from time import sleep
from celery import Celery, current_task, states
from llm import LLM
import yaml
import requests
import threading
from celery.result import allow_join_result

# Load config
config = None
with open("/app/config/config.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

print("config: ", config)

# Create the Celery app

app = Celery(
    "llm", broker=config["celery"]["broker"], backend=config["celery"]["backend"]
)
app.conf.task_routes = (
    [
        ("classify_sentiment", {"queue": "sentimentclassifier"}),
    ],
)


def create_model():
    model_config = {
        "name": "summarizer",
        "modelfile": "FROM mistral:7b-instruct\nSYSTEM You are a summarizing AI. Provide a comprehensive summary of the given video script? The summary should cover all the key points and main ideas presented in the original text, while also condensing the information into a concise and easy-to-understand format. Ensure that the summary includes relevant details and examples that support the main ideas, while avoiding any unnecessary information or repetition. The length of the summary should be appropriate for the length and complexity of the original text, providing a clear and accurate overview without omitting any important information. Do not mention that it is an video script.",
    }
    threading.Thread(
        target=requests.post,
        args=("http://ollama:11434/api/create",),
        kwargs={"json": model_config},
    ).start()


create_model()

# app.conf.task_routes = {"summarize_text": {"queue": "llm"}}


print("initializing llm...")
llm = LLM(config["llm"]["model"])
print("llm initialized")


@app.task(name="summarize")
def summarize(text, model_name="ollama", api_key=None):
    print("summarizing...")
    print("text: ", text)

    llm = LLM(model_name, api_key)

    # change task state to started
    try:
        current_task.update_state(state=states.STARTED)
    except Exception as e:
        print(f" State update failed: {e}", flush=True)

    answer = llm.get_answer(text)

    is_finance_video = llm.get_finance_answer(text)
    if is_finance_video:
        task = app.send_task("classify_sentiment", args=[text])
        while not task.ready():
            print(f"Task {task.id} not ready")
            print(f"Task {task.id} state: {task.state}")
            sleep(1)
        with allow_join_result():
            sentiment = task.get()
            print(f"Sentiment: {sentiment}")
            return f"{answer} \n\n `Financial Impact: {sentiment}`"
    return answer
