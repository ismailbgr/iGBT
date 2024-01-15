from celery import Celery
import time

input_text = """Johannes Gutenberg (1398 – 1468) was a German goldsmith and publisher who introduced printing to Europe. His introduction of mechanical movable
type printing to Europe started the Printing Revolution and is widely regarded as the most important event of the modern period. It played a key role in the
scientific revolution and laid the basis for the modern knowledge-based economy and the spread of learning to the masses.

Gutenberg many contributions to printing are: the invention of a process for mass-producing movable type, the use of oil-based ink for printing books, adjustable
molds, and the use of a wooden printing press. His truly epochal invention was the combination of these elements into a practical system that allowed the mass
production of printed books and was economically viable for printers and readers alike.
In Renaissance Europe, the arrival of mechanical movable type printing introduced the era of mass communication which permanently altered the structure of
society. The relatively unrestricted circulation of information—including revolutionary ideas—transcended borders, and captured the masses in the Reformation.
The sharp increase in literacy broke the monopoly of the literate elite on education and learning and bolstered the emerging middle class."""

app = Celery("tts", broker="amqp://localhost:5672", backend="redis://localhost:6379/0")

app.conf.task_routes = (
    [
        ("tts", {"queue": "tts"}),
    ],
)

res = app.send_task("tts", args=["TTS", input_text, "en", "output"])

while not res.ready():
    print("waiting...")
    print(res.state)
    time.sleep(1)

print(res.get())
