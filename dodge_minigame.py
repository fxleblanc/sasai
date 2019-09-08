"""Python module to play the strength minigame"""
import sys
import threading
from time import sleep
import signal
import os.path

from pynput import keyboard
import win32api
import math


from pykeyboard import PyKeyboard
from pymouse import PyMouse

import pyscreenshot as ImageGrab
import cv2
import numpy as np
from capture_rectangle import CaptureRectangle

k = PyKeyboard()
m = PyMouse()
# Lock for each delay
LOCK = threading.Lock()

LOOP = True


TOPLEFT_X = 750
TOPLEFT_Y = 530
BOTRIGHT_X = 1000
BOTRIGHT_Y = 645

# Lane Lock to prevent spamming in one direction at the detriment of other directions
LANE_LOCK_DELAY = 0.05#30
SPEED = 520 #px/s
STAR_SPEED = 444 #px/s
ATTACK_POS = 260 #px

AT_UP = False
AT_DW = False
AT_SI = False

CENTER_X = 399
CENTER_Y = 309

BACK_ATTACK_POS = 310 #px
TOPLOCK = threading.Lock()
MIDLOCK = threading.Lock()
BOTLOCK = threading.Lock()
LEFTLOCK = threading.Lock()
MOUSELOCK = threading.Lock()

# Capture delay timer
CAPTURE_DELAY = 0.000005

def start_actions_from_contours(cnts):
  """Start action threads from contours positions"""
  cnts_len = len(cnts)

  # Bounds of contour capture
  right_bound = 500
  left_bound = 350
  top_bound = 200

  if cnts_len > 0:
    for contour in cnts:
      # Find coordinates and start threads
      # (cnt_pos_x,cnt_pos_y),radius = cv2.minEnclosingCircle(contour)
      # cnt_pos_x = circle[0][0]
      # cnt_pos_y = circle[0][1]
	  
		try:
		  if len(contour) > 5:
			  ellipse = cv2.fitEllipse(contour)
			  x1 = int(ellipse[0][0])
			  y1 = int(ellipse[0][1])
			  x2 = int(ellipse[1][0])
			  y2 = int(ellipse[1][1])
			  angle = int(ellipse[0][1])
			  
			  xx = x1-x2
			  yy = y1-y2
			  
			  # print(int(x1-x2), int(y1-y2), int(angle))
			  if angle >= 21 and angle <= 33 and xx >= 180 and xx <= 219:
				  action_thread = threading.Thread(name='thread_top', target=at_top, args=(xx,angle))
				  action_thread.setDaemon(True)
				  action_thread.start()
			  elif angle >= 41 and angle <= 52 and xx >= 141 and xx <= 148:
				  action_thread = threading.Thread(name='thread_side', target=at_side, args=(xx,angle))
				  action_thread.setDaemon(True)
				  action_thread.start()
			  elif angle >= 48 and angle <= 87 and xx >= 82 and xx <= 86:
				  action_thread = threading.Thread(name='thread_down', target=at_down, args=(xx,angle))
				  action_thread.setDaemon(True)
				  action_thread.start()
			  # elif angle >= 47 and angle <= 49:
				# print('P')
			  # else:
				# # print(angle)
				# print(int(x1-x2), int(y1-y2), int(angle))
				
				# print(ellipse)
				# print(x1,y1,x2,y2)
				# if cnt_pos_x <= right_bound and cnt_pos_x >= left_bound and cnt_pos_y <= 190:
				  # action_thread = threading.Thread(name='move_mouse',
								   # target=move_mouse, args=(cnt_pos_x,cnt_pos_y))
				  # action_thread.setDaemon(True)
				  # action_thread.start()
				# elif (cnt_pos_x <= right_bound and cnt_pos_x >= left_bound and
					# cnt_pos_y > 190 and cnt_pos_y < 260):
				  # action_thread = threading.Thread(name='thread_right',
								   # target=right, args=(cnt_pos_x,cnt_pos_y))
				  # action_thread.setDaemon(True)
				  # action_thread.start()
				# elif cnt_pos_x <= right_bound and cnt_pos_x >= left_bound and cnt_pos_y >= 260:
				  # action_thread = threading.Thread(name='thread_down',
								   # target=down, args=(cnt_pos_x,cnt_pos_y))
				  # action_thread.setDaemon(True)
				  # action_thread.start()
		except cv2.error as e:
			 print('err2')

def signal_handler():
  "Close everything with SIGINT"
  cv2.destroyAllWindows()
  sys.exit(0)
  

def at_top(xx,angle):
  """Top attack"""
  if xx == 200 or ((xx == 203 or xx == 204 or xx == 206) and angle == 29) or ((xx == 207 or xx == 206) and angle == 28)or ((xx == 205) and angle == 26):
	delay = 0.3
  elif xx == 199:
	delay = 0.5
  else:
	delay = 0.4
  print('Top', xx, angle, round(delay,3))
  sleep(delay)
  TOPLOCK.acquire()
  LOCK.acquire()
  k.tap_key(k.left_key)
  LOCK.release()
  sleep(LANE_LOCK_DELAY)
  TOPLOCK.release()

def at_down(xx,angle):

  if (xx == 83 or angle == 85) and angle <=74:
	delay = 0.55
  else:
	delay = 0.4
	# if xx == 85:
		# delay = 0.5
	# else:
		# if angle == 72 or angle == 74
			# delay = 0.45
		# else:
			# delay = 0.45
  print('Down', xx, angle, round(delay,3))
  sleep(delay)
  BOTLOCK.acquire()
  LOCK.acquire()
  k.tap_key(k.up_key)
  LOCK.release()
  sleep(LANE_LOCK_DELAY)
  BOTLOCK.release()
  
def at_side(xx,angle):
  """side attack"""
  if xx < 144:
	delay = 0.6
  elif xx >= 147 or (xx == 145 and angle == 49)or (xx == 144 and angle == 52):
	delay = 0.45
  else:
	delay = 0.55
  print('Side', xx, angle, round(delay,3))
  sleep(delay)
  LEFTLOCK.acquire()
  LOCK.acquire()
  k.tap_key(k.down_key)
  LOCK.release()
  sleep(LANE_LOCK_DELAY)
  LEFTLOCK.release()

def capture_image(capture_rectangle):
  """Capture image, detect apples and launch thread for the appropriate direction"""

  # HSV Red bounds
  HAT_lower = (130, 20, 180)
  HAT_higher = (140, 30, 200)
  # HAT_lower = (130, 20, 180)
  # HAT_higher = (140, 30, 200)
  # HSV Red bounds
  lower = (0, 100, 210)#(92, 160, 250)
  higher = (115, 255, 255)

  while LOOP:
    # Get the image and transform it in a numpy array
    img = ImageGrab.grab(bbox=(capture_rectangle.topleft[0],
                   capture_rectangle.topleft[1],
                   capture_rectangle.botright[0],
                   capture_rectangle.botright[1]))
    img_np = np.array(img)

    # blurred = cv2.GaussianBlur(img_np, (11, 11), 0)

    #rand_name = generate_random_string(5,15)
    #saveas= os.path.join('.\\', rand_name + '.png')
    #img.save("screen.bmp", "BMP")

    # Apply Gaussian blur and hsv color conversion
    hsv = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)
    # cv2.imshow('contours', hsv)

    # Find a mask using the APPLE_lower and APPLE_higher bounds
    mask = cv2.inRange(hsv, HAT_lower, HAT_higher)
    #mask = cv2.erode(mask, None, iterations=2)
    #mask = cv2.dilate(mask, None, iterations=2)

    # cv2.imshow('contours', mask)
    # Find contours
    _, cnts, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)#[-2]
    
    #cv2.drawContours( mask, cnts, -1, (255,0,0), 3, cv2.LINE_AA, hierarchy, 1)
    #cv2.imshow('contours', mask)
    #cv2.waitKey()

    start_actions_from_contours(cnts)
    #sleep(CAPTURE_DELAY)
  signal_handler()
  return True
  
def kb_work():
  # Collect events until released
  with keyboard.Listener(
        on_press=on_press) as listener:
    listener.join()

def on_press(key):
    try:
      if key.char == 's':
        print('alphanumeric key {0} pressed'.format(key.char))
        global LOOP
        LOOP = False
    except AttributeError:
         print('special key {0} pressed'.format(key))

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False


signal.signal(signal.SIGINT, signal_handler)
if __name__ == "__main__":
  CAPTURE_RECTANGLE = CaptureRectangle(capture_image)
  CAPTURE_RECTANGLE.topleft = (int(TOPLEFT_X), int(TOPLEFT_Y))
  CAPTURE_RECTANGLE.botright = (int(BOTRIGHT_X), int(BOTRIGHT_Y))
  print('start capture_image()')
  
  # action_thread = threading.Thread(name='thread_keyboard', target=kb_work)
  # action_thread.setDaemon(True)
  # action_thread.start()

  capture_image(CAPTURE_RECTANGLE)
"""
  if os.path.isfile("coordinates.txt"):
    print("Using coordinates.txt")
    with open("coordinates.txt", "r") as file:
      CAPTURE_RECTANGLE = CaptureRectangle(capture_image)
      TOPLEFT_X = file.readline()
      TOPLEFT_Y = file.readline()
      BOTRIGHT_X = file.readline()
      BOTRIGHT_Y = file.readline()
      CAPTURE_RECTANGLE.topleft = (int(TOPLEFT_X), int(TOPLEFT_Y))
      CAPTURE_RECTANGLE.botright = (int(BOTRIGHT_X), int(BOTRIGHT_Y))
      print('start capture_image()')
      capture_image(CAPTURE_RECTANGLE)
  else:
    CAPTURE_RECTANGLE = CaptureRectangle(capture_image)
    CAPTURE_RECTANGLE.run()
"""

def find_contour_center(self, cnt):
    """
    finds the center of a contour using a bounding circle.
    """
    (x,y), r = cv2.minEnclosingCircle(cnt)
    center = (int(x), int(y))
    return center