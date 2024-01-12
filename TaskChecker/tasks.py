from celery import Celery, current_task, states
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
######################################### DATABASE #########################################################
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
    try:
        current_task.update_state(state=states.STARTED)
    except Exception as e:
        print(f" State update failed: {e}", flush=True)

    task = app.AsyncResult(task_id)
    cur_task_state = task.state

    while not task.ready():
        print(f"Task {task_id} not ready")
        print(f"Task {task_id} state: {task.state}")
        if task.state != cur_task_state:
            cur_task_state = task.state
            change_task_state(task_id, cur_task_state)
            change_task_edit_date(task_id)
        time.sleep(10)

    is_video = get_task_attribute(task_id, "type").iloc[0]["type"] == "video"

    speech_texter_result = None
    if is_video:
        with allow_join_result():
            try:
                task_result = task.get()
                task_graph = get_task_graph(task_id)
                speech_texter_id = task_graph["speech_texter"][0]
                speech_texter_result = app.AsyncResult(speech_texter_id).get()
            except Exception as e:
                print(
                    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                )
                print(e, flush=True)
                task_result = "FAILED"
    else:
        with allow_join_result():
            task_result = task.get()

    task_result = str(task_result).replace("'", "&#39;").replace('"', "&#34;")
    change_task_state(task_id, task_result)
    change_task_edit_date(task_id)
    if speech_texter_result is not None:
        change_input_text(task_id, speech_texter_result)
    return task_result
