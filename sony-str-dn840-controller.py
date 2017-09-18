#!/usr/bin/env python
import requests
import itertools
import time
import sys 
import urllib

# config
ip="receiver"
port_status=50001
port_control=8080
max_vol = 10
myid="TVSideView:aa-bb-cc-dd-ee-ff"
myname="Jarvis"
mydevinfo='PythonScript' 
myuseragent='PythonScript'

# get currently active input  
def getCurrentInput():
	url='http://%s:%d/cers/getStatus' % (ip, port_status)
	headers = {
		'X-CERS-DEVICE-ID': myid,
		'X-CERS-DEVICE-INFO': mydevinfo,
		'Connection': 'close',
		'User-Agent': myuseragent,
		'Host': '%s:%d' % (ip, port_status),
		'Accept-Encoding': 'gzip'
	}
	try:
		r = requests.get(url, headers=headers)
	except ConnectionError:
		print("Connection error.")
		return "error"

	try: 
		source = r.text.split("=")[3].split("\"")[1]
		return source	
	except IndexError:
		print("returned(%d): %s" % (r.status_code, r.text))
		return "error"

# send a command
def sendCommand(key, repeat):
	# shortcuts
	if key == "power":
		key = "str_powermain"

	if not key.lower() in commands:
		print("Keycode for %s not found." % key)
		return 
	keycode = commands[key.lower()]
	url='http://%s:%d/upnp/control/IRCC' % (ip, port_control)
	headers = {
		'soapaction': '\"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC\"',
		'content-type': 'text/xml; charset=utf-8',
		'Connection': 'close',
		'User-Agent': myuseragent,
		'Host': '%s:%d' % (ip, port_control),
		'Accept-Encoding': 'gzip'
	}
	payload  = "<?xml version=\"1.0\"?>"
	payload += "<s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\">"
	payload += "<s:Body> <u:X_SendIRCC xmlns:u=\"urn:schemas-sony-com:service:IRCC:1\"> <IRCCCode>%s==</IRCCCode>" % keycode
	payload += "</u:X_SendIRCC> </s:Body> </s:Envelope>" 
	for i in range(0, int(repeat)):
		r = requests.post(url, headers=headers, data=payload)
		time.sleep(.5)

# Inputs
inputs = ["BD", "DVD", "GAME", "SAT/CATV", "VIDEO", "TV", "SA-CD/CD", "FM TUNER", "AM TUNER", "USB", "HOME NETWORK", "SEN"]

# Change input to
def switchInputTo(target):
	target = target.upper()

	# shortcuts
	if target == "SAT":
		target = "SAT/CATV"
	if target == "SACD":
		target = "SA-CD/CD"
	if target == "FM":
		target = "FM TUNER"
	if target == "AM":
		target = "AM TUNER"
	if target == "NET":
		target = "HOME NETWORK"

	if not target in inputs:
		print("Can't switch to this source: %s." % target)
		return
	idx = inputs.index(target)
	currentInput = getCurrentInput()
	if not currentInput in inputs:
		print("current input %s not in inputs." % currentInput)
		return 
	cidx = inputs.index(currentInput)
	diff = idx - cidx
	print("diff to %s is %d." % (target, diff))
	if diff < 0:
		sendCommand("STR_FunctionMinus", abs(diff))
	else:
		sendCommand("STR_FunctionPlus", diff)

def setVolumeTo(volume):
	vol = int(volume)
	if vol > max_vol: 
		vol = max_vol
		print("Max. allowed volume %d (because afraid :D)." % max_vol)
	sendCommand("VolumeDown", max_vol * 2)
	sendCommand("VolumeUp", vol)


# Commands
commands = {
	"str_powermain":		"AAAAAgAAADAAAAAVAQ==",
	"mute":					"AAAAAgAAADAAAAAUAQ==",
	"muteon":				"AAAAAwAADRAAAAAgAQ==",
	"muteoff":				"AAAAAwAADRAAAAAhAQ==",
	"confirm":				"AAAAAgAAADAAAAAMAQ==",
	"home":					"AAAAAgAAADAAAABTAQ==",
	"display":				"AAAAAgAAADAAAABLAQ==",
	"return":				"AAAAAwAAARAAAAB9AQ==",
	"options":				"AAAAAwAAARAAAABzAQ==",
	"str_functionplus":		"AAAAAgAAALAAAABpAQ==",
	"str_functionminus":	"AAAAAgAAALAAAABqAQ==",
	"play":					"AAAAAwAAARAAAAAyAQ==",
	"pause":				"AAAAAwAAARAAAAA5AQ==",
	"stop":					"AAAAAwAAARAAAAA4AQ==",
	"next":					"AAAAAwAAARAAAAAxAQ==",
	"prev":					"AAAAAwAAARAAAAAwAQ==",
	"str_shuffle":			"AAAAAwAAARAAAAAqAQ==",
	"str_repeat":			"AAAAAwAAARAAAAAsAQ==",
	"str_ff":				"AAAAAwAAARAAAAA0AQ==",
	"str_fr":				"AAAAAwAAARAAAAAzAQ==",
	"volumeup":				"AAAAAgAAADAAAAASAQ==",
	"volumedown":			"AAAAAgAAADAAAAATAQ==",
	"up":					"AAAAAgAAALAAAAB4AQ==",
	"down":					"AAAAAgAAALAAAAB5AQ==",
	"left":					"AAAAAgAAALAAAAB6AQ==",
	"right":				"AAAAAgAAALAAAAB7AQ==",
	"str_num1":				"AAAAAgAAADAAAAAAAQ==",
	"str_num2":				"AAAAAgAAADAAAAABAQ==",
	"str_num3":				"AAAAAgAAADAAAAACAQ==",
	"str_num4":				"AAAAAgAAADAAAAADAQ==",
	"str_num5":				"AAAAAgAAADAAAAAEAQ==",
	"str_num6":				"AAAAAgAAADAAAAAFAQ==",
	"str_num7":				"AAAAAgAAADAAAAAGAQ==",
	"str_num8":				"AAAAAgAAADAAAAAHAQ==",
	"str_num9":				"AAAAAgAAADAAAAAIAQ==",
	"str_num0":				"AAAAAgAAADAAAAAJAQ==",
	"str_puredirect":		"AAAAAwAABRAAAAB5AQ=="
}

def printUsage():
	print("Usage: %s register" % sys.argv[0])
	print("Usage: %s status" % sys.argv[0])
	print("Usage: %s cmd <Mute, VolumeUp, VolumeDown, ...> [<repeat>]" % sys.argv[0])
	print("Usage: %s list cmd" % sys.argv[0])
	print("Usage: %s switch <BD, DVD, GAME, ...>" % sys.argv[0])
	print("Usage: %s list input" % sys.argv[0])
	print("Usage: %s vol <0-20>" % sys.argv[0])
	print("Usage: %s power <on/off>" % sys.argv[0])

# scan all possible status values
def scanStatus():
	switchInputTo("BD")
	for i in range(len(inputs)):
		sendCommand("STR_FunctionPlus")
		print(getCurrentInput())

# initially register yourself with the receiver (go to HOME NETWORK on your 
# receiver and make it listen for registrations via the options menu for this)
def register():
	encodedid = urllib.parse.quote_plus(myid)
	print(encodedid)
	url='http://%s:%d/cers/register?name=%s&registrationType=initial&deviceId=%s' % (ip, port_status, myname, encodedid)
	headers = {
		'X-CERS-DEVICE-ID': myid,
		'X-CERS-DEVICE-INFO': mydevinfo,
		'Connection': 'close',
		'User-Agent': myuseragent,
		'Host': '%s:%d' % (ip, port_status),
		'Accept-Encoding': 'gzip'
	}
	r = requests.get(url, headers=headers)

# this allows explicitly turning the receiver on or off. this only works because
# of a very hacky assumption: when the receiver is off and still connected to
# ethernet, it will always show BD as active input. if you don't have anything
# connected to BD you will never use BD and thus you can assume the receiver is
# powered off when showing BD as active input. based on this assumption we can
# issue the str_powermain command to toggle its power state only if required to
# change its state explicitly to either on or off.
def changePowerState(action):
	input = getCurrentInput()
	rpower = False if input == "BD" else True
	if (action == "on" and not rpower) or (action == "off" and rpower):
		sendCommand("str_powermain", 1)

def main():
	argc = len(sys.argv)
	
	if argc == 2 and sys.argv[1] == "register":
		print("Registering as %s (ID:%s)", (myname, myid))
		register()
		exit(0)

	if argc == 2 and sys.argv[1] == "status":
		print("Currently selected input: %s." % getCurrentInput())
		exit(0)

	if argc == 3 and sys.argv[1] == "list":
		if sys.argv[2] == "cmd":
			for c in commands.keys():
				print("%s" % c)
		elif sys.argv[2] == "input":
			for i in inputs:
				print("%s" % i)
		exit(0)

	if argc == 3 and sys.argv[1] == "vol":
		print("Set volume %s..." % sys.argv[2])
		setVolumeTo(sys.argv[2])
		exit(0)

	if argc == 3 and sys.argv[1] == "cmd":
		print("Issuing command %s..." % sys.argv[2])
		sendCommand(sys.argv[2], 1)
		exit(0)

	if argc == 4 and sys.argv[1] == "cmd":
		print("Issuing command %s..." % sys.argv[2])
		sendCommand(sys.argv[2], int(sys.argv[3]))
		exit(0)

	if argc == 3 and sys.argv[1] == "switch":
		print("Switching to %s..." % sys.argv[2])
		switchInputTo(sys.argv[2])
		exit(0)

	if argc == 3 and sys.argv[1] == "power":
		action = sys.argv[2]
		if action != "on" and action != "off":
			print("Invalid option \"%s\", only \"on\" or \"off\" is allowed." % action)
			exit(1)
		changePowerState(action)
		exit(0)

	printUsage()

main()
