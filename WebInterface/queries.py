from sqlalchemy import create_engine
from sqlalchemy.sql import text
import hashlib
import pandas as pd

global engine


def init_db():
    global engine
    engine = create_engine("postgresql://igbt:bitircez@postgres/igbt")
    print("Connected to database.")


def encrypt_string(hash_string):
    global engine
    sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature


def get_data_from_db_userid(userid):
    global engine
    query = 'select * from "user" where user_id = ' + str(userid)
    print(query)
    user = pd.read_sql_query(query, con=engine)
    # set userid to string
    user["user_id"] = user["user_id"].astype(str)
    test_data = user.to_json(orient="records")
    return test_data


def check_user_from_database(username, password):
    global engine
    query = (
        'select * from "user" where email = \''
        + username
        + "' and saltedpassword = '"
        + password
        + "'"
    )
    print(query)
    user = pd.read_sql_query(query, con=engine)
    user["user_id"] = user["user_id"].astype(str)
    test_data = user.to_json(orient="records")
    return test_data


def check_email_available(email):
    global engine
    query = 'select * from "user" where email = \'' + email + "'"
    print(query)
    user = pd.read_sql_query(query, con=engine)
    # if user is empty then email is available
    print(user.empty)
    if user.empty:
        return True
    else:
        return False


def add_user_to_db(
    e_mail,
    personname,
    personsurname,
    telephoneno,
    saltedpassword,
    is_admin,
):
    global engine
    if telephoneno == "":
        telephoneno = "NULL"
    else:
        telephoneno = "'" + telephoneno + "'"
    query = (
        'insert into "user"(ad, soyad, email, telefon, saltedpassword, is_admin) values(\''
        + personname
        + "','"
        + personsurname
        + "','"
        + e_mail
        + "',"
        + telephoneno
        + ",'"
        + saltedpassword
        + "',"
        + str(is_admin)
        + ");"
    )

    query = str(query)

    print(query)
    engine.execute(text(query))


def get_tasks_of_user_by_id(userid):
    # We have 3 tables: Task, User, UserTask
    # Task: task_id, thumbnail, result
    # User: user_id, ad, soyad, email, telefon, saltedpassword, is_admin
    # UserTask: task_id, user_id
    query = (
        'select "Task".task_id, "Task".thumbnail, "Task".result from "Task" inner join "UserTask" on "Task".task_id = "UserTask".task_id where "UserTask".user_id = '
        + str(userid)
    )
    print(query, flush=True)
    tasks = pd.read_sql_query(query, con=engine)
    print(tasks, flush=True)
    tasks["task_id"] = tasks["task_id"].astype(str)
    tasks["result"] = tasks["result"].astype(str)
    return tasks


def get_task_by_id(taskid):
    # task_id is string
    query = 'select * from "Task" where task_id = \'' + taskid + "'"
    print(query, flush=True)
    tasks = pd.read_sql_query(query, con=engine)
    print(tasks, flush=True)
    return tasks


def check_if_user_has_task(userid, taskid):
    query = (
        'select * from "UserTask" where user_id = '
        + str(userid)
        + " and task_id = '"
        + taskid
        + "'"
    )
    print(query, flush=True)
    tasks = pd.read_sql_query(query, con=engine)
    print(tasks, flush=True)
    if tasks.empty:
        return False
    else:
        return True


def add_task_with_thumbnail(taskid, thumbnail):
    query = (
        f"insert into \"Task\" (task_id, thumbnail) values ('{taskid}', '{thumbnail}')"
    )
    print(query, flush=True)
    engine.execute(text(query))
