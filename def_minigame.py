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


TOPLEFT_X = 400
TOPLEFT_Y = 287
BOTRIGHT_X = 1119
BOTRIGHT_Y = 886

# Lane Lock to prevent spamming in one direction at the detriment of other directions
LANE_LOCK_DELAY = 0.05#30
SPEED = 520 #px/s
STAR_SPEED = 444 #px/s
ATTACK_POS = 260 #px

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

def start_actions_from_contours(cnts,apple):
  """Start action threads from contours positions"""
  cnts_len = len(cnts)

  # Bounds of contour capture
  right_bound = 500
  left_bound = 350
  top_bound = 200

  if cnts_len > 0:
    for contour in cnts:
      # Find coordinates and start threads
      circle = cv2.minEnclosingCircle(contour)
      cnt_pos_x = circle[0][0]
      cnt_pos_y = circle[0][1]
      if apple:
        # if cnt_pos_x <= right_bound and cnt_pos_x >= left_bound and cnt_pos_y <= 190:
          action_thread = threading.Thread(name='move_mouse',
                           target=move_mouse, args=(cnt_pos_x,cnt_pos_y))
          action_thread.setDaemon(True)
          action_thread.start()
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
      else:
        if cnt_pos_y < top_bound:
          action_thread = threading.Thread(name='thread_left',
                           target=left, args=(cnt_pos_x,cnt_pos_y))
          action_thread.setDaemon(True)
          action_thread.start()

def signal_handler():
  "Close everything with SIGINT"
  cv2.destroyAllWindows()
  sys.exit(0)
  
def move_mouse(pos_x,pos_y,):
  delay = math.sqrt((pos_x - CENTER_X) ** 2 + (pos_y - CENTER_Y) ** 2 ) / SPEED - 0.3
  if delay > 0.05:
    m_x = int(pos_x + TOPLEFT_X)
    m_y = int(pos_y + TOPLEFT_Y)
    print('move', int(m_x), int(m_y), round(delay,3))
    sleep(delay)
    MOUSELOCK.acquire()
    # LOCK.acquire()
    # m.move(m_x, m_y)
    win32api.SetCursorPos((m_x, m_y))
    # LOCK.release()
    # sleep(LANE_LOCK_DELAY)
    MOUSELOCK.release()

def capture_image(capture_rectangle):
  """Capture image, detect apples and launch thread for the appropriate direction"""

  # HSV Red bounds
  APPLE_lower = (116, 180, 143)#(110, 100, 100)
  APPLE_higher = (126, 213, 195)#(130, 255, 255)
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
    #cv2.imshow('contours', hsv)

    # Find a mask using the APPLE_lower and APPLE_higher bounds
    mask = cv2.inRange(hsv, APPLE_lower, APPLE_higher)
    mask = cv2.erode(mask, None, iterations=2)
    #mask = cv2.dilate(mask, None, iterations=2)

    #cv2.imshow('contours', mask)
    # Find contours
    _, cnts, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)#[-2]
    
    #cv2.drawContours( mask, cnts, -1, (255,0,0), 3, cv2.LINE_AA, hierarchy, 1)
    # cv2.imshow('contours', mask)
    # cv2.waitKey()

    start_actions_from_contours(cnts,True)
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