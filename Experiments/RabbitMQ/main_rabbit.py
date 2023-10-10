from tasks import get_answer_task, pars_task, speech_to_text_task
from time import sleep
import sys
 
def main():

    #convert mp4 to mp3
    pars_task.delay("test_videos/news_kisa.mp4","output.mp3")
    while not pars_task.ready():
        print("Waiting for pars result...")
        sleep(1)

    question_prefix = """

    This is a transcript of video. your job is to summarize the video without missing any important information.
    try not to copy the transcript word by word.
    never give information that is not in the video.

    Here is the transcript:

    """

    #convert mp3 to text
    question = speech_to_text_task.delay("output.mp3","output.txt")
    while not question.ready():
        print("Waiting for question result...")
        sleep(1)
    #ask question
    result = get_answer_task.delay(question_prefix+question,"bard" ,llm_token="bgimLgh0_gdPWhrzo7sEvTXvh70Vj-OU-JmycMCBMQ-2GyymajdSqww4nn8nzW76DAjS0w.")
    while not result.ready():
        print("Waiting for summary result...")
        sleep(1)
    print(result.get())

if __name__ == '__main__':
    main()


