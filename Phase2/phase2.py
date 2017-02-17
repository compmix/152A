import random
import math
import matplotlib.pyplot as plt

# Negative Exponential Distributed Time:
def NED_time(rate):
    u = random.random()
    return ((-1/rate)* math.log(1-u))

# random backoff
def backOff(T):
    u = random.uniform(0, 1)
    return round(T*u)

# generate NED variable for data frame length(packet size)
def frameLength():
    u = NED_time(1)*1544
    while (u > 1544):
        #u = random.randint(0,1544)
        u = NED_time(1)*1544
    return u

# Data structures
class Event():
    def __init__(self, eventTime, eventType, serviceTime, backoffCount):
        self.eventTime = eventTime
        self.eventType = eventType
        self.serviceTime = serviceTime
        #self.source = source
        #self.destination = destination
        self.backoffCount = backoffCount

class Host():
    def __init__(self, ID):
        self.ID = ID
        self.gel = []

def simulation(N, arrivalRate, T):
    totalBytes = 0
    totalTime = 0
    totalFrames = 0
    time = 0
    curTime = 0
    busyTime = 0
    DIFS = 0.1
    SIFS = 0.05
    FRAMESIZE = 64

    hostList = []
    for n in range(N):
        hostList.append(Host(n))

    for host in hostList:
        firstArrivalEvent = Event(time + NED_time(arrivalRate), "ARRIVAL", frameLength(), 0)
        host.gel.append(firstArrivalEvent)
    
    for i in range(0,100000):
        hostList.sort(key=lambda x: x.gel[0].eventTime)
        idle = curTime >= busyTime
        curEvent = hostList[0].gel.pop(0)
        frameLen = curEvent.serviceTime
        backoffCount =curEvent.backoffCount
        curTime = curEvent.eventTime

        if curEvent.eventType == "ARRIVAL":
            if idle:
                newEvent = Event(curTime + DIFS, "DEPARTURE", frameLen, backoffCount)
            else:
                newEvent = Event(curTime + backOff(T), "ARRIVAL", frameLen, backoffCount+1)
            hostList[0].gel.append(newEvent)

        elif curEvent.eventType == "DEPARTURE":
            if idle:
                totalBytes = frameLen + totalBytes + 64
                totalFrames = totalFrames + 1
                busyTime = curTime + (frameLen*8)/(11* 10**6) + SIFS + (FRAMESIZE*8)/(11* 10**6)
                newEvent = Event(curTime + NED_time(arrivalRate), "ARRIVAL", frameLength(), backoffCount)
            else:
                newEvent = Event(curTime + backOff(T), "ARRIVAL", frameLen, backoffCount+1)
            hostList[0].gel.append(newEvent)
    totalTime = curTime
    throughput = (totalBytes/totalTime)
    if throughput == 0:
        avgDelay = 0
    else:
        avgDelay = busyTime/throughput
    return throughput, avgDelay

def main():
    print("*----------------------------------------------------------------------*")
    print("|                                N = 10                                |")
    print("*----------------------------------------------------------------------*")
    print("{0:<15} {1:<15} {2:<15} {3:<15}".format(
        "Lambda", "Throughput", "Avg Delay", "T value"))
    for lam in [0.01, 0.05, 0.1, 0.3, 0.6, 0.8, 0.9]:
        throughput, avgDelay = simulation(10, lam, backOff(10))
        print("{lamb:<15} {throughput:<15.3f} {avgDelay:<15.3f} {T:<15.3f}" .format(
            lamb = lam, throughput = throughput, avgDelay = avgDelay, T = backOff(10)))

    print("*----------------------------------------------------------------------*")
    print("|                                N = 20                                |")
    print("*----------------------------------------------------------------------*")
    print("{0:<15} {1:<15} {2:<15} {3:<15}".format(
        "Lambda", "Throughput", "Avg Delay", "T value"))
    for lam in [0.01, 0.05, 0.1, 0.3, 0.6, 0.8, 0.9]:
        throughput, avgDelay = simulation(20, lam, backOff(10))
        print("{lamb:<15} {throughput:<15.3f} {avgDelay:<15.3f} {T:<15.3f}" .format(
            lamb = lam, throughput = throughput, avgDelay = avgDelay, T = backOff(10)))

main()