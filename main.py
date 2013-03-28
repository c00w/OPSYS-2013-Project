#!/usr/bin/env python3
#OpSys Project 1 by Michael Pomeranz and Colin Rice
from collections import deque
from random import randrange,random
from math import log
from sys import argv

RR_TIME = 200
last_switch = 0

class Process():
    def __init__(self, pid, start, needed, priority):
        self.pid = pid
        self.start = start
        self.priority = priority
        self.run = 0
        self.needed = needed
        self.wait = 0
        self.initial_wait = 0

    def step(self):
        self.run += 1

    def done(self):
        return self.run == self.needed

    def sleepstep(self):
        self.wait += 1
        if not self.run:
            self.initial_wait += 1

    def left(self):
        return self.needed - self.run;

def exp_rand(n = 20):
    lamb = .001
    nums = []
    i = 0
    while(i<n):
        x = int(-log(random())/lamb)
        if x>8000:
            continue
        nums.append(x)
        i += 1
    return nums

def create_processes(n=20):
    try:
        x = int(.8 * n)
        y = n - x
        argv.index("-PART2")
        starts = exp_rand(x)
        p = [Process(pid, 0, randrange(500, 4001), randrange(0, 5)) for pid in range(y)]
        p.extend([Process(pid+y, starts[pid], randrange(500,4001), randrange(0,5)) for pid in range(x)])
    except:
        p = [Process(pid, 0, randrange(500, 4001), randrange(0, 5)) for pid in range(n)]
    return p


def tprint(time, message):
    print("[time %sms] %s" % (time, message))

def done(proc):
    return proc.needed == proc.run

def simulate(func):
    global last_switch
    notreadyp = create_processes()
    readyp = []
    backup_p = [x for x in notreadyp]
    time = 0
    switchtime = 0
    last_switch = 0
    current = None
    last_current = None
    while notreadyp != [] or readyp != []:
        temp = []
        for proc in notreadyp:
            if proc.start == time:
                temp.append(proc)
                tprint(time, "Process %s created (requires %sms CPU time)" % (
                proc.pid, proc.needed))
        for proc in temp:
            notreadyp.remove(proc)
        if readyp == [] and temp == []:
            time += 1
            continue
        next_current = func(time,current,readyp,temp)
        if time == 0:
            current = next_current
        if next_current != current and next_current != None:
            if switchtime != 10 and switchtime != 0:
                time += 1
                switchtime -= 1
                for proc in readyp:
                    proc.sleepstep()
                continue
            #do a context switch
            last_switch = 0
            if switchtime == 0:
                switchtime = 17
            if current == None:
                current = last_current
            tprint(time,"Context switch (swapping out process "+ str(current.pid) + " for process " + str(next_current.pid))
            current = next_current
            time += 1
            switchtime -= 1
            for proc in readyp:
                proc.sleepstep()
            continue
        if switchtime != 0:
            time += 1
            switchtime -= 1
            for proc in readyp:
                proc.sleepstep()
            continue
        if current != None:
            for proc in readyp:
                if current == proc:
                    proc.step()
                else:
                    proc.sleepstep()
            if current.done():
                readyp.remove(current);
                current.turn = time-current.start
                tprint(time, 'Process %s completed its CPU burst (turnaround time %sms, initial wait time %sms, total wait time %sms)'%( current.pid, time-current.start, current.initial_wait, current.wait))
                last_current = current
                current = None
        time += 1
        last_switch += 1

    turn = []
    initial_wait = []
    tot_wait = []
    for p in backup_p:
        turn.append(p.turn)
        initial_wait.append(p.initial_wait)
        tot_wait.append(p.wait)

    print('Turnaround time: min %0.3fms; avg %0.3fms; max %0.3fms' % (min(turn), sum(turn)/len(turn), max(turn)))
    print('Initial wait time: min %0.3fms; avg %0.3fms; max %0.3fms' % (min(tot_wait), sum(tot_wait)/len(tot_wait), max(tot_wait)))
    print('Total wait time: min %0.3fms; avg %0.3fms; max %0.3fms' % (min(tot_wait), sum(tot_wait)/len(tot_wait), max(tot_wait)))



def fcfs(time,current,p,newp):
       p.extend(newp)
       if current == None:
           return p[0]
       return current

def sjf(time,current,p,newp):
    p.extend(newp)
    p.sort(key=lambda proc: proc.left())
    if current == None:
        return p[0]
    return current

def sjfp(time,current,p,newp):
    p.extend(newp)
    p.sort(key=lambda proc: proc.left())
    if current == None:
        return p[0]
    if p[0].left() < current.left():
        return p[0]
    return current
    
def rr(time,current,p,newp):
    global RR_TIME
    global last_switch
    p.extend(newp)
    if current == None:
        return p[0]
    if last_switch < RR_TIME:
        return current
    last_switch = 0
    p.append(p.pop(0))
    return p[0]

def pp(time,current,p,newp):
    global RR_TIME
    global last_switch
    p.extend(newp)
    p.sort(key=lambda proc: proc.priority)
    if current == None:
        if p[0].run % RR_TIME != 0:
            last_switch = p[0].run % RR_TIME
        return p[0]
    if p[0] != current:
        last_switch = 0
        return p[0]
    if last_switch < RR_TIME:
        return current
    last_switch = 0
    p.append(p.pop(0))
    p.sort(key=lambda proc: proc.priority)
    if p[0].run % RR_TIME != 0:
        last_switch = p[0].run % RR_TIME
    return p[0]
    

try:
    simulate(fcfs)
    simulate(sjf)
    simulate(sjfp)
    simulate(rr)
    simulate(pp)

except:
    import traceback
    traceback.print_exc()
