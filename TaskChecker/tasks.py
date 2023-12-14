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

try:
    engine = create_engine("postgresql://igbt:bitircez@postgres/igbt")
    print("Connected to database.")
except Exception as e:
    print("Connection Error.")
    exit()


def add_entry_to_usertask(task_id, user_id):
    query = f"insert into \"UserTask\" values('{user_id}', '{task_id}');"

    print(query)
    engine.execute(text(query))


def add_entry_to_task(task_id, result):
    query = f"insert into \"Task\" values('{task_id}', '{result}');"

    print(query)
    engine.execute(text(query))


def change_task_state(task_id, state):
    query = f"update \"Task\" set result = '{state}' where task_id = '{task_id}';"

    print(query)
    engine.execute(text(query))


# Create the Celery app


app = Celery(
    "taskchecker",
    broker=config["celery"]["broker"],
    backend=config["celery"]["backend"],
)


@app.task(name="check_task", time_limit=60, soft_time_limit=50)
def check_task(task_id, user_id):
    task = app.AsyncResult(task_id)
    cur_task_state = task.state
    # add_entry_to_task(task_id, cur_task_state)
    add_entry_to_usertask(task_id, user_id)
    while not task.ready():
        print(f"Task {task_id} not ready")
        if task.state != cur_task_state:
            cur_task_state = task.state
            change_task_state(task_id, cur_task_state)
        time.sleep(10)

    with allow_join_result():
        task_result = task.get()
        task_result = str(task_result).replace("'", "&#39;").replace('"', "&#34;")
    change_task_state(task_id, task_result)
    return task_result
    # TODO: Write to DB
