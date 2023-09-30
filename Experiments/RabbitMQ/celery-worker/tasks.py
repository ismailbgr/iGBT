from celery import Celery 
from time import sleep
from llm import LLM

app = Celery('tasks', broker='amqp://guest:guest@rabbitmq', backend='redis://redis')

@app.task 
def get_answer_from_llm(question):
    sleep(30)
    llm = LLM("bard","bgimLmavjMMRxUpfs_Hdy9DI31GegnmIzXLPwnxMxF3M_kL21AKzHs2OJarDpEhuXQa-Kg.")
    return llm.get_answer(question)

@app.task
def exception_example():
    raise Exception('An exception raised in a Celery task')