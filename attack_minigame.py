"""Python module to play the strength minigame"""
import sys
import threading
from time import sleep
import signal

from pykeyboard import PyKeyboard
import pyscreenshot as ImageGrab
import cv2
import numpy as np
from capture_rectangle import CaptureRectangle

k = PyKeyboard()
# Lock for each delay
LOCK = threading.Lock()

# Lane Lock to prevent spamming in one direction at the detriment of other directions
LANE_LOCK_DELAY = 0.3
TOPLOCK = threading.Lock()
MIDLOCK = threading.Lock()
BOTLOCK = threading.Lock()

def start_actions_from_contours(cnts):
    """Start action threads from contours positions"""
    cnts_len = len(cnts)

    # Bounds of contour capture
    right_bound = 500
    if cnts_len > 0:
        for contour in cnts:
            # Find coordinates and start threads
            circle = cv2.minEnclosingCircle(contour)
            cnt_pos_x = circle[0][0]
            cnt_pos_y = circle[0][1]
            if cnt_pos_x <= right_bound and cnt_pos_x >= 325 and cnt_pos_y <= 180:
                action_thread = threading.Thread(name='thread_top',
                                                 target=top, args=(cnt_pos_x,))
                action_thread.setDaemon(True)
                action_thread.start()
            elif (cnt_pos_x <= right_bound and cnt_pos_x >= 325 and
                  cnt_pos_y > 180 and cnt_pos_y < 260):
                action_thread = threading.Thread(name='thread_right',
                                                 target=right, args=(cnt_pos_x,))
                action_thread.setDaemon(True)
                action_thread.start()
            elif cnt_pos_x <= right_bound and cnt_pos_x >= 325 and cnt_pos_y >= 260:
                action_thread = threading.Thread(name='thread_down',
                                                 target=down, args=(cnt_pos_x,))
                action_thread.setDaemon(True)
                action_thread.start()

def signal_handler():
    "Close everything with SIGINT"
    cv2.destroyAllWindows()
    sys.exit(0)

def top(pos_x):
    """Top attack"""
    delay = 0.25
    print(pos_x, delay)
    sleep(delay)
    TOPLOCK.acquire()
    LOCK.acquire()
    k.tap_key('Up')
    LOCK.release()
    sleep(LANE_LOCK_DELAY)
    TOPLOCK.release()

def right(pos_x):
    """Right attack"""
    delay = 0.1
    print(pos_x, delay)
    sleep(delay)
    MIDLOCK.acquire()
    LOCK.acquire()
    k.tap_key('Right')
    LOCK.release()
    sleep(LANE_LOCK_DELAY)
    MIDLOCK.release()

def down(pos_x):
    """Down attack"""
    delay = 0.1
    print(pos_x, delay)
    sleep(delay)
    BOTLOCK.acquire()
    LOCK.acquire()
    k.tap_key('Down')
    LOCK.release()
    sleep(LANE_LOCK_DELAY)
    BOTLOCK.release()

def capture_image(capture_rectangle):
    """Capture image, detect apples and launch thread for the appropriate direction"""

    # HSV Red bounds
    lower = (110, 100, 100)
    higher = (130, 255, 255)

    while True:
        # Get the image and transform it in a numpy array
        img = ImageGrab.grab(bbox=(capture_rectangle.topleft[0],
                                   capture_rectangle.topleft[1],
                                   capture_rectangle.botright[0],
                                   capture_rectangle.botright[1]))
        img_np = np.array(img)
        img_crop = img_np[150:500, 100:600]
        blurred = cv2.GaussianBlur(img_crop, (11, 11), 0)

        # Apply Gaussian blur and hsv color conversion
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # Find a mask using the lower and higher bounds
        mask = cv2.inRange(hsv, lower, higher)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # Find contours
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        start_actions_from_contours(cnts)


signal.signal(signal.SIGINT, signal_handler)
CAPTURE_RECTANGLE = CaptureRectangle(capture_image)
CAPTURE_RECTANGLE.run()
