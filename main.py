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
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    #
    #
    # If a card is found
    #
    if status == MIFAREReader.MI_OK:
        try:
            iteration = 0
            items_list = ""
            (status,nuid) = MIFAREReader.MFRC522_Anticoll()
            if (len(nuid) >= 4 and (nuid != latest_card)):
                print "Card detected"
                latest_card = nuid
                NUID16 = []
                idall = "%02x%02x%02x%02x" % (nuid[0], nuid[1], nuid[2], nuid[3])
                for j in range(0, 4):
                    if len(str(nuid[j]))== 1:
                        NUID16.append(str("0")+str(hex(nuid[j]))[2:])
                    else:
                        NUID16.append(str(hex(nuid[j]))[2:])
                (status,nuid) = MIFAREReader.MFRC522_Anticoll()
                MIFAREReader.MFRC522_SelectTag(nuid)

                #
                #
                # Get every block
                #
                for i in range(0,46):
                    index = blocks[i]
                    status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, index, key, nuid)
                    if status == MIFAREReader.MI_OK:
                        GetValue = MIFAREReader.MFRC522_ReturnValue(index)
                        if (len(GetValue) == 0):
                            items_list = ''
                            print 'no GetValue?'
                            break
                        hasData = GetValue[0] == sectors[i] and GetValue[1] == blocks[i]
                        if (hasData):
                            dd = GetValue[3]
                            month = GetValue[4]
                            yy = GetValue[5]
                            hh = GetValue[7]
                            mm = GetValue[8]
                            isodate = "20%02d-%02d-%02dT%02d:%02d" % (yy, month, dd, hh, mm)
                            if (iteration == 0):
                                items_list = str(i)
                                iteration = iteration + 1
                            else:
                                items_list = items_list + ";" + str(i)
                    else:
                        print "card not ok"
                        items_list = ''
                        break

                if items_list == '':
                    print 'No data'
                    latest_card = ''
                else:
                    # construct a single record for the visit - person (UID) based
                    # we can use UID, readerId, datetime (of last item) - need to laminate itemId into a composite ... semi-colon separated
                    # write to database
                    url = "https://sensit-17f0.restdb.io/rest/dc-fnl-tracking-person"
                    payload = '{"UID" : "%s", "readerId" : "%s",  "items_list" : "%s", "datetime" : "%s" }' % (idall, readerId, items_list, isodate)
                    print "Saving..."
                    response = requests.request("POST", url, data=payload, headers=headers)
                    print "Saved!", response

                items_list = ""
                GPIO.cleanup()
                MIFAREReader = MFRC522.MFRC522()
        except:
            print "it failed for an unknown reason"
