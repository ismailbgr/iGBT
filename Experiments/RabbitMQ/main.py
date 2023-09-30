from tasks import get_answer_from_llm
from tasks import exception_example
from time import sleep
 
# result = get_answer_from_llm.delay("What is the capital of Turkey?")
result = exception_example.delay()

while not result.ready():
    print("Waiting for result...")a
    sleep(1)

print(result.get())