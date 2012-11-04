import array
from ola.ClientWrapper import ClientWrapper
import threading
import time
import random

print "Loading Libraries: Done"

#####################################################################
## OLA
#####################################################################

class DMXServerThread(threading.Thread):
    wrapper = None
    TICK_INTERVAL = 1  # in ms
    SPEED = 3           # speed multiplier
    targetValues = [0,0,0,0,0,0,0,0,0]
    currentValues = [0,0,0,0,0,0,0,0,0]

    def __init__(self):
        print "DMXServerThread Init"
        threading.Thread.__init__(self)
        self.wrapper = ClientWrapper()

    def DmxSent(self, state):
        if not state.Succeeded():
            print "DMX Sending Failed for some reason"
            self.wrapper.Stop()

    def SendDMXFrame(self):
        # continuously schedule the next function call
        self.wrapper.AddEvent(self.TICK_INTERVAL, self.SendDMXFrame)

        # if current values are within range of target, set to target; prevent target oscillation
        for i,v in enumerate(self.currentValues):
            diff = abs(self.targetValues[i] - v)
            if diff > 0 and diff <= self.SPEED:
                #print "Forcing channel %s to %s" % (i, v)
                self.currentValues[i] = v

        # Don't flood the dmx controller with unnecessary messages
        if self.currentValues == self.targetValues:
            return

        # compute next current value for each channel & add to frame
        data = array.array('B')
        for i,v in enumerate(self.targetValues):
            newVal = self.currentValues[i] + (cmp(self.targetValues[i] - self.currentValues[i], 0) * self.SPEED)
            #print newVal
            if(newVal > 255): newVal = 255
            if(newVal < 0): newVal = 0
            self.currentValues[i] = newVal
            
            data.append(self.currentValues[i])

        self.wrapper.Client().SendDmx(1, data, self.DmxSent)

    def setTargets(self, _targetValues={}):
        for k,v in _targetValues.iteritems():
            if not isinstance(k, int) or k > 10:
                print "Target channel is not an int or is out of range"
                return
            self.targetValues[k] = v

    def stop(self):
        self.wrapper.Stop()

    def run(self):
        self.wrapper.AddEvent(self.TICK_INTERVAL, self.SendDMXFrame)
        self.wrapper.Run()

def fadeDone():
    print "Fade Done in other thread"

#####################################################################
## Logic
#####################################################################

def findKeywords(inputStr):
    # Build a list of channels that contain keywords in the input string
    channels = []
    inputs = inputStr.split(" ")
    for i in inputs:
        for dk,dv in keywords.iteritems():
            if i in dv:
                channels.append(dk)
    return channels

#####################################################################
## Main
#####################################################################

print "Starting DMX Server Thread"
dmxServer = DMXServerThread()
dmxServer.start()

print "Starting Demo Cycle"

while True:
    chanDict = {}
    for x in range(9):
        chanDict[x] = random.randint(0, 1) * 255
    print "Setting %s" % chanDict
    dmxServer.setTargets(chanDict)
    time.sleep(random.randint(1, 4))

    # chanDict = {}
    # for x in range(9):
    #     chanDict[x] = random.randint(0, 1) * 255
    # print "Setting %s" % chanDict
    # dmxServer.setTargets(chanDict)
    # time.sleep(4)