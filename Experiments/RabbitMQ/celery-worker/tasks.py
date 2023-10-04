from celery import Celery 
from time import sleep
from llm import LLM
from video_parsing import pars

app = Celery('tasks', broker='amqp://guest:guest@rabbitmq', backend='redis://redis')

@app.task 
def get_answer_task(question,llm_model, llm_token):
    return LLM(llm_model,llm_token).get_answer(question)

@app.task
def exception():
    raise Exception('An exception raised in a Celery task')

@app.task
def pars_task(input_file, output_file="output.mp3"):
    pars(input_file, output_file)
    return f"Conversion completed. Output file: {output_file}"