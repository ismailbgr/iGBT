from sqlalchemy import create_engine
from sqlalchemy.sql import text
import hashlib
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


################################################################
#################### INITIALIZATION ############################
################################################################


def init_db():
    global engine
    engine = create_engine("postgresql://igbt:bitircez@postgres/igbt")
    print("Connected to database.")


################################################################
#################### ADDING TO DATABASE #######################
################################################################


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


def add_task_with_thumbnail(taskid, thumbnail, file_name, type, input_text):
    current_date = pd.Timestamp.now()
    input_text = str(input_text).replace("'", "&#39;").replace('"', "&#34;")
    query = f"insert into \"Task\" (task_id, thumbnail, task_name, task_start_date, type, input_text, is_finished) values('{taskid}', '{thumbnail}', '{file_name}', '{current_date}', '{type}', '{input_text}', '{False}');"
    print(query)
    engine.execute(text(query))


def add_task_without_thumbnail(taskid, file_name, type, input_text):
    current_date = pd.Timestamp.now()
    input_text = str(input_text).replace("'", "&#39;").replace('"', "&#34;")
    query = f"insert into \"Task\" (task_id, task_name, task_start_date, type, input_text, is_finished) values('{taskid}', '{file_name}', '{current_date}', '{type}', '{input_text}', '{False}');"
    print(query)
    engine.execute(text(query))


def add_entry_to_usertask(task_id, user_id):
    query = f"insert into \"UserTask\" values('{user_id}', '{task_id}');"

    print(query)
    engine.execute(text(query))


def add_task_graph(llm_id, speech_texter_id, video_parser_id, task_id):
    query = f"insert into \"TaskGraph\" (llm, speech_texter, video_parser, task_id) values('{llm_id}', '{speech_texter_id}', '{video_parser_id}', '{task_id}');"
    print(query)
    engine.execute(text(query))


################################################################
#################### GETTING FROM DATABASE #####################
################################################################


def get_data_from_db_userid(userid):
    global engine
    query = 'select * from "user" where user_id = ' + str(userid)
    print(query)
    user = pd.read_sql_query(query, con=engine)
    # set userid to string
    user["user_id"] = user["user_id"].astype(str)
    test_data = user.to_json(orient="records")
    return test_data


def get_user_from_database_by_username(username, password):
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


def get_tasks_of_user_by_id(userid):
    query = (
        'select "Task".task_id, "Task".result, "Task".task_start_date, "Task".task_last_edit_date, "Task".type, "Task".task_name,"Task".thumbnail, "Task".is_finished from "Task" inner join "UserTask" on "Task".task_id = "UserTask".task_id where "UserTask".user_id = '
        + str(userid)
    )
    print(query)
    tasks = pd.read_sql_query(query, con=engine)
    print(tasks)
    tasks["task_id"] = tasks["task_id"].astype(str)
    tasks["result"] = tasks["result"].astype(str)
    tasks["task_start_date"] = tasks["task_start_date"].astype(str)
    tasks["task_last_edit_date"] = tasks["task_last_edit_date"].astype(str)
    tasks["type"] = tasks["type"].astype(str)
    tasks["task_name"] = tasks["task_name"].astype(str)
    tasks["thumbnail"] = tasks["thumbnail"].astype(str)
    tasks["is_finished"] = tasks["is_finished"].astype(bool)

    return tasks


def get_task_by_id(taskid):
    query = 'select * from "Task" where task_id = \'' + taskid + "'"
    print(query)
    tasks = pd.read_sql_query(query, con=engine)
    print(tasks)
    return tasks


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


################################################################
#################### UPDATING DATABASE #########################
################################################################


def update_task_attribute(task_id, attribute, value):
    query = f"update \"Task\" set {attribute} = '{value}' where task_id = '{task_id}';"

    print(query)
    engine.execute(text(query))


def update_user(user_id, ad, soyad, telefon):
    global engine
    query = f"update \"user\" set ad = '{ad}', soyad = '{soyad}', telefon = '{telefon}'  where user_id = '{user_id}';"
    print(query)
    engine.execute(text(query))


################################################################
#################### CHECKING DATABASE #########################
################################################################


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


def check_if_user_has_task(userid, taskid):
    query = (
        'select * from "UserTask" where user_id = '
        + str(userid)
        + " and task_id = '"
        + taskid
        + "'"
    )
    print(query)
    tasks = pd.read_sql_query(query, con=engine)
    print(tasks)
    if tasks.empty:
        return False
    else:
        return True


################################################################
#################### REMOVING FROM DATABASE ####################
################################################################


def remove_text_from_db(task_id):
    # then remove from UserTask
    query = f"delete from \"UserTask\" where task_id = '{task_id}';"
    print(query)
    engine.execute(text(query))
    # then remove from Task
    query = f"delete from \"Task\" where task_id = '{task_id}';"
    print(query)
    engine.execute(text(query))


def remove_video_from_db(task_id):
    # then remove from TaskGraph
    query = f"delete from \"TaskGraph\" where task_id = '{task_id}';"
    print(query)
    engine.execute(text(query))
    # then remove from UserTask
    query = f"delete from \"UserTask\" where task_id = '{task_id}';"
    print(query)
    engine.execute(text(query))
    # then remove from Task
    query = f"delete from \"Task\" where task_id = '{task_id}';"
    print(query)
    engine.execute(text(query))


################################################################
#################### OTHERS ####################################
################################################################


def encrypt_string(hash_string):
    global engine
    sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature
