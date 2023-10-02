from tasks import get_answer_from_llm
from tasks import exception_example
from time import sleep
import sys
 
def main():
    result = get_answer_from_llm.delay(sys.argv[1])
    while not result.ready():
        print("Waiting for result...")
        sleep(1)
    print(result.get())

if __name__ == '__main__':
    main()

if __name__ == 'main_q':    
    print("not concerned yet")

