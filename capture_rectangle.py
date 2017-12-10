"""
Capture rectangle module.
Captures a rectangle in your screen and invokes a method that uses those coordinates
"""
import sys

from pymouse import PyMouseEvent

class CaptureRectangle(PyMouseEvent):
    """Identify the corners that capture_image is going to use in order to deal with the image"""
    def __init__(self, stop_action):
        PyMouseEvent.__init__(self)
        self.clicks = 0
        self.topleft = (0, 0)
        self.botright = (0, 0)
        self.stop_action = stop_action

    def click(self, x, y, button, press):
        if button == 1:
            if press:
                print("Click")
                if self.clicks == 0:
                    print("Top left corner")
                    self.topleft = (x, y)
                    self.clicks += 1
                elif self.clicks == 1:
                    print("Bottom Right corner")
                    self.botright = (x, y)
                    self.stop()
        else:
            self.stop()

    def stop(self):
        print(self.topleft[0], self.topleft[1])
        print(self.botright[0], self.botright[1])
        self.stop_action(self)
        PyMouseEvent.stop(self)

def print_coordinates(capture_rectangle):
    """Print coordinates of a capture rectangle"""
    with open("coordinates.txt", "w") as file:
        file.write(str(capture_rectangle.topleft[0]) + "\n")
        file.write(str(capture_rectangle.topleft[1]) + "\n")
        file.write(str(capture_rectangle.botright[0]) + "\n")
        file.write(str(capture_rectangle.botright[1]) + "\n")
    sys.exit(0)

if __name__ == "__main__":
    CAPTURE_RECTANGLE = CaptureRectangle(print_coordinates)
    CAPTURE_RECTANGLE.run()
