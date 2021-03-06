import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--ip', default='127.0.0.1', help='The ip of the OSC server')
parser.add_argument('--port', type=int, default=8001, help='The port the OSC server is listening on')
parser.add_argument('--identifier', type=int, default=0, help='This is the identifier that will be sent to the visor')
parser.add_argument('--samples', type=int, default=1000, help='Number of samples')
args = parser.parse_args()


import numpy as np
import cv2
import time
from OSC import OSCClient, OSCMessage


client = OSCClient()
client.connect( (args.ip, args.port) )

cap = cv2.VideoCapture(0)

width, height = cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH), cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

print 
print 'Identifier: %d' % args.identifier
print 'Captured image size: %d, %d' % (width, height)
print 'Sending to %s:%d' % (args.ip, args.port)
print 'Samples %d' % (args.samples)
print

def sample(colorset, _size):
    idx_x = np.random.randint(colorset.shape[0], size=_size)
    idx_y = np.random.randint(colorset.shape[1], size=_size)
    return colorset[idx_x, idx_y, :]

try:
  while(True):
      ret, frame = cap.read()
      if not ret:
          continue

      sampling_pixels = sample(frame, args.samples)
      color = np.mean(sampling_pixels, axis=0)
      
      try:
        client.send( OSCMessage("/camera", [args.identifier, int(color[2]), int(color[1]), int(color[0])] ) )
      except:
        pass
      time.sleep(1.0 / 30.0)

except KeyboardInterrupt:
  print "quitting..."
finally:
  print 'Releasing cam'
  cap.release()