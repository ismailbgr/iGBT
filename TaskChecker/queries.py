from sqlalchemy import create_engine
from sqlalchemy.sql import text

global engine


def init_db():
    global engine
    engine = create_engine("postgresql://igbt:bitircez@postgres/igbt")
    print("Connected to database.")


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
