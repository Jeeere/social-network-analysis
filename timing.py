# source: http://stackoverflow.com/a/1557906/6009280
 
import atexit
from time import perf_counter as clock
from functools import reduce
 
logs:list[str] = []

def seconds_to_str(t):
    return "%d:%02d:%02d.%03d" % \
           reduce(lambda ll, b: divmod(ll[0], b) + ll[1:],
                  [(t * 1000,), 1000, 60, 60])
 
 
line = "=" * 40
 
 
def log(s, elapsed=None):
    x = ""
    # print(line)
    # print(seconds_to_str(clock()), '-', s)
    x += (seconds_to_str(clock())+ '-'+ s)
    if elapsed:
        # print("Elapsed time:", elapsed)
        x += "\nElapsed time:"+ elapsed
    # print(line)
    # print()
    logs.append(x)
 
 
def endlog():
    end = clock()
    elapsed = end - start
    log("End Program", seconds_to_str(elapsed))
    print(line)
    print(" "*17 + "SUMMARY" + " "*16)
    print(line)
    for x in logs:
        print(x)
    print(line)


 
 
def now():
    return seconds_to_str(clock())
 
 
start = clock()
atexit.register(endlog)
log("Start Program")