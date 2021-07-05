import gym
import numpy as np

class Shape:
    def __init__(self, rot0: np.ndarray, rot90: np.ndarray, rot180: np.ndarray, rot270: np.ndarray):
        self.rot = 0
        self.shapes = {
            "rot0": rot0,
            "rot90": rot90,
            "rot180": rot180,
            "rot270": rot270
        }

        self.shape = self.shapes["rot0"]
    
    def rotate(self, direct:int):
        self.rot += direct * 90
        if self.rot > 270:
            self.rot = 0
        if self.rot < 0:
            self.rot = 270
        self.shape = self.shapes["rot" + str(self.rot)]

lblock = Shape()
jblock = Shape()
sblock = Shape()
zblock = Shape()
tblock = Shape()
iblock = Shape()
sqrblock = Shape()

class Tetris(gym.Env):
    def __init__(self):
        self.board = np.zeros((10, 40))
        self.blocks = [lblock, jblock, sblock, zblock, tblock, iblock, sqrblock]
        self.blocks_buf = [i for i in self.blocks]
        self.blocks_buf.shuffle()
        self.step_idx = 0
        self.free_fall = False
        self.current_block = None
        
    def step(self, action):
        self.step_idx += 1
        
        if self.step_idx % len(self.blocks) == 0:
            self.blocks = [lblock, jblock, sblock, zblock, tblock, iblock, sqrblock]
            self.blocks_buf = [i for i in self.blocks]
        
        if not self.free_fall:
            self.current_block = self.blocks_buf.pop(0)



    def reset(self):
        pass

    def render(self, render_mode="human"):
        pass
    