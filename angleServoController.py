import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--local_ip', default='192.168.1.11', help='The ip of the local OSC')
parser.add_argument('--local_port', type=int, default=7110, help='The port the OSC server is listening to')
parser.add_argument('--ip', default='127.0.0.1', help='The ip of the remove OSC server')
parser.add_argument('--port', type=int, default=8001, help='The port the remote OSC server ')
parser.add_argument('--identifier', type=int, default=0, help='This is the identifier that will be sent to the visor')
parser.add_argument('--delta_time', type=float, default=0.05, help='The port the remote OSC server ')
args = parser.parse_args()


print 
print 'Identifier: %d' % args.identifier
print 'Listening to %s:%d' % (args.local_ip, args.local_port)
print 'Sending to %s:%d' % (args.ip, args.port)
print 'Sending to %f' % (args.delta_time)
print

import RPi.GPIO as GPIO
from OSC import OSCServer
from OSC import OSCClient, OSCMessage
import time
import sys

SERVO_MAX = 11.9
SERVO_MIN = 2.5
SERVO_MAX_ANGLE = 180.0
SERVO_DELTA_TIME = args.delta_time
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
p = GPIO.PWM(18, 50)

angle = 0
p.start(angle)

def duty(a):
  return (a / SERVO_MAX_ANGLE) * (SERVO_MAX - SERVO_MIN) + SERVO_MIN

def goto(end, s):
  global angle
  if abs(end - angle) < 1:
    return

  print "Moving from: ", angle, " to: ", end, " in: ", s, " s"

  init = angle * 1.0
  end = end * 1.0
  steps = s / SERVO_DELTA_TIME
  inc = abs(init - end) / steps
  for i in range(int(steps) + 1):
    pos = inc * i

    if init > end:
      a = init - pos
    else:
      a = init + pos
    
    if a < 0:
      a = 0
    if a > SERVO_MAX_ANGLE:
      a = SERVO_MAX_ANGLE

    angle = a
    try:
      client.send( OSCMessage("/angle", [args.identifier, int(angle), 1] ) )
    except:
      pass
    p.ChangeDutyCycle(duty(a))
    time.sleep(SERVO_DELTA_TIME)


client = OSCClient()
client.connect( (args.ip, args.port) )

server = OSCServer( (args.local_ip, args.local_port) )
server.timeout = 0
run = True

def handle_timeout(self):
  self.timed_out = True

import types
server.handle_timeout = types.MethodType(handle_timeout, server)

def servo_callback(path, tags, args, source):
  goto(args[0], args[1])

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
    try:
      client.send( OSCMessage("/angle", [args.identifier, int(angle), 0] ) )
    except:
      pass
  print "quiting..."
except KeyboardInterrupt:
  print "quiting..."


server.close()
p.stop()
GPIO.cleanup()
