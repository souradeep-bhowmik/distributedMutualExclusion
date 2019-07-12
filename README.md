# distributedMutualExclusion
Date of Project: November 2018

This project was undertaken as part of my term project for Advanced Operating Systems course for my Masters degree. I have done implementations of two DME algorithms and Vector clock.

DME: Distributed Mutual Exclusion is a property of concurrency control in a distributed system. The goals of DME is to:
* Provide a mutually exclusive (safe) communication for critical section access
* Enable every system in a network to commit to critical section (finite waiting)
* Prevent deadlock
* Fault tolerance
* Minimize synchronization delay
* Reduce message traffic

Wiki source and more information: https://en.wikipedia.org/wiki/Mutual_exclusion

The program is coded using Python (version: 3.x.x) and Message Passing Interface standard for Python, or mpi4py. The programs for DME algorithms simulate a distributed environment by forking threads in a single system and communicating using MPI.

# Instructions for environment setup:
* Install __Python 3.x.x__ using [Python downloads page](https://www.python.org/downloads/) and selecting your operating system and latest stable release
* For Windows, install __MSMPI__ using [this link](https://docs.microsoft.com/en-us/message-passing-interface/microsoft-mpi/) (remember to always check for latest release, __v10.0__ is the latest at the time of writing the code).
For MAC, install __Homebrew__ which is kind of a package installer using [Homwbrew site](https://brew.sh/). Then, install mpich using `brew install mpich`
* Install the __mpi4py__ package in Python using `[sudo] pip install mpi4py`

# Execution instructions:
To execute Vector Clock script, type `python {filename}.py`.
To execute the DME algorithm scripts, type `mpiexec -n X python -m {filename}.py` where "X" represents the number of processes you want.

NOTE: The implementation is not perfect and there is room for improvement. Any feedback for betterment of code is always welcome.
