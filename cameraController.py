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

COLOR_SIZE = 100

cap = cv2.VideoCapture(args.capture)
identifier = str(uuid.uuid4()) if not args.identifier else args.identifier

width, height = cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH), cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
center_roi_x, center_roi_y = int(width / 2 - 100 / 2), int(height / 2 - 100 / 2)
pos_roi_x, pos_roi_y = int(width + (width/2-100/2)), int(height/3-100/2)
pos_color_x, pos_color_y = width + (width/2 - COLOR_SIZE / 2), (height / 3 * 2 - COLOR_SIZE/2)
n_pixels = width * height

black_image = np.zeros((height, width * 2, 3), np.uint8)
color_image = np.zeros((COLOR_SIZE, COLOR_SIZE, 3), np.uint8)
end_color_y = pos_color_y + COLOR_SIZE

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

      m_roi = frame[center_roi_y : center_roi_y + 100, center_roi_x : center_roi_x + 100]
      sampling_pixels = sample(m_roi, 1000)
      color = np.mean(sampling_pixels, axis=0)
      
      luminance = (0.2126 * color[2] + 0.7152 * color[1] + 0.0722 * color[0]) / 255
      client.send( OSCMessage("/camera", [identifier, color[2], color[1], color[0], luminance] ) )
      time.sleep(1.0 / 30.0)

except KeyboardInterrupt:
  print "quitting..."
finally:
  print 'Releasing cam'
  cap.release()