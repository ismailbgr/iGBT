from celery import Celery 
from time import sleep
from llm import LLM
from video_parsing import pars
from time import sleep

import speech_recognition as sr
from llm import LLM
from speech_texter import Speech2Text
from video_parsing import pars

app = Celery('tasks', broker='amqp://guest:guest@rabbitmq', backend='redis://redis')

@app.task 
def get_answer_task(question,llm_model="bard", llm_token="bgimLgh0_gdPWhrzo7sEvTXvh70Vj-OU-JmycMCBMQ-2GyymajdSqww4nn8nzW76DAjS0w."):
    return LLM(llm_model,llm_token).get_answer(question)

@app.task
def pars_task(input_file, output_file="output.mp3"):
    pars(input_file, output_file)
    return f"Conversion completed. Output file: {output_file}"

@app.task
def speech_to_text_task(input_file, output_file="output.txt", language_code="en-US", model_name="local"):
    converter = Speech2Text(input_file, output_file, language_code, model_name)
    text= converter.speech_to_text()
    return text
