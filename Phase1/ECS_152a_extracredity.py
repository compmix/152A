import random
import math
import matplotlib.pyplot as plt

# 3.6
# Negative Exponential Distributed Time:
def NED_time(rate):
    u = random.random()
    return  ((-1/rate)* math.log(1-u))

#3.8
def Pareto_time(rate):
	u = random.random()
	return ( 1 / ( math.log(1 - u) / math.log(rate)) )


# 3.1
# Data structures
class Event():
    def __init__(self, eventTime, eventType, serviceTime):
        self.eventTime = eventTime
        self.eventType = eventType
        self.serviceTime = serviceTime


def server_queue(arrivalRate, serviceRate, maxBuffer):
    # 3.2
    # Initialization:
    # We will initialize length to be 0.
    length = 0 
    # Variable time to denote the current time, initialize to 0.
    time = 0
    MAXBUFFER = maxBuffer
    # Set the service rate and the arrival rate of the packets
    arrival_rate = arrivalRate
    service_rate = serviceRate
    # Create first arrival event - first in first out?
    fifo = []
    # GEL
    gel = []
    # The event time of the first arrival event is obtained by
    # adding a randomly generated inter-arrival time to the current time
    first_arrival_event_time = Event(time + Pareto_time(arrival_rate), "ARRIVAL", NED_time(service_rate))
    gel.append(first_arrival_event_time)

    # 3.5 variables
    # number of packet dropped
    packet_dropped = 0
    # mean queue length
    mql = 0
    mqlsum = 0
    # utilization
    utilization = 0
    busyTime = 0
    
    # want to check each discrete time step to get the MQL
    for i in range(0, 100000):
        mqlsum += length

        # only process events that occur during this timestep
        if gel[0].eventTime > i+1:
            continue

        # 3.1 - 1 get the first event from the GEL;
        curEvent = gel.pop(0)

        # 3.3 - Processing an Arrival Event
        if curEvent.eventType == "ARRIVAL":
            # (1) find the time of the next arrival, which is current time
            time = curEvent.eventTime
            # Find next arrival time, which is current time plus a randomly generated time drawn from a NED random variable with rate lambda
            next_arrival_time = time + Pareto_time(arrival_rate)
            # (2) Create a new packet and determine its service time which is randomly generated time drawn from a NED random variable with rate mu
            service_time = NED_time(service_rate)
            # (3) Create a new arrival Event(next arrival time, type = arrival, service time)
            new_arrivalEvent = Event(next_arrival_time, "ARRIVAL" , service_time)
            # (4) Insert the event into the event list - GEL
            gel.append(new_arrivalEvent)
            # GEL is sorted in time.
            gel.sort(key=lambda x: x.eventTime)

            # Process the arrival event:
            # (a) If the server is free
            if length == 0:
                # (a1) Get the service time of the packet
                length += 1
                # (a2) Create a depature event at time which is equal to the current time plus the service time of the packet
                # Again it is randomly generated from NED random variable
                departure_time = time + service_time
                fifo.append(departure_time)
                # (a3) Insert the event into GEL - Event(departure time, type = departure, service time = 0)
                new_departureEvent = Event(departure_time, "DEPARTURE", 0)
                gel.append(new_departureEvent)
                # GEL is sorted in time.
                gel.sort(key=lambda x: x.eventTime) 
                busyTime += service_time
            # (b) if the server is busy, ie if length > 0
            # if the queue is full, drop the packet, record a packet drop
            elif length == MAXBUFFER and MAXBUFFER > 0:
                packet_dropped = packet_dropped + 1
            # else Put the packet into the queue.
            else:
                last_departure_time = fifo[length-1]
                length += 1
                service_time = NED_time(service_rate)
                fifo.append(service_time + last_departure_time)
                busyTime += service_time
                           
            mqlsum += length
        # 3.4 Processing a departure event
        elif curEvent.eventType == "DEPARTURE":
            # Since this is a packet departure, we decrement the length.
            length -= 1
            fifo.pop(0)
            if length > 0:
                # dequeue the first packet from the buffer
                # create a new departure event for a time
                new_departure_time = fifo[0]
                new_departureEvent = Event(new_departure_time, "DEPARTURE", service_time)
                # insert the event at the right place in GEL
                gel.append(new_departureEvent)
                gel.sort(key=lambda x: x.eventTime)
                mqlsum += length
                
    # Update Statistics
    # Utilization = the time for which the server is busy /  total time
    utilization = busyTime/time
    mql = mqlsum/time
    return utilization, mql, packet_dropped

# 3.7 Phase 1
def main():
    # 1 and 2
    p1_util = []
    p1_mql = []
    p1_arr = []
    MU = 1
    print("\t\t\t******** Part 1 and 2 *********")
    print("*----------------------------------------------------------------------*")
    print("|                 Assume that MU = 1 packet/second                     |")
    print("|                 MAXBUFFER is infinite - set to 100000                |")
    print("*----------------------------------------------------------------------*")

    print("{0:<15} {1:<15} {2:<20} {3:<15}".format(
        "Lambda", "Utilization", "Mean Queue Length", "Packets Dropped"))
    for arr in [0.1, 0.25, 0.4, 0.55, 0.65, 0.80, 0.90]:
        utilization, mql, packet_dropped = server_queue(arr, 1, 100000)
        print("{lamb:<15} {bt:<15.3f} {mql:<20.3f} {packet_dropped:<15}" .format(
            lamb = arr, bt = utilization, mql = mql, packet_dropped = packet_dropped))
        p1_mql.append(mql)
        p1_util.append(utilization)
        p1_arr.append(arr)

    # plot MQL vs lambda
    plt.subplot(1, 2, 1)
    plt.title('MQL')
    plt.xlabel('Arrival rate (lambda)')
    plt.grid(True)
    plt.plot(p1_arr, p1_mql, 'o-')
    # plot Utilization vs lambda
    plt.subplot(1, 2, 2)
    plt.title('Utilization')
    plt.xlabel('Arrival rate (lambda)')
    plt.grid(True)
    plt.plot(p1_arr, p1_util, 'o-')
    # show plots
    plt.show()


    # 3
    print("\n\t\t\t******** Part 3 *********")
    print("*----------------------------------------------------------------------*")
    print("|                 Assume that MU = 1 packet/second                     |")
    print("|                 MAXBUFFER is 1, 20 and 50                            |")
    print("*----------------------------------------------------------------------*")
    for index, buf in enumerate([1, 20, 50]):    
        print("MAXBUFFER = " + str(buf))
        print("{0:<15} {1:<15} {2:<20} {3:<15}".format(
        "Lambda", "Utilization", "Mean Queue Length", "Packets Dropped"))
        # store plot data
        p3_pktl = []
        p3_arr = []
        for arr in [0.2, 0.4, 0.6, 0.8, 0.9]: 
            utilization, mql, packet_dropped = server_queue(arr, 1, buf)
            print("{lamb:<15} {bt:<15.3f} {mql:<20.3f} {packet_dropped:<15}" .format(
                lamb = arr, bt = utilization, mql = mql, packet_dropped = packet_dropped))
            # store data in lists
            p3_pktl.append(packet_dropped)
            p3_arr.append(arr)

        # plot pkt loss
        plt.subplot(3, 1, index+1)
        plt.title('MAXBUFFER = ' + str(buf))
        plt.grid(True)
        plt.plot(p3_arr, p3_pktl, 'o-')

    # show 3 plots
    plt.show()


main()
