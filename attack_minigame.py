"""Python module to play the strength minigame"""
import sys
import threading
from time import sleep
import signal

from pymouse import PyMouseEvent
from pykeyboard import PyKeyboard
import pyscreenshot as ImageGrab
import cv2
import numpy as np

k = PyKeyboard()
# Lock for each delay
LOCK = threading.Lock()

# Lane Lock to prevent spamming in one direction at the detriment of other directions
LANE_LOCK_DELAY = 0.3
TOPLOCK = threading.Lock()
MIDLOCK = threading.Lock()
BOTLOCK = threading.Lock()

def signal_handler():
    "Close everything with SIGINT"
    cv2.destroyAllWindows()
    sys.exit(0)

def top(pos_x):
    """Top attack"""
    delay = ((pos_x - 325) / (500 - 325)) / 5
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
    delay = ((pos_x - 325) / (500 - 325)) / 5
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
    delay = ((pos_x - 325) / (500 - 325)) / 5
    print(pos_x, delay)
    sleep(delay)
    BOTLOCK.acquire()
    LOCK.acquire()
    k.tap_key('Down')
    LOCK.release()
    sleep(LANE_LOCK_DELAY)
    BOTLOCK.release()

def capture_image():
    """Capture image, detect apples and launch thread for the appropriate direction"""

    # HSV Red bounds
    lower = (110, 100, 100)
    higher = (130, 255, 255)
    pos_x = botright[0] - topleft[0]
    pos_y = botright[1] - topleft[1]

    while True:
        # Get the image and transform it in a numpy array
        img = ImageGrab.grab(bbox=(topleft[0], topleft[1], botright[0], botright[1]))
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
        cnts_len = len(cnts)
        if cnts_len > 0:
            for contour in cnts:
                # Find coordinates and start threads
                ((pos_x, pos_y)) = cv2.minEnclosingCircle(contour)
                if pos_x <= 500 and pos_x >= 325 and pos_y <= 180:
                    action_thread = threading.Thread(name='thread_top', target=top, args=(pos_x,))
                    action_thread.setDaemon(True)
                    action_thread.start()
                elif pos_x <= 500 and pos_x >= 325 and pos_y > 180 and pos_y < 260:
                    action_thread = threading.Thread(name='thread_right', target=right, args=(pos_x,))
                    action_thread.setDaemon(True)
                    action_thread.start()
                elif pos_x <= 500 and pos_x >= 325 and pos_y >= 260:
                    action_thread = threading.Thread(name='thread_down', target=down, args=(pos_x,))
                    action_thread.setDaemon(True)
                    action_thread.start()


class CaptureRectangle(PyMouseEvent):
    def __init__(self):
        PyMouseEvent.__init__(self)
        self.clicks = 0

    def click(self, pos_x, y, button, press):
        if button == 1:
            if press:
                print("Click")
                if self.clicks == 0:
                    print("Top left corner")
                    global topleft
                    topleft = (pos_x, y)
                    self.clicks += 1
                elif self.clicks == 1:
                    print("Bottom Right corner")
                    global botright
                    botright = (pos_x, y)
                    self.stop()
        else:
            self.stop()

    def stop(self):
        print(topleft[0], topleft[1])
        print(botright[0], botright[1])
        capture_image()
        PyMouseEvent.stop(self)

signal.signal(signal.SIGINT, signal_handler)
captureRectangle = CaptureRectangle()
captureRectangle.run()
