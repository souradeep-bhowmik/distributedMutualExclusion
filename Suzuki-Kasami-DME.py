# In[1]:

import sys
import random
import threading
from time import sleep
from mpi4py import MPI
from threading import Thread
from datetime import datetime
from collections import deque

# Initialize
comm = MPI.COMM_WORLD
threadId = comm.Get_rank()
numberofProcess = comm.Get_size()

# queue in token, first in first out!
tokenQueue = deque()
# Has no token : 0. Otherwise: 1
hasToken = 0
# Not in critical section: 0. Otherwise: 1
inCriticalSection = 0
# Not request for token: 0. Otherwise: 1
reqForToken = 0

# Synchronization lock for each step
criticalSectionLock = threading.Lock()
sendTokenLock = threading.Lock()
rnLock = threading.Lock()
releaseLock = threading.Lock()
# Only one process can request for token at one time
requestLock = threading.Lock()
# Only one process can have token at one time
tokenLock = threading.Lock()

# Create LN and RN
LN = [0]*numberofProcess
RN = [0]*numberofProcess

# Assume Process 0 has token initially
if threadId == 0:
    print("%s: %d has a token initially." %
          (datetime.now().strftime('%H:%M:%S'), threadId))
    hasToken = 1

# One process wants to request for token


def request():
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

# One process sends request to others


def startSend(value):
    for i in range(numberofProcess):
        if threadId != i:
            print("%s: %d sends request to %d!!!" %
                  (datetime.now().strftime('%H:%M:%S'), threadId, i))
            sys.stdout.flush()
            valueSent = ['CS', threadId, value]
            comm.send(valueSent, dest=i)
            sleep(2)

# One process sends token to another


def sendToken(receiver):
    global tokenQueue
    global inCriticalSection
    with sendTokenLock:
        print("%s: %d sends token to %d." %
              (datetime.now().strftime('%H:%M:%S'), threadId, receiver))
        sys.stdout.flush()
        token = ['Token', LN, tokenQueue]
        comm.send(token, dest=receiver)

# One process receives something


def receive():
    global LN
    global reqForToken
    global hasToken
    global RN
    global tokenQueue
    global inCriticalSection
    while True:
        message = comm.recv(source=MPI.ANY_SOURCE)
        # receive a request
        if message[0] == 'CS':
            with rnLock:
                RN[message[1]] = max([message[2], RN[message[1]]])
                # if sequence number that i send is less than RN[i] (receiver), out of date
                if message[2] < RN[message[1]]:
                    print("%s: Request from %d is out of date." %
                          (datetime.now().strftime('%H:%M:%S'), message[1]))
                    sys.stdout.flush()
                # if j has token, no process is in cs, and RN[i] = LN[i]+1, send token
                if (hasToken == 1) and inCriticalSection == 0 and (RN[message[1]] == (LN[message[1]] + 1)):
                    hasToken = 0
                    sendToken(message[1])
        # receive a token
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

# One process enters CS


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
            release()

# One process releases CS


def release():
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


# Starts program!
try:
    threadSource = Thread(target=receive)
    threadSource.start()
except:
    print("Error during thread creation!")

while True:
    if hasToken == 0:
        sleep(random.uniform(1, 3.5))
        request()
    elif inCriticalSection == 0:
        enterCriticalSection()
    while reqForToken:
        sleep(random.uniform(1, 3))
