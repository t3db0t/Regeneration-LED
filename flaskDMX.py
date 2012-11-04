print "Starting Regeneration Server"
print "Loading Libraries..."

import array
from ola.ClientWrapper import ClientWrapper
import threading
from flask import Flask
from flask import request
from twilio import twiml
import time
import random
import datetime

print "...Done"

#####################################################################
## Global Settings
#####################################################################

CYCLE_DELAY_TIME = 60		# seconds

keywords = {
	0: ['regeneration', 'sustainability', 'Tomorrow', '2.0', 'tomorrow', 'Carl', 'Skelton', 're-envisioning', 'Flushing', 'Meadows', 'Corona', 'Park', 'generation', 'next-generation', 'urban', 'environment', 'ecosystem', 'mix', 'possibilities', 'world', 'fair', 'fairs', 'visions', 'future', 'cities', 'life', 'land', 'public', 'park', 'system', 'challenges', 'possibilities', 'framework', 'collaborative', 'participatory', 'virtual', 'laboratory', 'model', 'design', 'students', 'expertise', 'ideas', 'visitors', 'fly', 'hypothetical', 'artists', 'open-source'],
	1: ['regeneration', 'sustainability', 'new', 'york', 'Nick', 'Yulman', 'data', 'represented', 'representation', 'digital', 'digitally', 'control', 'controlled', 'acoustic', 'sound', 'installation', 'network', 'mechanically', 'mechanical', 'actuated', 'piano', 'strings', 'nodes', 'map', '1855', 'algorithmic', 'musical', 'music', 'composition', 'sonically', 'sonic', 'representing', 'changing population', 'countries', 'contry', 'connected', 'residents'],
	2: ['regeneration', 'sustainability', 'Biomodd', 'Angelo', 'Vermeulen', 'multifaceted', 'social', 'socially', 'engaged', 'meaningful', 'relationships', 'biology', 'computers', 'computer', 'people', 'symbiotic', 'plants', 'conversations', 'community', 'algae', 'cool', 'processors', 'heat', 'ecosystem', 'dynamic', 'catalysis', 'collaboration', 'artists', 'biologists', 'scientists', 'game', 'designers', 'gardeners', 'growing', 'food', 'systems', 'team', 'world', 'New York', 'collaborators', 'volunteers', 'different', 'viewpoints', 'complementary', 'version'],
	3: ['regeneration', 'sustainability', '2049', 'scott', 'kildall', 'landfills', 'raw materials', 'materials', 'garbage', 'sculptures', 'blueprints', 'San Francisco', 'residency', 'prospector', 'imaginary devices', 'device', 'survive', 'universal', 'send', 'message', 'time', 'capsule', 'submit', 'vision', 'reuse', 'throw', 'away', 'future', 'smell', 'resource', 'recycle', 'trash'],
	4: ['regeneration', 'sustainability', 'face', 'Zach', 'Lieberman', 'see', 'ourselves', 'people', 'faces', 'photo', 'booth', 'participant', 'participants', 'video', 'live', 'visualization', 'custom', 'software', 'visualize', 'eyes', 'noses', 'mouths', 'eyebrows', 'parts', 'previous', 'database', 'present', 'similarities', 'differences', 'difference', 'similar', 'view', 'look', 'diverse', 'textures', 'rhythms', 'styles', 'algorithmic', 'collective', 'portrait', 'museum', 'visitors'],
	5: ['regeneration', 'sustainability', 'world', 'fair', 'fairs', '2.0', 'Marisa', 'Jahn', 'Stephanie', 'Rothenberg', 'reclaims', 're-envisioning', 're-envision', 'transformed', 'valley', 'ashes', 'Flushing', 'Meadowns', 'Corona', 'Park', '1939', '1964', 'Futurama', 'road', 'tomorrow', 'electrical', 'living', 'visitors', 'products', 'ideas', 'robots', 'national psyche', 'global', 'consciousness', 'cultural', 'technological', 'history', 'teens', 'innovations', 'mobile', 'augmented', 'reality', 'technology', 'utopian', 'visions', 'past', 'future', 'space', 'game', 'interventions', 'tools', 'present'],
	6: ['regeneration', 'sustainability', 'geography', 'geographia', 'Ricardo Miranda', 'Zuniga', 'undocumented', 'immigrant', 'population', 'citizen', 'citizenry', 'youth', 'kinetic', 'drone', 'drones', 'video', 'game', 'challenges', 'player', 'zine', 'options', 'experiences', 'observations', 'self-determination', 'civil', 'status', 'politics', 'psychological', 'personal', 'relationships', 'life', 'activists', 'community'],
	7: ['regeneration', 'sustainability', 'ethnobotanical', 'new york', 'futurefarmers', 'future', 'farmer', 'historian', 'history', 'faith', 'fanatical', 'scientific', 'science', 'thought', 'meaning', 'human', 'existence', 'scientific', 'revolution', 'understanding', 'nature', 'manipulating', 'quantitative', 'qualitative', 'world', 'relationships', 'plants', 'food', 'closing', 'currency', 'ritual', 'medicine', 'dye', 'construction', 'cosmetics', 'indigenous', 'use', 'commercial', 'prospecting', 'piracy', 'pharmaceutical', 'knowledge', 'workshops'],
	8: ['regeneration', 'sustainability', '99plus', 'shih', 'chieh', 'huang', 'CJ', 'integration', 'science', 'technology', 'adaptations', 'interactions', 'complex', 'evolving', 'environment', 'research', 'observations', 'Queens', 'neighborhood', 'neighborhoods', 'every', 'day', 'ecology', 'storefronts', 'neighborhoods', 'recombination', 'elements', 'computer', 'microcontroller', 'inflatables', 'hybrid', 'materials', 'improvised', 'ad hoc', 'sculptures', 'patterns', 'electronic', 'kinetic', 'LED', 'LEDs', 'pulsate', 'life', 'cooperative', '99', 'cent', 'store']
}

# maps logical ring numbers to LED channel numbers

ledMap = {
	1: [1],
	2: [20],
	3: [3,15],
	4: [5],
	5: [7],
	6: [9,17],
	7: [29],
	8: [24],
	9: [32]
}

#####################################################################
## OLA
#####################################################################

class DMXServerThread(threading.Thread):
	wrapper = None
	TICK_INTERVAL = 1  # in ms
	SPEED = 3 			# speed multiplier
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

		dataFrame = [0 for x in range(32)]
		# compute next current value for each channel & add to frame
		data = array.array('B')
		for i,v in enumerate(self.targetValues):
			newVal = self.currentValues[i] + (cmp(self.targetValues[i] - self.currentValues[i], 0) * self.SPEED)
			#print newVal
			if(newVal > 255): newVal = 255 # clamp high output to max
			if(newVal < 0): newVal = 0
			self.currentValues[i] = newVal
			
			for di in ledMap[i+1]:
				dataFrame[di-1] = newVal
			#data.append(self.currentValues[i])
		# print "dataFrame: %s" % dataFrame
		# copy dataFrame to data
		for i in dataFrame:
			data.append(i)

		# copy values for extra lines
		# data.append(0)	# 10: not used
		# data.append(0)	# 11: not used
		# data.append(0)	# 12: not used
		# data.append(0)	# 13: not used
		# data.append(0)	# 14: not used
		# data.append(self.currentValues[2])	# 15: #3
		# data.append(0)	# 16: not used
		# data.append(self.currentValues[5])	# 17: #6
		# data.append(0)	# 18: not used
		# data.append(0)	# 19: not used
		# data.append(self.currentValues[1])	# 20: #2

		print "Sending DMX Frame: %s" % data
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
## Cycling Thread
#####################################################################

class CycleThread(threading.Thread):
	doCycle = True
	pausedTime = None

	def __init__(self):
		print "CycleThread Init"
		threading.Thread.__init__(self)

	def pauseCycle(self):
		print "CycleThread: pauseCycle"
		self.doCycle = False
		self.pausedTime = datetime.datetime.today()

	def resumeCycle(self):
		print "CycleThread: resumeCycle"
		self.doCycle = True

	def run(self):
		while True:

			if not self.doCycle and self.pausedTime:
				timeDiff = datetime.datetime.today() - self.pausedTime
				if timeDiff.seconds > CYCLE_DELAY_TIME:
					self.doCycle = True

			if self.doCycle:
				chanDict = {}
				for x in range(9):
					chanDict[x] = random.randint(0, 1) * 255
				print "CycleThread setting %s" % chanDict
				dmxServer.setTargets(chanDict)
				time.sleep(random.randint(1, 4))

#####################################################################
## Flask
#####################################################################

app = Flask(__name__)

@app.route('/sms', methods=['GET', 'POST'])
def sms():
	smsFrom = request.form.get('From')
	smsMessage = request.form.get('Body')
	print "Got SMS: %s" % smsMessage

	# parse the message: look for words in master dictionary
	onChannels = findKeywords(smsMessage)
	chanDict = {}
	numOn = 0
	for i in range(9):
		if i in onChannels:
			chanDict[i] = 255
			numOn += 1
		else:
			chanDict[i] = 0
	print "Setting channels: %s" % chanDict
	dmxServer.setTargets(chanDict)
	cycleThread.pauseCycle()

	response = twiml.Response()
	response.sms("Thanks for texting Regeneration at NYSCI. Your message matches %s of 9 artworks, lights them up, and adds to a collective display of interest." % numOn)
	return str(response)

@app.route('/test')
def testRoutine():
	print "Testing"
	dmxServer.setTargets({0:255})
	return "Testing"

@app.route('/set/<int:channel>/<int:v>')
def setChannelToValue(channel, v):
	print "Setting target channel %s to %s" % (channel, v)
	dmxServer.setTargets({channel:v})
	return "Setting target channel %s to %s" % (channel, v)

@app.route('/all/<int:c0>/<int:c1>/<int:c2>/<int:c3>/<int:c4>/<int:c5>/<int:c6>/<int:c7>/<int:c8>')
def setAll(c0,c1,c2,c3,c4,c5,c6,c7,c8):
	# print "Setting target channel %s to %s" % (channel, value)
	t = {0:c0,1:c1,2:c2,3:c3,4:c4,5:c5,6:c6,7:c7,8:c8}
	dmxServer.setTargets(t)
	# dmxServer.startFade(fadeDone)
	return "Setting channels to %s" % t

#####################################################################
## Logic
#####################################################################

def findKeywords(inputStr):
	# Build a list of channels that contain keywords in the input string
	channels = []
	inputs = inputStr.split(" ")
	inputs = [x.upper() for x in inputs]
	for i in inputs:
		for dk,dv in keywords.iteritems():
			dv = [x.upper() for x in dv]
			if i in dv:
				channels.append(dk)
	return channels

#####################################################################
## Main
#####################################################################

print "Starting DMX Server Thread"
dmxServer = DMXServerThread()
dmxServer.start()

print "Starting Cycle Thread"
cycleThread = CycleThread()
cycleThread.start()

print "Starting Web Server"
if __name__ == '__main__':
	app.run(debug=False, host='0.0.0.0')