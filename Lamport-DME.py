
# coding: utf-8

# In[ ]:


import random
from mpi4py import MPI
import sys
from datetime import datetime
import threading
from time import sleep
from collections import deque
from threading import Thread

comm = MPI.COMM_WORLD
thread_id = comm.Get_rank()
number_of_process = comm.Get_size()

queue_in_process = deque()
in_cs = 0
release_lock = threading.Lock()
request_lock = threading.Lock()
cs_lock = threading.Lock()
vector_clock=0
counter = 0

def request():
    global vector_clock
    with request_lock:
        vector_clock+=1
        for i in range(number_of_process):
            if thread_id!=i:
                print("%s: %d sends request to %d!!!" % (datetime.now().strftime('%H:%M:%S'), thread_id, i))
                sys.stdout.flush()
                value_sent = ['CS',vector_clock,thread_id]
                comm.send(value_sent, dest=i)
                sleep(2)
            
def reply(id):
    global vector_clock
    print("%s: %d sends reply to %d!!!" % (datetime.now().strftime('%H:%M:%S'), thread_id, id[1]))
    sys.stdout.flush()
    value_sent = ['reply',vector_clock,thread_id]
    comm.send(value_sent, dest=id[1])
    sleep(3)
    queue_in_process.append(id)

def release():
    global vector_clock
    counter=0
    with release_lock:
        for i in range(number_of_process):
            if thread_id!=i:
                print("%s: %d sends release to %d!!!" % (datetime.now().strftime('%H:%M:%S'), thread_id, i))
                sys.stdout.flush()
                value_sent = ['release',vector_clock,thread_id]
                comm.send(value_sent, dest=i)
                sleep(2)

def receive():
    global queue_in_process
    global counter
    while True:
        message = comm.recv(source=MPI.ANY_SOURCE)
        if message[0] == 'release':
            queue_in_process.popleft()
        elif message[0] == 'CS':
            reply([message[1],message[2]])
            queue_in_process.append([message[1],message[2]])
        elif message[0] == 'reply':
            counter+=1
            if counter == number_of_process-1:
                enter_cs()

def enter_cs():
    global in_cs
    with cs_lock:
        in_cs = 1
        print("%s: %d enters CS." % (datetime.now().strftime('%H:%M:%S'), thread_id))
        sys.stdout.flush()
        sleep(random.uniform(3,7))
        print("%s: %d finishes CS." % (datetime.now().strftime('%H:%M:%S'), thread_id))
        sys.stdout.flush()
        in_cs = 0
        release()
    counter = 0

try:
    some_process = Thread(target=receive)
    some_process.start()
except:
    print("can't start thread!!!!")

while True:
    request()
    sleep(random.uniform(1,2))
    if in_cs==0:
        receive()
