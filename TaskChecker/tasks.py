from celery import Celery, states
import time
import yaml
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from celery.result import allow_join_result

# Load config
config = None
with open("/app/config/config.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

print("config: ", config)


############################################################################################################
######################################### DATABASE##########################################################
############################################################################################################

import queries
from queries import *

queries.init_db()


# Create the Celery app


app = Celery(
    "taskchecker",
    broker=config["celery"]["broker"],
    backend=config["celery"]["backend"],
)


@app.task(name="check_task")
def check_task(task_id, user_id):
    task = app.AsyncResult(task_id)
    cur_task_state = task.state

    while not task.ready():
        print(f"Task {task_id} not ready")
        print(f"Task {task_id} state: {task.state}")
        if task.state != cur_task_state:
            cur_task_state = task.state
            change_task_state(task_id, cur_task_state)
        time.sleep(10)

    with allow_join_result():
        try:
            task_result = task.get()
        except:
            print(
                "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            )
            task_result = "FAILED"

        task_result = str(task_result).replace("'", "&#39;").replace('"', "&#34;")
    change_task_state(task_id, task_result)
    return task_result
    # TODO: Write to DB
