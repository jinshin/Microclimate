#!/usr/bin/env python
# -*- coding: utf-8 -*-

import OPi.GPIO as GPIO
import time          # this lets us have a time delay

GPIO.setboard(GPIO.ZEROPLUS2H5)    # Orange Pi PC board
GPIO.setmode(GPIO.BOARD)        # set up BOARD BCM numbering
GPIO.setup(19, GPIO.OUT)         # set BCM7 (pin 26) as an output (LED)
GPIO.setup(21, GPIO.OUT)         # set BCM7 (pin 26) as an output (LED)
GPIO.setup(23, GPIO.OUT)         # set BCM7 (pin 26) as an output (LED)


GPIO.output(23, 1)
GPIO.output(21, 1)
GPIO.output(19, 1)

try:
  print ("Press CTRL+C to exit")
#  while True:

  SendPIN=23

  GPIO.output(SendPIN, 0)
  time.sleep(0.5)
  GPIO.output(SendPIN, 1)
  time.sleep(1)

  GPIO.output(SendPIN, 0)
  time.sleep(0.5)
  GPIO.output(SendPIN, 1)
  time.sleep(1)

  GPIO.output(SendPIN, 0)
  time.sleep(0.5)
  GPIO.output(SendPIN, 1)
  time.sleep(1)

  SendPIN=21

  GPIO.output(SendPIN, 0)
  time.sleep(0.5)
  GPIO.output(SendPIN, 1)
  time.sleep(1)

  GPIO.output(SendPIN, 0)
  time.sleep(0.5)
  GPIO.output(SendPIN, 1)
  time.sleep(1)

  GPIO.output(SendPIN, 0)
  time.sleep(0.5)
  GPIO.output(SendPIN, 1)
  time.sleep(1)




except KeyboardInterrupt:
    GPIO.output(19, 0)           # set port/pin value to 0/LOW/False
    GPIO.output(21, 0)           # set port/pin value to 0/LOW/False
    GPIO.output(23, 0)           # set port/pin value to 0/LOW/False
    GPIO.cleanup()              # Clean GPIO
    print ("Bye.")

