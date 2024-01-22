from sqlalchemy import create_engine
from sqlalchemy.sql import text
import pandas as pd
import yaml
import builtins

global engine

# Load config
config = None
with open("/app/config/config.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

if config is None:
    raise Exception("Config file not found")

print("config: ", config)


def print(*args, **kwargs):
    if config["verbose"]:
        return builtins.print(*args, flush=True, **kwargs)
    else:
        if "force" in kwargs:
            if kwargs["force"]:
                return builtins.print(*args, flush=True, **kwargs)
        else:
            return


def init_db():
    global engine
    engine = create_engine("postgresql://igbt:bitircez@postgres/igbt")
    print("Connected to database.")


def get_task_graph(taskid):
    query = 'select * from "TaskGraph" where task_id = \'' + taskid + "'"
    print(query)
    tasks = pd.read_sql_query(query, con=engine)
    print(tasks)
    return tasks


def get_task_attribute(task_id, attribute):
    query = f"select {attribute} from \"Task\" where task_id = '{task_id}';"
    print(query)
    result = pd.read_sql_query(query, con=engine)
    print(result)
    return result


def set_task_attribute(task_id, attribute, value):
    query = f"update \"Task\" set {attribute} = '{value}' where task_id = '{task_id}';"
    print(query)
    engine.execute(text(query))
