import sys
from time import sleep

import speech_recognition as sr
from llm import LLM
from speech_texter import Speech2Text
from tasks import get_answer_task
from video_parsing import pars

#convert mp4 to mp3
pars(sys.argv[1],"output.mp3")

question_prefix = """

This is a transcript of video. your job is to summarize the video without missing any important information.
try not to copy the transcript word by word.
never give information that is not in the video.

Here is the transcript:



"""

#convert mp3 to text
question = Speech2Text("output.mp3","output.txt","en-US","local").speech_to_text()

#ask question
print(LLM("bard","bgimLgh0_gdPWhrzo7sEvTXvh70Vj-OU-JmycMCBMQ-2GyymajdSqww4nn8nzW76DAjS0w.").get_answer(question_prefix+question))



#not going to work right now