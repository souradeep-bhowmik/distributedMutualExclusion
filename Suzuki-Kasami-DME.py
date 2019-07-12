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
numberofProcess = comm.Get_size()

# Token queue, first in first out!
tokenQueue = deque()

# Doesn't have token: 0, otherwise: 1
hasToken = 0

# Not in critical section: 0, otherwise: 1
inCriticalSection = 0

# Did not request for token: 0, otherwise: 1
reqForToken = 0

# Synchronization lock for each step
criticalSectionLock = threading.Lock()
sendTokenLock = threading.Lock()
rnLock = threading.Lock()
releaseLock = threading.Lock()
# Only one process can request for the token at one time
requestLock = threading.Lock()
# Only one process can have the token at one time
tokenLock = threading.Lock()

# List for keeping information about most recent sequence execution by a site in the token
LN = [0]*numberofProcess
# List for keeping the largest sequence number of request from a site
RN = [0]*numberofProcess

# Assume Process 0 has token initially
if threadId == 0:
    print("%s: %d has a token initially." %
          (datetime.now().strftime('%H:%M:%S'), threadId))
    hasToken = 1

# Method for ensuring mutual exclusion during token request
def requestToken():
    global hasToken
    global RN
    global inCriticalSection
    global reqForToken
    with requestLock:
        if hasToken == 0:
            RN[threadId] += 1
            currentValue = RN[threadId]
            print("%s: %d wants to request for a token to enter CS." %
                  (datetime.now().strftime('%H:%M:%S'), threadId))
            sys.stdout.flush()
            reqForToken = 1
            startSend(currentValue)

# Method for sending requests to other sites
def startSend(value):
    for i in range(numberofProcess):
        if threadId != i:
            print("%s: %d sends request to %d!!!" %
                  (datetime.now().strftime('%H:%M:%S'), threadId, i))
            sys.stdout.flush()
            valueSent = ['CS', threadId, value]
            comm.send(valueSent, dest=i)
            sleep(2)

# Method for sending token to another site
def sendToken(receiver):
    global tokenQueue
    global inCriticalSection
    with sendTokenLock:
        print("%s: %d sends token to %d." %
              (datetime.now().strftime('%H:%M:%S'), threadId, receiver))
        sys.stdout.flush()
        token = ['Token', LN, tokenQueue]
        comm.send(token, dest=receiver)

# Method that does processing related to receiving a message form a site
def receive():
    global LN
    global reqForToken
    global hasToken
    global RN
    global tokenQueue
    global inCriticalSection
    while True:
        message = comm.recv(source=MPI.ANY_SOURCE)

        # Receives a request
        if message[0] == 'CS':
            with rnLock:
                RN[message[1]] = max([message[2], RN[message[1]]])
                # Check for out of date requests
                if message[2] < RN[message[1]]:
                    print("%s: Request from %d is out of date." %
                          (datetime.now().strftime('%H:%M:%S'), message[1]))
                    sys.stdout.flush()
                # If process j has token, no other process is in cs and RN[i] = LN[i]+1 then send token
                if (hasToken == 1) and inCriticalSection == 0 and (RN[message[1]] == (LN[message[1]] + 1)):
                    hasToken = 0
                    sendToken(message[1])
                    
        # Receives a token
        elif message[0] == 'Token':
            with tokenLock:
                print("%s: %d receives a token." %
                      (datetime.now().strftime('%H:%M:%S'), threadId))
                sys.stdout.flush()
                hasToken = 1
                reqForToken = 0
                LN = message[1]
                tokenQueue = message[2]
                enterCriticalSection()

# Method that is used to enter critical section
def enterCriticalSection():
    global inCriticalSection
    global hasToken
    with criticalSectionLock:
        if hasToken == 1:
            inCriticalSection = 1
            print("%s: %d enters CS." %
                  (datetime.now().strftime('%H:%M:%S'), threadId))
            sys.stdout.flush()
            sleep(random.uniform(3, 7))
            print("%s: %d finishes CS." %
                  (datetime.now().strftime('%H:%M:%S'), threadId))
            sys.stdout.flush()
            inCriticalSection = 0
            exitCriticalSection()

# Method that is used to exit critical section
def exitCriticalSection():
    global inCriticalSection
    global LN
    global RN
    global tokenQueue
    global hasToken
    with releaseLock:
        LN[threadId] = RN[threadId]
        for i in range(numberofProcess):
            if i not in tokenQueue:
                if RN[i] == (LN[i] + 1):
                    tokenQueue.append(i)
                    print("%s: %d has added %d to the queue. Now queue of token is: %s." % (
                        datetime.now().strftime('%H:%M:%S'), threadId, i, str(tokenQueue)))
                    sys.stdout.flush()

        if tokenQueue:
            hasToken = 0
            sendToken(tokenQueue.popleft())


# Main program module that starts the communication in an infinite loop (the communication must be terminated manually!)
try:
    threadSource = Thread(target=receive)
    threadSource.start()
except:
    print("Error during thread creation!")

while True:
    if hasToken == 0:
        sleep(random.uniform(1, 3.5))
        requestToken()
    elif inCriticalSection == 0:
        enterCriticalSection()
    while reqForToken:
        sleep(random.uniform(1, 3))
