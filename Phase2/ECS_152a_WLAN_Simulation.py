import random
import math
import matplotlib.pyplot as plt


DIFS = 0.1
SIFS = 0.05



# Negative Exponential Distributed Time:
def NED_time(rate):
    u = random.random()
    return ((-1/rate)* math.log(1-u))

# random backoff
def backOff(T):
    u = random.uniform(0, 1)
    return round(T*u)

# generate NED variable for data frame length
def frameLength():
    u = random.randint(0,1544)
    while (u > 1544):
        u = random.randint(0,1544)
    return u

# Data structures
class Event():
    def __init__(self, eventTime, eventType, serviceTime, source, destination):
        self.eventTime = eventTime
        self.eventType = eventType
        self.serviceTime = serviceTime
        self.source = source
        self.destination = destination

class Packet():
    def __init__(self, packetType):
        self.type = packetType
        self.size = random.expovariate()


class Host():
    def __init__(self, ID, neighbors):
        self.ID = ID
        self.fifo = []
        self.neighbors = neighbors
        self.length = 0

        
    def newEvent(self,arrival_rate, service_rate):
        self.first_arrival_event_time = Event(time + NED_time(arrival_rate), "ARRIVAL", NED_time(service_rate))


def simulation(N, arrivalRate, serviceRate):
    # create N hosts
    hostList = []
    for n in range(N):
        hostList.append(Host(n, N-1) )

    # initialize first packet
    time = 0
    gel = []
    firstArrivalEvent = Event(time + NED_time(arrivalRate), "ARRIVAL", NED_time(serviceRate), 0, random.randint(1, N))
    gel.append(firstArrivalEvent)

    # 100000 time steps
    for i in range(0,100000):
        print("time step: ", i)

        if gel[0].eventTime > i+1:
            continue

        # process each host
        for host in hostList:
            print(host.ID)

            print(gel[0].eventTime)
            

            curEvent = gel.pop()

            if curEvent.eventType == "ARRIVAL":
                # (1) find the time of the next arrival, which is current time
                time = curEvent.eventTime
                # Find next arrival time, which is current time plus a randomly generated time drawn from a NED random variable with rate lambda
                next_arrival_time = time + NED_time(arrivalRate)
                # (2) Create a new packet and determine its service time which is randomly generated time drawn from a NED random variable with rate mu
                serviceTime = NED_time(serviceRate)
                # (3) Create a new arrival Event(next arrival time, type = arrival, service time)
                new_arrivalEvent = Event(next_arrival_time, "ARRIVAL" , serviceTime)
                # (4) Insert the event into the event list - GEL
                host.gel.append(new_arrivalEvent)
                # GEL is sorted in time.
                host.gel.sort(key=lambda x: x.eventTime)

                # Process the arrival event:
                # (a) If the server is free
                if host.length == 0:
                    # (a1) Get the service time of the packet
                    host.length += 1
                    # (a2) Create a depature event at time which is equal to the current time plus the service time of the packet
                    # Again it is randomly generated from NED random variable
                    departure_time = time + serviceTime
                    host.fifo.append(departure_time)
                    # (a3) Insert the event into GEL - Event(departure time, type = departure, service time = 0)
                    new_departureEvent = Event(departure_time, "DEPARTURE", 0)
                    host.gel.append(new_departureEvent)
                    # GEL is sorted in time.
                    host.gel.sort(key=lambda x: x.eventTime) 
                # (b) if the server is busy, ie if length > 0
                # else Put the packet into the queue.
                else:
                    last_departure_time = host.fifo[host.length-1]
                    host.length += 1
                    serviceTime = NED_time(serviceRate)
                    host.fifo.append(serviceTime + last_departure_time)
                               
                #mqlsum += length
            # 3.4 Processing a departure event
            elif curEvent.eventType == "DEPARTURE":
                # Since this is a packet departure, we decrement the length.
                host.length -= 1
                host.fifo.pop(0)
                if host.length > 0:
                    # dequeue the first packet from the buffer
                    # create a new departure event for a time
                    new_departure_time = host.fifo[0]
                    new_departureEvent = Event(new_departure_time, "DEPARTURE", serviceTime)
                    # insert the event at the right place in GEL
                    host.gel.append(new_departureEvent)
                    host.gel.sort(key=lambda x: x.eventTime)



def main():

    for lam in [0.01, 0.05, 0.1, 0.3, 0.6, 0.8, 0.9]:
        simulation(4, lam, 1)


main()