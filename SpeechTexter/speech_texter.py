from google.cloud import speech_v1p1beta1 as speech
import io
import speech_recognition as sr
from pydub import AudioSegment


class Speech2Text:
    """_summary_
    This class is used to convert speech to text using google speech to text api or local speech to text api. The input file should be in mp3 format. The output file will be in txt format.
    """

    def __init__(
        self, input_file, output_file, language_code, model_name, json_path=None
    ):
        self.input_file = input_file
        self.output_file = output_file
        self.language_code = language_code
        self.model_name = model_name
        self.json_path = json_path
        if self.model_name == "google":
            self.client = speech.SpeechClient.from_service_account_json(self.json_path)
            self.config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language_code,  # Change this to your desired language code
            )

        elif self.model_name == "local":
            self.recognizer = sr.Recognizer()
        elif self.model_name == "mock":
            pass

        else:
            raise Exception("Invalid model name in speech to text.")

    def speech_to_text(self) -> str:
        """_summary_

        Raises:
            sr.UnknownValueError: _description_
            sr.RequestError: _description_
            Exception: _description_

        Returns:
            str: returns the transcribed text
        """
        if self.model_name == "google":
            with io.open(self.input_file, "rb") as audio_file:
                content = audio_file.read()
            audio = speech.RecognitionAudio(content=content)
            response = self.client.recognize(config=self.config, audio=audio)
            transcribed_text = ""
            for result in response.results:
                transcribed_text += result.alternatives[0].transcript + "\n"
            with open(self.output_file, "w", encoding="utf-8") as text_file:
                text_file.write(transcribed_text)

            return transcribed_text

        elif self.model_name == "local":

            def convert_mp3_to_wav(mp3_file, wav_file):
                # Read the MP3 file
                audio = AudioSegment.from_mp3(mp3_file)
                # Export the audio to WAV format
                audio.export(wav_file, format="wav")

            mp3_file = self.input_file
            wav_file = "audio.wav"
            convert_mp3_to_wav(mp3_file, wav_file)
            # Load the audio file
            with sr.AudioFile(wav_file) as source:
                audio_data = self.recognizer.record(source)
            # Use Google Web Speech API to transcribe the audio
            try:
                transcribed_text = self.recognizer.recognize_sphinx(audio_data, language=self.language_code)
                print("Transcription: ", transcribed_text)
                # Save the transcribed text to the output file
                with open(self.output_file, "w", encoding="utf-8") as text_file:
                    text_file.write(transcribed_text)

                print(f"Transcription completed. Text saved to {self.output_file}")
                return transcribed_text
            except sr.UnknownValueError:
                print("Google Web Speech API could not understand the audio")
                raise sr.UnknownValueError
            except sr.RequestError:
                print("Could not request results from Google Web Speech API")
                raise sr.RequestError
        elif self.model_name == "mock":
            text = """Johannes Gutenberg (1398 – 1468) was a German goldsmith and publisher who introduced printing to Europe. His introduction of mechanical movable
type printing to Europe started the Printing Revolution and is widely regarded as the most important event of the modern period. It played a key role in the
scientific revolution and laid the basis for the modern knowledge-based economy and the spread of learning to the masses.
"""

            with open(self.output_file, "w", encoding="utf-8") as text_file:
                text_file.write(text)
        else:
            raise Exception("Invalid model name in speech to text.")

    # write setter and getter methods for all the variables (does not q)


"""
    def speech_to_text_api(json_path, input_file, output_file, language_code="en-US"):    
        # Replace 'your-credentials.json' with the path to your service account credentials JSON file.
        credentials_path = json_path
        client = speech.SpeechClient.from_service_account_json(credentials_path)

        # Replace 'input.mp3' with the path to your MP3 file.
        input_file = 'input.mp3'

        # Configure audio settings
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_code,  # Change this to your desired language code
        )

        with io.open(input_file, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)

        response = client.recognize(config=config, audio=audio)

        transcribed_text = ""
        for result in response.results:
            transcribed_text += result.alternatives[0].transcript + "\n"

        with open(output_file, "w") as text_file:
            text_file.write(transcribed_text)
    

    def speech_to_text_local(input_file, output_file,language_code="es-US"):
        # Replace 'input.mp3' with the path to your MP3 file.
        # Initialize the recognizer
        recognizer = sr.Recognizer()
        def convert_mp3_to_wav(mp3_file, wav_file):
            # Read the MP3 file
            audio = AudioSegment.from_mp3(mp3_file)

            # Export the audio to WAV format
            audio.export(wav_file, format="wav")
        # Usage example
        mp3_file = input_file
        wav_file = "audio.wav"
        convert_mp3_to_wav(mp3_file, wav_file)
        # Load the audio file
        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)

        # Use Google Web Speech API to transcribe the audio
        try:
            transcribed_text = recognizer.recognize_google(audio_data, language=language_code)
            print("Transcription: ", transcribed_text)

            # Save the transcribed text to the output file
            with open(output_file, "w") as text_file:
                text_file.write(transcribed_text)

            print(f"Transcription completed. Text saved to {output_file}")
            return transcribed_text

        except sr.UnknownValueError:
            print("Google Web Speech API could not understand the audio")
            raise sr.UnknownValueError
        except sr.RequestError as e:
            print(f"Could not request results from Google Web Speech API; {e}")
            raise sr.RequestError
"""
