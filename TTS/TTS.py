import pyttsx3
from gtts import gTTS
import sys

class TTS:
    def __init__(self, model):
        self.model = model

    def tts(self, text, lang="en", output_filename="voice.mp3"):
        if self.model == "gTTS":
            file = gTTS(text=text, lang=lang)
            filename = output_filename
            file.save(filename)
        elif self.model == "TTS":
            # TODO: add TTS code here
            pass
        elif self.model == "PYTTSX3":
            """
            TODO: control the voice speed and volume
            RATE
            rate = engine.getProperty('rate')   # getting details of current speaking rate
            print (rate)                        #printing current voice rate
            engine.setProperty('rate', 125)     # setting up new voice rate


            VOLUME
            volume = engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
            print (volume)                          #printing current volume level
            engine.setProperty('volume',1.0)
            """
            engine = pyttsx3.init()
            engine.save_to_file(text, output_filename)
            engine.runAndWait()
            engine.stop()
        else:
            print("no valid model name ")
            sys.exit(1)
