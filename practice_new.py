"""
Python threads with a `threading.Event` flag to allow for safe termination with
a `KeyboardInterrupt`.
While it is possible to have all threads abruptly terminate by setting 
`daemon == True` on the thread object, sometimes you need to perform cleanup,
so we essentially set a flag for the threads to check, assuming they all work
via an ongoing loop.
Note that this flag could be any object that evaluates to `True` or `False`,
not just a `threading.Event` object.
If you want a different sort of quitting flag, then just ensure that the object
a `__bool__` method defined that evaluates to `True` if it's time for the task
to stop and `False` otherwise.
We include some rather verbose logging to demonstrate what is going on during
each phase of the program.
"""
import logging
import threading
import time, queue, random, socket

# Configure logging
logging.basicConfig(level=logging.DEBUG)

q = queue.Queue()

# class Task:
#     """A simple class for performing a task."""
#     def __init__(self, quit_flag, name=None, interval=1,q=q):
#         if name is None:
#             name = id(self)
#         # Set up the task object
#         self.quit_flag = quit_flag
#         self.name = name
#         self.interval = interval
#         self.q=q
#         logging.debug("Task %s created"%self.name)

#     def run(self):
#         try:
#             logging.debug("Task %s started"%self.name)
#             while not self.quit_flag:
#                 logging.debug("Task %s is doing something"%self.name)
#                 self.q.put(self.name)
#                 time.sleep(self.interval)
#                 print(list(self.q.queue))
#         finally:
#             logging.debug("Task %s performing cleanup..."%self.name)
#             # Perform cleanup here
#             logging.debug("Task %s stopped."%self.name)

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

class ProducerTask:
    """A simple class for performing a task."""
    def __init__(self, quit_flag, name=None, interval=1,q=q, channel=1):
        if name is None:
            name = id(self)
        # Set up the task object
        self.quit_flag = quit_flag
        self.name = name
        self.interval = interval
        self.q=q
        self.channel = channel
        logging.debug("Task %s created"%self.name)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        self.client_socket.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")


    def run(self):
        try:
            logging.debug("Task %s started"%self.name)
            while not self.quit_flag:
                # logging.debug("Task %s is doing something"%self.name)
                time.sleep(self.interval)
                # item = random.randint(1, 25)
                self.client_socket.sendall("{:d}".format(self.channel).encode('utf-8'))
                item = (self.client_socket.recv(1024)).decode('utf-8')
                
                print("Producer Producting Item: ", item)
                q.put(item)
                time.sleep(3)
        finally:
            logging.debug("Task %s performing cleanup..."%self.name)
            # Perform cleanup here
            logging.debug("Task %s stopped."%self.name)


class ConsumerTask:
    def __init__(self, quit_flag, name=None, interval=1,q=q):
        if name is None:
            name = id(self)
        # Set up the task object
        self.quit_flag = quit_flag
        self.name = name
        self.interval = interval
        self.q=q
        logging.debug("Task %s created"%self.name)

    def run(self):
        try:
            logging.debug("Task %s started"%self.name)
            while not self.quit_flag:
                # logging.debug("Task %s is doing something"%self.name)
                print("Consumer waiting ")
                print("Consumer consumed the item:", q.get())
                time.sleep(3)
        finally:
            logging.debug("Task %s performing cleanup..."%self.name)
            # Perform cleanup here
            logging.debug("Task %s stopped."%self.name)


class Flag(threading.Event):
    """A wrapper for the typical event class to allow for overriding the
    `__bool__` magic method, since it looks nicer.
    """
    def __bool__(self):
        return self.is_set()

if __name__ == "__main__":
    try:
        # Create the event flag for when we wish to terminate.
        flag = Flag()
        # Create some tasks
        # tasks = [Task(flag, name="thread-%d"%i, interval=1 , q = q) for i in range(5)]
        tasks = [ConsumerTask(flag, name="thread-consumer", interval=1 , q = q), ProducerTask(flag, name="thread-producer", interval=1 , q = q)]
        # Create some threads
        threads = [threading.Thread(target=t.run, name="thread-%s"%t.name) for t in tasks]
        # Start the threads
        for t in threads: t.start()
        # Spin in place while threads do their work
        while True:
            # logging.debug("Main thread is doing something")
            time.sleep(1)

    except KeyboardInterrupt:
        logging.debug("Interrupt received, setting quit flag.")
        flag.set()
    finally:
        # Ensure that the flag is set regardless since program is terminating
        logging.debug("Starting termination, setting quit flag.")
        flag.set()

        # Join the threads
        logging.debug("Attempting to join threads...")
        while threads:
            for t in threads:
                t.join(0.1)
                if t.is_alive():
                    logging.debug("Thread %s not ready to join"%t.name)
                else:
                    logging.debug("Thread %s successfully joined"%t.name)
                    threads.remove(t)
        logging.debug("Program terminated.")
