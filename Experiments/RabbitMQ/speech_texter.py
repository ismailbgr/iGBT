from google.cloud import speech_v1p1beta1 as speech
import io
import speech_recognition as sr
from pydub import AudioSegment

def speech_to_text(json_path, input_file, output_file, language_code="en-US"):    
    # Replace 'your-credentials.json' with the path to your service account credentials JSON file.
    credentials_path = json_path
    client = speech.SpeechClient.from_service_account_json(credentials_path)

    # Replace 'input.mp3' with the path to your MP3 file.
    input_file = 'input.mp3'

    # Configure audio settings
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",  # Change this to your desired language code
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
    

def speech_to_text_local(input_file, output_file):
    # Replace 'input.mp3' with the path to your MP3 file.

    #input_file = 'input.mp3'
    #output_file = 'transcribed.txt'  # The name of the output text file

    # Initialize the recognizer
    recognizer = sr.Recognizer()
    def convert_mp3_to_wav(mp3_file, wav_file):
        # Read the MP3 file
        audio = AudioSegment.from_mp3(mp3_file)

        # Export the audio to WAV format
        audio.export(wav_file, format="wav")
    # Usage example
    mp3_file = "output.mp3"
    wav_file = "audio.wav"
    convert_mp3_to_wav(mp3_file, wav_file)
    # Load the audio file
    with sr.AudioFile(wav_file) as source:
        audio_data = recognizer.record(source)

    # Use Google Web Speech API to transcribe the audio
    try:
        transcribed_text = recognizer.recognize_google(audio_data)
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