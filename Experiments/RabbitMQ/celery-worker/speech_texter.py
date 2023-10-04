from google.cloud import speech_v1p1beta1 as speech
import io


def speech_texter(json_path, input_file, output_file, language_code="en-US"):    
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
    