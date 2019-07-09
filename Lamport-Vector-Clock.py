#!/usr/bin/env python
# coding: utf-8

# In[1]:

from os import getpid
from multiprocessing import Pipe, Process

# Lamport Vector Clock
def lamport_time(vector_clock):
    return '(lamport_vector_clock={})'.format(vector_clock)

# Received timestamp (Vector Clock)
def received_timestamp(time_stamp, vector_clock):
    for i in range(len(vector_clock)):
        vector_clock[i] = max(vector_clock[i], time_stamp[i])
    return vector_clock

# Sending message
def sending(pipe, id, vector_clock):
    vector_clock[id-1] += 1
    pipe.send(('Go Cyclone!!!', vector_clock))
    print(str(id) + ' has sent message: '+ lamport_time(vector_clock))
    return vector_clock

# Local event
def local_event(id,vector_clock):
    vector_clock[id-1] += 1
    print('A local event occurs in {}: '.format(id) + lamport_time(vector_clock))
    return vector_clock

# Receiving message
def received(pipe, id, vector_clock):
    vector_clock[id-1] += 1
    message, timestamp = pipe.recv()
    vector_clock = received_timestamp(timestamp, vector_clock)
    print(str(id)  + ' has received message: ' + lamport_time(vector_clock))
    return vector_clock

# Process 1
def one(pipe_one_to_two,pipe_one_to_four):
    id = 1
    vector_clock = [0,0,0,0]
    vector_clock = local_event(id, vector_clock)
    vector_clock = sending(pipe_one_to_two, id, vector_clock)
    vector_clock = sending(pipe_one_to_four, id, vector_clock)
    vector_clock = received(pipe_one_to_four, id, vector_clock)
    vector_clock = received(pipe_one_to_two, id, vector_clock)

# Process 2
def two(pipe_three_to_two):
    id = 2
    vector_clock = [0,0,0,0]
    vector_clock = received(pipe_three_to_two, id, vector_clock)
    vector_clock = sending(pipe_three_to_two, id, vector_clock)

# Process 3
def three(pipe_two_to_one):
    id = 3
    vector_clock = [0,0,0,0]
    vector_clock = received(pipe_two_to_one, id, vector_clock)
    vector_clock = sending(pipe_two_to_one, id, vector_clock)

# Process 4
def four(pipe_four_to_one,pipe_two_to_three):
    id = 4
    vector_clock = [0,0,0,0]
    vector_clock = received(pipe_four_to_one, id, vector_clock)
    vector_clock = sending(pipe_two_to_three, id, vector_clock)
    vector_clock = local_event(id,vector_clock)
    vector_clock = sending(pipe_four_to_one, id, vector_clock)
    vector_clock = received(pipe_two_to_three, id, vector_clock)
    
one_to_two, two_to_one = Pipe()
two_to_three, three_to_two = Pipe()
four_to_one, one_to_four = Pipe()

p_one = Process(target=one, args=(one_to_two,one_to_four))
p_two = Process(target=two, args=(three_to_two,))
p_three = Process(target=three, args=(two_to_one,))
p_four = Process(target=four, args=(four_to_one,two_to_three))

p_one.start()
p_two.start()
p_three.start()
p_four.start()

p_one.join()
p_two.join()
p_three.join()
p_four.join()

