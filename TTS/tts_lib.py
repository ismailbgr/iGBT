import pyttsx3
from gtts import gTTS
import sys
import torch
from TTS.api import TTS


class iGBTTS:
    def __init__(self, model):
        self.model = model

    def tts(self, text, lang="en", output_filename="output.wav"):
        if self.model == "gTTS":
            file = gTTS(text=text, lang=lang)
            filename = output_filename
            file.save(filename)
        elif self.model == "TTS":
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print("tts_models/de/thorsten/tacotron2-DDC")
            tts = TTS(
                model_name="tts_models/en/ljspeech/tacotron2-DDC",
                progress_bar=False,
            ).to(device)
            print(output_filename)
            tts.tts_to_file(text=text, file_path=output_filename)
        elif self.model == "PYTTSX3":
            engine = pyttsx3.init()
            rate = engine.getProperty(
                "rate"
            )  
            engine.setProperty("rate", (rate * 45 / 100))

            engine.setProperty('volume',0.7)
            engine.save_to_file(text, output_filename)
            engine.runAndWait()
            engine.stop()
        else:
            print("no valid model name ")
            sys.exit(1)

    def tts_self_voice():
        # TODO: write the self voice method
        raise NotImplementedError()