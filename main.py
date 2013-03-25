#!/usr/bin/env python3
from collections import deque
from random import randrange,random
from math import log

def exp_rand(n = 20):
    lamb = .001
    nums = []
    i = 0
    while(i<n):
        x = -log(random())/lamb
        if x>8000:
            continue
        nums.append(x)
        i += 1
    return nums

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

def create_processes(n=20):
    p = [Process(pid, 0, randrange(500, 4001), randrange(0, 5)) for pid in range(n)]
    return p


def tprint(time, message):
    print("[time %sms] %s" % (time, message))

def done(proc):
    return proc.needed == proc.run

def simulate(choose):
    p = create_processes()
    backup_p = [x for x in p]
    for proc in p:
        tprint(0, "Process %s created (requires %sms CPU time)" % (
        proc.pid, proc.needed))
    current = None
    time = 0
    switchtime = 0
    while p != []:
        time += 1
        next_current = choose(p, current, time)
        if next_current != current and current is not None:
            #context switch
            tprint(time, 'Context switch (swapping out process %s for process %s)' % (current.pid, next_current.pid))
            time += 17
            for i in range(17):
                for proc in p:
                    proc.sleepstep()
            current = next_current
            continue
        current = next_current
        for proc in p:
            if proc is not current:
                proc.sleepstep()
            else:
                proc.step()
        if current.done():
            p.remove(current)
            current.turn = time-current.start
            tprint(time, 'Process %s completed its CPU burst (turnaround time %sms, initial wait time %sms, total wait time %sms)'%( current.pid, time-current.start, current.initial_wait, current.wait))

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

def fcfs(p, current, time):
    for proc in p:
        if proc.start <= time:
            return proc
    return p[0]

def sjf(p, current, time):
    if current not in p:
        next = p[0]
        for proc in p:
            if proc.start > time:
                continue
            if proc.needed < next.needed:
                next = proc
        return next
    return current

def sjfp(p, current, time):
    next = p[0]
    for proc in p:
        if proc.start > time:
            continue
        if proc.needed < next.needed:
            next = proc
    return next


def rrg():
    loop = deque()
    start = [0]
    def rr(proc, current, time):
        for p in proc:
            if p not in loop:
                if p.start <= time:
                    loop.append(p)
        for p in list(loop):
            if p not in proc:
                loop.remove(p)
        if current is None or current.run - start[0] > 200 or current not in proc:
            a = loop.pop()
            loop.appendleft(a)
            start[0] = a.run
            return a
        return current
    return rr

def ppg():
    rr = rrg()
    def pp(proc, current, time):
        for prio in range(0, 5):
            a = [p for p in proc if p.priority == prio and p.start <= time]
            if a:
                return rr(a, current, time)
        return proc[0]
    return pp

try:
    simulate(fcfs)
    simulate(sjf)
    simulate(sjfp)
    simulate(rrg())
    simulate(ppg())

except:
    import traceback
    traceback.print_exc()
