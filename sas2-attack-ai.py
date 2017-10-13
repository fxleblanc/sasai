from pymouse import PyMouseEvent

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
        PyMouseEvent.stop(self)

captureRectangle = CaptureRectangle()
captureRectangle.run()
