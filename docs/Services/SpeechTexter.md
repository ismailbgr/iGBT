# SpeechTexter

## Usage

SpeechTexter is a service that converts speech to text. It communicates with the reqired APIs to perform the conversion.

### Tasks

#### Speech2Text

```python

# speech_texter/tasks.py

def speech2text(

input_file_path,

language_code="en-US",

model_name=config["speechtexter"]["model_name"],

):
...

```

this method is used to convert speech to text. It receives the path of the input file, the language code of the input file, and the model name. It returns the text. can be called like this:

```python

res = celery_app.send_task("speech_texter.speech2text", args=["path/to/input/file"])

```

> currently, the only supported model is `local`. This means that the conversion is done locally using sphinx.
