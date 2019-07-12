from multiprocessing import Pipe, Process

# Vector Clock
def lamportTime(vectorClock):
    return '(lamport_vector_clock={})'.format(vectorClock)

# Method for timestamp update of local vector clock for processes
def receivedTimestamp(timeStamp, vectorClock):
    for i in range(len(vectorClock)):
        vectorClock[i] = max(vectorClock[i], timeStamp[i])
    return vectorClock

# Sending message
def sendMessage(pipe, id, vectorClock):
    vectorClock[id-1] += 1
    pipe.send(('Go Cyclone!!!', vectorClock))
    print(str(id) + ' has sent message: '+ lamportTime(vectorClock))
    return vectorClock

# Local event
def localEvent(id,vectorClock):
    vectorClock[id-1] += 1
    print('A local event occurs in {}: '.format(id) + lamportTime(vectorClock))
    return vectorClock

# Receiving message
def receiveMessage(pipe, id, vectorClock):
    vectorClock[id-1] += 1
    message, timeStamp = pipe.recv()
    vectorClock = receivedTimestamp(timeStamp, vectorClock)
    print(str(id)  + ' has received message: ' + lamportTime(vectorClock))
    return vectorClock

# 1st Process
def one(pipeOneToTwo,pipeOneToFour):
    id = 1
    vectorClock = [0,0,0,0]
    vectorClock = localEvent(id, vectorClock)
    vectorClock = sendMessage(pipeOneToTwo, id, vectorClock)
    vectorClock = sendMessage(pipeOneToFour, id, vectorClock)
    vectorClock = receiveMessage(pipeOneToFour, id, vectorClock)
    vectorClock = receiveMessage(pipeOneToTwo, id, vectorClock)

# 2nd Process
def two(pipeThreeToTwo):
    id = 2
    vectorClock = [0,0,0,0]
    vectorClock = receiveMessage(pipeThreeToTwo, id, vectorClock)
    vectorClock = sendMessage(pipeThreeToTwo, id, vectorClock)

# 3rd Process
def three(pipeTwoToOne):
    id = 3
    vectorClock = [0,0,0,0]
    vectorClock = receiveMessage(pipeTwoToOne, id, vectorClock)
    vectorClock = sendMessage(pipeTwoToOne, id, vectorClock)

# 4th Process
def four(pipeFourToOne,pipeTwoToThree):
    id = 4
    vectorClock = [0,0,0,0]
    vectorClock = receiveMessage(pipeFourToOne, id, vectorClock)
    vectorClock = sendMessage(pipeTwoToThree, id, vectorClock)
    vectorClock = localEvent(id,vectorClock)
    vectorClock = sendMessage(pipeFourToOne, id, vectorClock)
    vectorClock = receiveMessage(pipeTwoToThree, id, vectorClock)

# Main module for process creation and synchronization
if __name__ == '__main__':
    oneToTwo, twoToOne = Pipe()
    twoToThree, threeToTwo = Pipe()
    fourToOne, oneToFour = Pipe()

    processOne = Process(target=one, args=(oneToTwo,oneToFour))
    processTwo = Process(target=two, args=(threeToTwo,))
    processThree = Process(target=three, args=(twoToOne,))
    processFour = Process(target=four, args=(fourToOne,twoToThree))

    processOne.start()
    processTwo.start()
    processThree.start()
    processFour.start()

    processOne.join()
    processTwo.join()
    processThree.join()
    processFour.join()
