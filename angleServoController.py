import RPi.GPIO as GPIO
from OSC import OSCServer
import time
import sys

SERVO_MAX = 11.9
SERVO_MIN = 2.5
SERVO_ANGLE = 180.0

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
p = GPIO.PWM(18, 50)
p.start(5)

def angle(a):
  return (a / SERVO_ANGLE) * (SERVO_MAX - SERVO_MIN) + SERVO_MIN

def goto(init, end, s):
  p.ChangeDutyCycle(angle(init))
  steps = s / 0.05
  inc = abs(init - end) / steps
  for i in range(int(steps)):
    pos = inc * i
    if init > end:
      p.ChangeDutyCycle(angle(init - pos))
    else:
      p.ChangeDutyCycle(angle(init + pos))
    time.sleep(0.05)


server = OSCServer( ("192.168.1.52", 7110) )
server.timeout = 0
run = True

def handle_timeout(self):
  self.timed_out = True

import types
server.handle_timeout = types.MethodType(handle_timeout, server)

def servo_callback(path, tags, args, source):
  print ("Moving from: ", args[0], " to: ", args[1], " in: ", args[2], " s")
  goto(args[0], args[1], args[2])

def quit_callback(path, tags, args, source):
  global run
  run = False

server.addMsgHandler( "/servo", servo_callback )
server.addMsgHandler( "/quit", quit_callback )

def each_frame():
  server.timed_out = False
  while not server.timed_out:
    server.handle_request()

try:
  while run:
    time.sleep(0.3)
    each_frame()
  print "quiting..."
except KeyboardInterrupt:
  print "quiting..."


server.close()
p.stop()
GPIO.cleanup()
