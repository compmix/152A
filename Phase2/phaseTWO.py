import math
import random
from collections import deque
from queue import PriorityQueue
import matplotlib.pyplot as plt


class Glb():
    time= 0
    gel = PriorityQueue()
    SIFS = 0.05
    DIFS = 0.10
    T = 1.0
    ACKtimeout = 5.0
    idle = True
    hostList = []
    totalDelays = 0
    totalBytes = 0
 
def resetGlb():
    Glb.time= 0
    Glb.idle = True
    Glb.hostList = []
    Glb.gel = PriorityQueue()
    Glb.totalBytes = 0
    Glb.totalDelays = 0

def NED_time(rate):
    u = random.uniform(0,1)
    return ((-1/rate)* math.log(1-u))

def frameLength():
    frame = NED_time(0.001)
    while (frame > 1544):
        frame = NED_time(0.001)
    return frame

def GEL_put(event):
    # insert into gel
    Glb.gel.put((event.time, event))

def GEL_pop():
    # pop gel top event
    return Glb.gel.get()[1]

def GEL_top():
    # get top gel without popping
    top = GEL_pop()
    GEL_put(top)
    return top


class Event:
    def __init__(self, time, eventType, source, destination, ACK = False):
        self.time = time
        # 3 types: arrival, transmission, departure
        self.eventType = eventType
        # ID of the host
        self.source = source
        self.destination = destination
        self.ACK = ACK

class Frame:
    def __init__(self, size, source, destination, ACK = False):
        # Frame's size, source, destination.
        self.size = size
        self.source = source
        self.destination = destination
        self.entry_time = Glb.time
        self.ACK = ACK

class Host:
    def __init__(self, ID, N, arrivalRate):
        self.ID = ID
        self.N = N
        # Buffer length 
        self.length = 0
        # Buffer of frames to transmit
        self.buffer = deque()
        self.arrivalRate = arrivalRate

        # Timer for backoffs, ACK timeouts
        self.backoff = 0 
        # count of collisions
        self.collisions = 0 

        # Set Event to not ACK, wait for ACK
        self.waitACK = False

        # Statistic variables
        self.successBytes = 0
        self.delays = 0

        # Generate first arrival event for this Host
        firstEvent = Event(Glb.time+ NED_time(self.arrivalRate), "ARRIVAL", self.ID, self.neighbors())
        Glb.gel.put((firstEvent.time, firstEvent))

    def neighbors(self):
        rand = random.randint(0, self.N - 1)
        while self.ID == rand:
            rand = random.randint(0, self.N - 1)
        return rand

    def processArrEvent(self, event):
        # Create new arrival event
        nextArrivalEvent = Event(Glb.time+ NED_time(self.arrivalRate), "ARRIVAL", self.ID, self.neighbors())
        Glb.gel.put((nextArrivalEvent.time, nextArrivalEvent))

        # Create Frame/Packet for new arrival
        frameLen = frameLength()
        self.buffer.append(Frame(frameLen, event.source, event.destination))

        # If buffer is empty, enqueue transmission event into GEL
        if (len(self.buffer) - 1) == 0:
            if Glb.idle:
                transEvent = Event(Glb.time+ Glb.DIFS, "TRANSMISSION", self.ID, event.destination)
                Glb.gel.put((transEvent.time, transEvent))
            else:
                self.generateBackoff()

    def generateTransEvent(self):
        # If there is no more packet, return. Otherwise check if channel is free.
        if len(self.buffer) == 0:
            return

        if Glb.idle:
            frame = self.buffer[0]
            # If the receiving host receives the frame correctly, enter SIFS, otherwise back to to step 2.
            if frame.ACK:
                GEL_put(Event(Glb.time+ Glb.SIFS, "TRANSMISSION", frame.source, frame.destination, True))
            else:
                GEL_put(Event(Glb.time+ Glb.DIFS, "TRANSMISSION", frame.source, frame.destination, False))
        else:
            self.generateBackoff()

    def processTransEvent(self, event):
        # if channel is free, set to busy, pop the top of Frame and reset collision count
        if Glb.idle:
            self.collisions = 0
            frame = self.buffer[0]
            transmission_time = (frame.size * 8) / (11 * 10 ** 6)
            departure_event = Event(Glb.time+ transmission_time, "DEPARTURE", self.ID, event.destination, event.ACK)
            GEL_put(departure_event)
            Glb.idle = False

            # Update statistics
            self.successBytes += frame.size
            self.delays += Glb.time- frame.entry_time

            # Event was not an ACK so set to wait for ACK.
            # Else, generate next transmission event based on next Frame
            if not frame.ACK:
                self.waitACK = True
            else:
                self.buffer.popleft()
                self.generateTransEvent()

        else:
            self.generateBackoff()

    def processDepEvent(self, event):
        # Frame has arrived at destinationination; channel is now free
        Glb.idle = True

        #  If waiting for an ACK
        if event.ACK and self.waitACK:
            self.buffer.popleft()
            self.waitACK = False
            self.ACK_counter = 0
            self.generateTransEvent()
        elif not event.ACK:
            ACK_frame = Frame(64, self.ID, event.source, True)
            self.buffer.append(ACK_frame)

            if not self.waitACK:
                # If channel is idle transmit a frame after a short DIFS
                if Glb.idle:
                    # Create transmission event
                    GEL_put(Event(Glb.time+ Glb.DIFS, "TRANSMISSION", self.ID, event.source, True))
                # else generate a back off
                else:
                    self.generateBackoff()

    def generateBackoff(self):
        time = Glb.T
        if self.waitACK:
            time = Glb.ACKtimeout

        self.collisions += 1
        u = random.uniform(0,1)
        self.backoff = u * time * self.collisions

        if not self.ID in Glb.hostList:
            Glb.hostList.append(self.ID)

    def timeOut(self):
        if self.waitACK:
            #   3 (max number of retransmissions allowed)
            if self.collisions <= 3:
                repeat_frame = GEL_top()
                event = Event(Glb.time, "TRANSMISSION", self.ID, repeat_frame.destination)
                self.processTransEvent(event)
            # give up and pop, get to generate_transmission event
            # if there are more packet/frame , create a transmission event, otherwise return
            else:
                self.buffer.popleft()
                self.generateTransEvent()
        else:
            self.processTransEvent()

        Glb.hostList.remove(self.ID)


def simulation(N, arrivalRate):
    # Reset globals
    resetGlb()

    # Initialize Hosts
    hosts = [Host(i, N, arrivalRate) for i in range(N)]

    for i in range(100000):
        # Get top event in the GEL
        event = GEL_pop()

        while len(Glb.hostList) > 0 and Glb.idle and Glb.time< event.time:
            for host_id in Glb.hostList:
                hosts[host_id].backoff -= 0.01
                if hosts[host_id].backoff <= 0:
                    hosts[host_id].timeOut()
            # Your CSMA/CA implementation can sense the channel every 0.01 msec.
            Glb.time+= 0.01

        Glb.time= event.time

        # Arrival event - a Host has a new Frame to transmit
        if event.eventType == "ARRIVAL":
            hosts[event.source].processArrEvent(event)

        elif event.eventType == "TRANSMISSION":
            hosts[event.source].processTransEvent(event)

        else:
            hosts[event.destination].processDepEvent(event)

    for host in hosts:
        Glb.totalDelays += host.delays
        Glb.totalBytes += host.successBytes
    throughput = 1000 * Glb.totalBytes / Glb.time 
    avgDelay = 1000 * Glb.totalDelays / Glb.time
    return throughput, avgDelay


def main():
    throughput = 0
    avgDelay = 0
    print("*---------------------------------------------------------*")
    print("|                         N = 10                          |")
    print("*---------------------------------------------------------*")
    print("{0:<15} {1:<15} {2:<15}".format(
        "Lambda", "Throughput", "Avg Delay"))
    for lam in [0.01, 0.05, 0.1, 0.3, 0.6, 0.8, 0.9]:
        throughput, avgDelay = simulation(10, lam)
        print("{lamb:<15} {throughput:<15.3f} {avgDelay:<15.3f}" .format(
            lamb = lam, throughput = throughput, avgDelay = avgDelay))
    throughput = 0
    avgDelay = 0
    print("*--------------------------------------------------------*")
    print("|                         N = 20                         |")
    print("*--------------------------------------------------------*")
    print("{0:<15} {1:<15} {2:<15}".format(
        "Lambda", "Throughput", "Avg Delay"))
    for lam in [0.01, 0.05, 0.1, 0.3, 0.6, 0.8, 0.9]:
        throughput, avgDelay = simulation(20, lam)
        print("{lamb:<15} {throughput:<15.3f} {avgDelay:<15.3f}" .format(
            lamb = lam, throughput = throughput, avgDelay = avgDelay))

main()