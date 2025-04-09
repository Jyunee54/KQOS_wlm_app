from threading import *
import time
import random
import queue
 

def producer(q):
    while True:
        item = random.randint(1, 25)
        print("Producer Producting Item: ", item)
        q.put(item)
        print("Producer Notification")
        time.sleep(3)

def consumer(q):
    while True:
        print("Consumer waiting ")
        print("Consumer consumed the item:", q.get())
        time.sleep(3)
def main() :
    run_event = Event()
    q = queue.Queue()
    t1 = Thread(target = consumer, args = (q,))
    t2 = Thread(target = producer, args = (q,))
    t1.start()
    t2.start()
    try:
        while True:
            time.sleep(1)
            print("ping")
    except KeyboardInterrupt:
        run_event.clear()
        t1.join()
        t2.join()
        print("threads successfully closed")
        exit()
if __name__=="__main__":
    main()