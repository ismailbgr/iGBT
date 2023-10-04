from tasks import get_answer_task
from time import sleep
import sys
 
def main():




    
    result = get_answer_task.delay(sys.argv[1])
    while not result.ready():
        print("Waiting for result...")
        sleep(1)
    print(result.get())

if __name__ == '__main__':
    main()

if __name__ == 'main_q':    
    print("not concerned yet")

