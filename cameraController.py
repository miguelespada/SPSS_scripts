import numpy as np
import cv2
import argparse
import uuid
import time
from OSC import OSCClient, OSCMessage

parser = argparse.ArgumentParser()
parser.add_argument('--ip', default='127.0.0.1', help='The ip of the OSC server')
parser.add_argument('--port', type=int, default=8000, help='The port the OSC server is listening on')
parser.add_argument('--capture', type=int, default=0, help='The cam identifier')
parser.add_argument('--show', type=int, default=0, help='Indicates if the frame is shown')
parser.add_argument('--roi', type=int, default=100, help='Indicates the ROI size in pixels')
parser.add_argument('--sampling', type=float, default=0.0, help='Sampling percentage (0..1) to obtain from ROI')
parser.add_argument('--delay', type=float, default=0, help='Delay time between frames')
parser.add_argument('--send', type=int, default=1, help='Indicates if it should send the color')
parser.add_argument('--identifier', type=str, default='', help='This is the identifier that will be sent to the visor')
parser.add_argument('--show_msg', type=int, default=0)
parser.add_argument('--servo', type=int, default=0, help='Indicates if the servo should be controlled')
args = parser.parse_args()

client = OSCClient()
client.connect( ("192.168.1.33", 8000) )

COLOR_SIZE = 100

cap = cv2.VideoCapture(args.capture)
identifier = str(uuid.uuid4()) if not args.identifier else args.identifier

width, height = cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH), cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
center_roi_x, center_roi_y = int(width / 2 - args.roi / 2), int(height / 2 - args.roi / 2)
pos_roi_x, pos_roi_y = int(width + (width/2-args.roi/2)), int(height/3-args.roi/2)
pos_color_x, pos_color_y = width + (width/2 - COLOR_SIZE / 2), (height / 3 * 2 - COLOR_SIZE/2)
n_pixels = width * height

black_image = np.zeros((height, width * 2, 3), np.uint8)
color_image = np.zeros((COLOR_SIZE, COLOR_SIZE, 3), np.uint8)
end_color_y = pos_color_y + COLOR_SIZE

print 
print 'Identifier: ' + identifier
print 'Captured image size: %d, %d' % (width, height)
print 'ROI size: %d, %d' % (args.roi, args.roi)
print 'Sending to %s:%d' % (args.ip, args.port)
print 'Controlling servo: %s' % ('yes' if control_servo else 'no')
print 'Showing results: %s' % ('yes' if args.show else 'no')
print 'Pixels in sent sampling: %d / %d' % (sampling, n_pixels)
if args.show:
    print 'Pixels in the shown samples: %s ' % repr(shown_sample)
print 'Delay: %s' % ('no' if args.delay == 0.0 else str(args.delay * 1000) + 'ms')
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

      m_roi = frame[center_roi_y : center_roi_y + args.roi, center_roi_x : center_roi_x + args.roi]
      sampling_pixels = sample(m_roi, 1000)
      color = np.mean(sampling_pixels, axis=0)
      
      luminance = (0.2126 * color[2] + 0.7152 * color[1] + 0.0722 * color[0]) / 255
      client.send( OSCMessage("/camera", [identifier, color[2], color[1], color[0], luminance] ) )
      time.sleep(0.05)

except KeyboardInterrupt:
  running = False
finally:
  print 'Releasing cam'
  cap.release()