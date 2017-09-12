from time import sleep
import sys


def sleepprogbar(timeToSleep):
    i = 0
    while i <= timeToSleep:
        prog = ((100 * i) / timeToSleep) + 0.0
        timeremaining = timeToSleep - i
        stringtoprint = "    -> Sleep progress: /" + int(prog/5)*"/" + (20 - int(prog/5))*" " + "/ " + str(timeremaining) + " seconds left.      \r"
        print stringtoprint,
        #print ""
        i += 1
        sleep(1)
    print "    -> Sleep progress: ////////////////////// DONE                    \r",
    print ""
sleepprogbar(5)
