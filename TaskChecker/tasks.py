from celery import Celery, states
import time
import yaml

# Load config
config = None
with open("/app/config/config.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

print("config: ", config)

# Create the Celery app

app = Celery(
    "videoparser",
    broker=config["celery"]["broker"],
    backend=config["celery"]["backend"],
)


@app.task(name="check_task", time_limit=60, soft_time_limit=50)
def check_task(task_id):
    task = celery.AsyncResult(task_id)
    while not task.ready():
        print(f"Task {task_id} not ready")
        time.sleep(10)

    # TODO: Write to DB
