#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import httplib
import string
import requests
import sys
import json

items_list = ""
iteration = 0
isodate = ""
readerId = "DC-LON-01" # HARDCODED readerId - needs to be changed for each reader instance

if (len(sys.argv) != 2):
    sys.exit()

headers = {
    'content-type': "application/json",
    'x-apikey': sys.argv[1],
    'cache-control': "no-cache"
}

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    print "Exited safely."
    GPIO.cleanup()
    sys.exit()
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# This is the default key for authentication
key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

# Welcome message
print "Welcome to the Digital Catapult Visitor Tracking System [DC-LON-01]"
print "Press Ctrl-C to stop."

# Blocks and sectors
blocks = [1,2,4,5,6,8,9,10,12,13,14,16,17,18,20,21,22,24,25,26,28,29,30,32,33,34,36,37,38,40,41,42,44,45,46,48,49,50,52,53,54,56,57,58,60,61,62]
sectors = [0,0,1,1,1,2,2,2,3,3,3,4,4,4,5,5,5,6,6,6,7,7,7,8,8,8,9,9,9,10,10,10,11,11,11,12,12,12,13,13,13,14,14,14,15,15,15]

latest_card = ''

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while True:
    print 'hello'
