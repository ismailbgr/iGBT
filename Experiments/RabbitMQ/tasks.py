from celery import Celery 
from time import sleep
from llm import LLM

app = Celery('tasks', broker='amqp://guest:guest@rabbitmq', backend='redis://redis')

@app.task 
def get_answer_from_llm(question,llm_model, llm_token):)
    return LLM(llm_model,llm_token).get_answer(question)

@app.task
def exception():
    raise Exception('An exception raised in a Celery task')