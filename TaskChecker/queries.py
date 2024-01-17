from sqlalchemy import create_engine
from sqlalchemy.sql import text
import pandas as pd

global engine


def init_db():
    global engine
    engine = create_engine("postgresql://igbt:bitircez@postgres/igbt")
    print("Connected to database.")


def get_task_graph(taskid):
    query = 'select * from "TaskGraph" where task_id = \'' + taskid + "'"
    print(query, flush=True)
    tasks = pd.read_sql_query(query, con=engine)
    print(tasks, flush=True)
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
