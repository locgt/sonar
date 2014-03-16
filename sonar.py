#!/usr/bin/env python
 
import os
import xively
import subprocess
import time
import datetime
import requests
 
FEED_ID = "your feed id here"  #enter your feed ID number here
API_KEY = "Your API key here"  #set your API key here
DEBUG = True
 
# initialize api client
api = xively.XivelyAPIClient(API_KEY)
 
# function to return a datastream object. This either creates a new datastream,
# or returns an existing one
def get_datastream(feed):
  try:
    datastream = feed.datastreams.get("SaltLevel")
    if DEBUG:
      print "Found existing datastream"
    return datastream
  except:
    if DEBUG:
      print "Creating datastream"
    datastream = feed.datastreams.create("SaltLevel", unit={'label':'centimeters', 'symbol':'cm'})
    return datastream
 
# main program entry point - runs continuously updating our datastream with the
# current 1 minute load average
def run():
  print "Starting Xively update script"
 
  feed = api.feeds.get(FEED_ID)
 
  datastream = get_datastream(feed)
  datastream.max_value = None
  datastream.min_value = None
 
  while True:
    level = int(round(reading(0)))
 
    if DEBUG:
      print "Updating Xively feed with value: %s" % level
 
    datastream.current_value = level
    datastream.at = datetime.datetime.utcnow()
    try:
      datastream.update()
    except requests.HTTPError as e:
      print "HTTPError({0}): {1}".format(e.errno, e.strerror)
 
    time.sleep(10)

def reading(sensor):
	import time
	import RPi.GPIO as GPIO
	
	# Disable any warning message such as GPIO pins in use
	GPIO.setwarnings(False)
	
	# use the values of the GPIO pins, and not the actual pin number
	# so if you connect to GPIO 25 which is on pin number 22, the 
	# reference in this code is 25, which is the number of the GPIO 
	# port and not the number of the physical pin
	GPIO.setmode(GPIO.BCM)
	
	if sensor == 0:
		
		# point the software to the GPIO pins the sensor is using
		# change these values to the pins you are using
		# GPIO output = the pin that's connected to "Trig" on the sensor
		# GPIO input = the pin that's connected to "Echo" on the sensor
		GPIO.setup(17,GPIO.OUT)
		GPIO.setup(27,GPIO.IN)
		GPIO.output(17, GPIO.LOW)
		
		# found that the sensor can crash if there isn't a delay here
		# no idea why. If you have odd crashing issues, increase delay
		time.sleep(0.3)
		
		# sensor manual says a pulse ength of 10Us will trigger the 
		# sensor to transmit 8 cycles of ultrasonic burst at 40kHz and 
		# wait for the reflected ultrasonic burst to be received
		
		# to get a pulse length of 10Us we need to start the pulse, then
		# wait for 10 microseconds, then stop the pulse. This will 
		# result in the pulse length being 10Us.
		
		# start the pulse on the GPIO pin 
		# change this value to the pin you are using
		# GPIO output = the pin that's connected to "Trig" on the sensor
		GPIO.output(17, True)
		
		# wait 10 micro seconds (this is 0.00001 seconds) so the pulse
		# length is 10Us as the sensor expects
		time.sleep(0.00001)
		
		# stop the pulse after the time above has passed
		# change this value to the pin you are using
		# GPIO output = the pin that's connected to "Trig" on the sensor
		GPIO.output(17, False)

		# listen to the input pin. 0 means nothing is happening. Once a
		# signal is received the value will be 1 so the while loop
		# stops and has the last recorded time the signal was 0
		# change this value to the pin you are using
		# GPIO input = the pin that's connected to "Echo" on the sensor
		while GPIO.input(27) == 0:
		  signaloff = time.time()
		
		# listen to the input pin. Once a signal is received, record the
		# time the signal came through
		# change this value to the pin you are using
		# GPIO input = the pin that's connected to "Echo" on the sensor
		while GPIO.input(27) == 1:
		  signalon = time.time()
		
		# work out the difference in the two recorded times above to 
		# calculate the distance of an object in front of the sensor
		timepassed = signalon - signaloff
		
		# we now have our distance but it's not in a useful unit of
		# measurement. So now we convert this distance into centimetres
		distance = timepassed * 17000
		
		# return the distance of an object in front of the sensor in cm
		return distance
		
		# we're no longer using the GPIO, so tell software we're done
		GPIO.cleanup()

	else:
		print "Incorrect usonic() function varible."
		
run()
