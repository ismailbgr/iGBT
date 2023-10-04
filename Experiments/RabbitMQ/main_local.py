from tasks import get_answer_task
from time import sleep
import sys
from video_parsing import pars
from speech_texter import speech_to_text, speech_to_text_local
from llm import LLM
import speech_recognition as sr

#convert mp4 to mp3
pars(sys.argv[1],"output.mp3")

#convert mp3 to text
question = speech_to_text_local("output.mp3","output.txt")

#ask question
print(LLM("bard","bgimLt_0gtUhWJU-lTiMZLPZanhGaiGd03G87F2cH_2_zFMnwNdzuO2cM7b7Tf1_X0aBIw.").get_answer(question))
