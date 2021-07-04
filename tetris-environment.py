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


class Tetris(gym.Env):
    def __init__(self):
        self.board = np.zeros((10, 40))

    def step(self, action):
        pass

    def reset(self):
        pass

    def render(self, render_mode="human"):
        pass

s = np.zeros((3, 3))
n = np.zeros((1, 1))
p = np.zeros((2, 2))
d = np.zeros((4, 4))

shape = Shape(s, n, p, d)
