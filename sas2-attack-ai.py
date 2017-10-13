from pymouse import PyMouseEvent
import pyscreenshot as ImageGrab
import cv2
import signal
import numpy as np
import sys

def signal_handler(signal, frame):
    cv2.destroyAllWindows()
    sys.exit(0)

def capture_images():
    print("Capturing images")
    frames = 50
    count = 0
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    x = botright[0] - topleft[0]
    y = botright[1] - topleft[1]
    writer = cv2.VideoWriter('output.avi', fourcc, 20.0, (x, y))
    if not writer.isOpened():
        print("Video could not be opened")

    while count <= frames:
        img = ImageGrab.grab(bbox=(topleft[0], topleft[1], botright[0], botright[1]))
        img_np = np.array(img)
        frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)
        print("Writing frame ", count)
        writer.write(frame)
        count += 1

    writer.release()
    sys.exit(0)

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
        capture_images()
        PyMouseEvent.stop(self)

signal.signal(signal.SIGINT, signal_handler)
captureRectangle = CaptureRectangle()
captureRectangle.run()
