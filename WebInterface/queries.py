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


def update_user(user_id, ad, soyad, telefon):
    global engine
    query = f"update \"user\" set ad = '{ad}', soyad = '{soyad}', telefon = '{telefon}'  where user_id = '{user_id}';"
    print(query)
    engine.execute(text(query))


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
        'select "Task".task_id, "Task".result, "Task".task_start_date, "Task".task_last_edit_date, "Task".type, "Task".task_name,"Task".thumbnail from "Task" inner join "UserTask" on "Task".task_id = "UserTask".task_id where "UserTask".user_id = '
        + str(userid)
    )
    print(query, flush=True)
    tasks = pd.read_sql_query(query, con=engine)
    print(tasks, flush=True)
    tasks["task_id"] = tasks["task_id"].astype(str)
    tasks["result"] = tasks["result"].astype(str)
    tasks["task_start_date"] = tasks["task_start_date"].astype(str)
    tasks["task_last_edit_date"] = tasks["task_last_edit_date"].astype(str)
    tasks["type"] = tasks["type"].astype(str)
    tasks["task_name"] = tasks["task_name"].astype(str)
    tasks["thumbnail"] = tasks["thumbnail"].astype(str)

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


def add_task_with_thumbnail(taskid, thumbnail, file_name, type, input_text):
    current_date = pd.Timestamp.now()

    query = f"insert into \"Task\" (task_id, thumbnail, task_name, task_start_date, type, input_text) values('{taskid}', '{thumbnail}', '{file_name}', '{current_date}', '{type}', '{input_text}');"
    print(query, flush=True)
    engine.execute(text(query))


def add_entry_to_usertask(task_id, user_id):
    query = f"insert into \"UserTask\" values('{user_id}', '{task_id}');"

    print(query)
    engine.execute(text(query))


def change_task_state(task_id, state):
    query = f"update \"Task\" set result = '{state}' where task_id = '{task_id}';"

    print(query)
    engine.execute(text(query))


def change_task_edit_date(task_id):
    current_date = pd.Timestamp.now()
    query = f"update \"Task\" set task_last_edit_date = '{current_date}' where task_id = '{task_id}';"
    print(query)
    engine.execute(text(query))


def add_task_graph(llm_id, speech_texter_id, video_parser_id, task_id):
    query = f"insert into \"TaskGraph\" (llm, speech_texter, video_parser, task_id) values('{llm_id}', '{speech_texter_id}', '{video_parser_id}', '{task_id}');"
    print(query)
    engine.execute(text(query))


def get_input_text(task_id):
    query = f"select input_text from \"Task\" where task_id = '{task_id}';"
    print(query)
    input_text = pd.read_sql_query(query, con=engine)
    print(input_text)
    return input_text
