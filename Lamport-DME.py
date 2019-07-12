"""
Author      :       Souradeep Bhowmik
Date        :       November 2018
Environment :       Windows 10
Version     :       Python 3.6.2
"""


import sys
import random
import threading
from time import sleep
from mpi4py import MPI
from threading import Thread
from datetime import datetime
from collections import deque

# Initialize MPI
comm = MPI.COMM_WORLD
threadId = comm.Get_rank()
numberOfProcesses = comm.Get_size()

# Process queue, first in first out
processQueue = deque()

# Inside critical section: 1, otherwise: 1
inCriticalSection = 0

# Locks for mutual exclusion
releaseLock = threading.Lock()
requestLock = threading.Lock()
criticalSectionLock = threading.Lock()

# Vector clock
vectorClock=0
counter = 0

# Method for broadcasting a critical section request
def requestCriticalSection():
    global vectorClock
    with requestLock:
        vectorClock+=1
        for i in range(numberOfProcesses):
            if threadId!=i:
                print("%s: %d sends request to %d!!!" % (datetime.now().strftime('%H:%M:%S'), threadId, i))
                sys.stdout.flush()
                value_sent = ['CS',vectorClock,threadId]
                comm.send(value_sent, dest=i)
                sleep(2)

# Method for replying to a received message
def sendReply(id):
    global vectorClock
    print("%s: %d sends reply to %d!!!" % (datetime.now().strftime('%H:%M:%S'), threadId, id[1]))
    sys.stdout.flush()
    value_sent = ['reply',vectorClock,threadId]
    comm.send(value_sent, dest=id[1])
    sleep(3)
    processQueue.append(id)

# Method for processing critical section exit
def exitCriticalSection():
    global vectorClock
    with releaseLock:
        for i in range(numberOfProcesses):
            if threadId!=i:
                print("%s: %d sends release to %d!!!" % (datetime.now().strftime('%H:%M:%S'), threadId, i))
                sys.stdout.flush()
                value_sent = ['release',vectorClock,threadId]
                comm.send(value_sent, dest=i)
                sleep(2)

# Method to handle received requests
def receiveMessage():
    global processQueue
    global counter
    while True:
        message = comm.recv(source=MPI.ANY_SOURCE)
        if message[0] == 'release':
            processQueue.popleft()
        elif message[0] == 'CS':
            sendReply([message[1],message[2]])
            processQueue.append([message[1],message[2]])
        elif message[0] == 'reply':
            counter+=1
            if counter == numberOfProcesses-1:
                enterCriticalSection()

# Method to process critical section entry
def enterCriticalSection():
    global inCriticalSection
    with criticalSectionLock:
        inCriticalSection = 1
        print("%s: %d enters CS." % (datetime.now().strftime('%H:%M:%S'), threadId))
        sys.stdout.flush()
        sleep(random.uniform(3,7))
        print("%s: %d finishes CS." % (datetime.now().strftime('%H:%M:%S'), threadId))
        sys.stdout.flush()
        inCriticalSection = 0
        exitCriticalSection()

# Main program module that starts the communication in an infinite loop (the communication must be terminated manually!)
try:
    some_process = Thread(target=receiveMessage)
    some_process.start()
except:
    print("can't start thread!!!!")

while True:
    requestCriticalSection()
    sleep(random.uniform(1,2))
    if inCriticalSection==0:
        receiveMessage()
