#!/usr/bin/env python3
import requests
import json
import time
import paho.mqtt.client as mqtt

from config import *

input_map = {
    "BD": "BD",
    "Shield": "DVD",
    "Nintendo": "GAME",
    "Sonos": "SAT/CATV",
    "FireTV": "VIDEO"
}

inputs = ["BD", "DVD", "GAME", "SAT/CATV", "VIDEO", "TV", "SA-CD/CD", "FM TUNER", "AM TUNER", "USB", "HOME NETWORK", "SEN"]

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

class SonySTRDN840:
    def __init__(self, address, status_port, control_port, id, dev_info, user_agent):
        self.address = address
        self.status_port = status_port
        self.control_port = control_port
        self.id = id
        self.dev_info = dev_info
        self.user_agent = user_agent

    def getCurrentInput(self):
        url='http://%s:%d/cers/getStatus' % (self.address, self.status_port)
        
        headers = {
            'X-CERS-DEVICE-ID': self.id,
            'X-CERS-DEVICE-INFO': self.dev_info,
            'Connection': 'close',
            'User-Agent': self.user_agent,
            'Host': '%s:%d' % (self.address, self.status_port),
            'Accept-Encoding': 'gzip'
        }

        try:
            r = requests.get(url, headers=headers, timeout=0.75)
        except:
            return "offline"

        try: 
            return r.text.split("=")[3].split("\"")[1]
        except IndexError:
            return "error"

    def sendCommand(self, cmd):
        url='http://%s:%d/upnp/control/IRCC' % (self.address, self.control_port)
        
        headers = {
            'soapaction': '\"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC\"',
            'content-type': 'text/xml; charset=utf-8',
            'Connection': 'close',
            'User-Agent': self.user_agent,
            'Host': '%s:%d' % (self.address, self.control_port),
            'Accept-Encoding': 'gzip'
        }
        
        payload  = "<?xml version=\"1.0\"?>"
        payload += "<s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\">"
        payload += "<s:Body> <u:X_SendIRCC xmlns:u=\"urn:schemas-sony-com:service:IRCC:1\"> <IRCCCode>%s==</IRCCCode>" % commands[cmd.lower()]
        payload += "</u:X_SendIRCC> </s:Body> </s:Envelope>" 

        try:
            requests.post(url, headers=headers, data=payload)
        except:
            pass

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    
    targetInput = input_map[payload]

    print("Switching to %s" % targetInput)

    sony = SonySTRDN840(sony_address, sony_port_status, sony_port_control, sony_myid, sony_mydevinfo, sony_myuseragent)

    currentInput = sony.getCurrentInput()
    print("Current input: ", currentInput)

    current_idx = inputs.index(currentInput)
    target_idx = inputs.index(targetInput)
    diff = target_idx - current_idx

    for i in range(0, abs(diff)):
        command = "STR_FunctionMinus" if diff < 0 else "STR_FunctionPlus"
        sony.sendCommand(command)
        print("send: ", i, command)
        time.sleep(.25)


def on_connect(client, userdata, flags, rc):
    print("Connected...")
    client.subscribe("%s" % mqtt_topic)
    print("MQTT listening to %s ..." % mqtt_topic)

def main():
    # sony = SonySTRDN840(sony_address, sony_port_status, sony_port_control, sony_myid, sony_mydevinfo, sony_myuseragent)
    # sony.getCurrentInput()
    # sony.sendCommand("muteon")

    payload = {
        "command_topic": mqtt_topic,
        "name": "Sony Receiver",
        "options": [ "BD", "Shield", "Nintendo", "Sonos", "FireTV" ],
        "device": {
            "identifiers": [
                "sony-strdn840"
            ],
            "model": "STR-DN840",
            "manufacturer": "Sony"
        }
    }

    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(mqtt_host, mqtt_port, 20)
    client.publish("homeassistant/select/sony/config", json.dumps(payload))
    client.loop_forever(retry_first_connection=True)


main()