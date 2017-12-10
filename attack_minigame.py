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
lock = threading.Lock()

# Lane Lock to prevent spamming in one direction at the detriment of other directions
lane_lock_delay = 0.3
toplock = threading.Lock()
midlock = threading.Lock()
botlock = threading.Lock()

def signal_handler(signal, frame):
    "Close everything with SIGINT"
    cv2.destroyAllWindows()
    sys.exit(0)

def top(x):
    delay = ((x - 325) / (500 - 325)) / 5
    print(x,delay)
    sleep(delay)
    toplock.acquire()
    lock.acquire()
    k.tap_key('Up')
    lock.release()
    sleep(lane_lock_delay)
    toplock.release()

def right(x):
    delay = ((x - 325) / (500 - 325)) / 5
    print(x,delay)
    sleep(delay)
    midlock.acquire()
    lock.acquire()
    k.tap_key('Right')
    lock.release()
    sleep(lane_lock_delay)
    midlock.release()

def down(x):
    delay = ((x - 325) / (500 - 325)) / 5
    print(x,delay)
    sleep(delay)
    botlock.acquire()
    lock.acquire()
    k.tap_key('Down')
    lock.release()
    sleep(lane_lock_delay)
    botlock.release()

def capture_image():

    # HSV Red bounds
    lower = (110, 100, 100)
    higher = (130, 255, 255)
    x = botright[0] - topleft[0]
    y = botright[1] - topleft[1]

    while True:
        # Get the image and transform it in a numpy array
        img = ImageGrab.grab(bbox=(topleft[0], topleft[1], botright[0], botright[1]))
        img_np = np.array(img)
        img_crop = img_np[150:500, 100:600]
        blurred = cv2.GaussianBlur(img_crop, (11, 11), 0)

        # Apply Gaussian blur and hsv color conversion
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        rgb = cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB)

        # Find a mask using the lower and higher bounds
        mask = cv2.inRange(hsv, lower, higher)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # Apply mask
        res = cv2.bitwise_and(hsv, hsv, mask = mask)

        # Find contours
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        if len(cnts) > 0:
            for contour in cnts:
                # Find coordinates and start threads
                ((x, y), radius) = cv2.minEnclosingCircle(contour)
                if x <= 500 and x >= 325 and y <= 180:
                    t = threading.Thread(name='thread_top', target=top, args=(x,))
                    t.setDaemon(True)
                    t.start()
                elif x <= 500 and x >= 325 and y > 180 and y < 260:
                    t = threading.Thread(name='thread_right', target=right, args=(x,))
                    t.setDaemon(True)
                    t.start()
                elif x <= 500 and x >= 325 and y >= 260:
                    t = threading.Thread(name='thread_down', target=down, args=(x,))
                    t.setDaemon(True)
                    t.start()


class CaptureRectangle(PyMouseEvent):
    def __init__(self):
        PyMouseEvent.__init__(self)
        self.clicks = 0

    def click(self, x, y, button, press):
        if button == 1:
            if press:
                print("Click")
                if self.clicks == 0:
                    print("Top left corner")
                    global topleft
                    topleft = (x, y)
                    self.clicks += 1
                elif self.clicks == 1:
                    print("Bottom Right corner")
                    global botright
                    botright = (x, y)
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
