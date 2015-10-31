import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--ip', default='127.0.0.1', help='The ip of the OSC server')
parser.add_argument('--port', type=int, default=8000, help='The port the OSC server is listening on')
parser.add_argument('--identifier', type=str, default='', help='This is the identifier that will be sent to the visor')
args = parser.parse_args()


import numpy as np
import cv2
import uuid
import time
from OSC import OSCClient, OSCMessage


client = OSCClient()
client.connect( (args.ip, args.port) )

cap = cv2.VideoCapture(0)

identifier = str(uuid.uuid4()) if not args.identifier else args.identifier
width, height = cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH), cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)


print 
print 'Identifier: ' + identifier
print 'Captured image size: %d, %d' % (width, height)
print 'Sending to %s:%d' % (args.ip, args.port)
print

def sample(colorset, _size):
    idx_x = np.random.randint(colorset.shape[0], size=_size)
    idx_y = np.random.randint(colorset.shape[1], size=_size)
    return colorset[idx_y, idx_x, :]

try:
  while(True):
      ret, frame = cap.read()
      if not ret:
          continue

      sampling_pixels = sample(frame, 1000)
      color = np.mean(sampling_pixels, axis=0)
      
      luminance = (0.2126 * color[2] + 0.7152 * color[1] + 0.0722 * color[0])
      try:
        client.send( OSCMessage("/camera", [identifier, int(color[2]), int(color[1]), int(color[0]), int(luminance)] ) )
      except:
        pass
      time.sleep(1.0 / 30.0)

except KeyboardInterrupt:
  print "quitting..."
finally:
  print 'Releasing cam'
  cap.release()