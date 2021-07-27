import time
import tetris_environment
import tkinter

class Tetris(tetris_environment.Tetris):
    def __init__(self):
        super().__init__()

        self.window.bind("<Left>", self.left_keypress)
        self.window.bind("<Right>", self.right_keypress)
        self.window.bind("<Up>", self.up_keypress)
        self.window.bind("<Down>", self.down_keypress)

        self.key_pressed = 0
        self.sleep_time = 1
    
    def left_keypress(self, event):
        self.key_pressed = 2
    
    def right_keypress(self, event):
        self.key_pressed = 1

    def up_keypress(self, event):
        self.key_pressed = 3

    def down_keypress(self, event):
        self.key_pressed = 4

    def mainloop(self):
        self.step(self.key_pressed)
        self.render(ms=0)
        self.key_pressed = 0

        t0 = time.time()
        while time.time() - t0 < self.sleep_time:
            self.window.update()
                    

t = Tetris()

while not t.done:
    t.mainloop()


