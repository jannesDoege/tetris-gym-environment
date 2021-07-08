import gym
import numpy as np



#jblock = Shape()
#sblock = Shape()
#zblock = Shape()
#tblock = Shape()
#iblock = Shape()
#sqrblock = Shape()

class Tetris(gym.Env):
    TETRAMINOS = [
        [(1, 1), (1, 0), (0, 1), (1, 0)], # lblock
        #jblock 
        #sblock 
        #zblock 
        #tblock 
        #iblock 
        #sqrblock

    ]

    def __init__(self):
        self.board = np.zeros((10, 40))
        self.blocks_buf = [i for i in Tetris.TETRAMINOS]
        self.blocks_buf.shuffle()
        self.step_idx = 0
        self.current_block = None
        self.block_count = 0
        
    def step(self, action):
        self.step_idx += 1
        
        if self.step_idx % len(self.blocks) == 0:
            self.blocks_buf = [i for i in Tetris.TETRAMINOS]
            self.blocks_buf = [i for i in self.blocks]
        
        if not self.free_fall:
            self.block_count += 1
            self.current_block = self.blocks_buf.pop(0)
        else:
            for i in range(0, self.block_count -1 ):
                fall = False
                for j in self.board:
                    if j == i && # check below
        
        # if line clear
        for i in range(0, self.block_count -1 ):
                fall = False
                for j in self.board:
                    if j == i && # check below

        # every block has its own number
        # this is used to get sticky line clears


    def reset(self):
        self.board = np.zeros((10, 40))
        self.blocks = [lblock, jblock, sblock, zblock, tblock, iblock, sqrblock]
        self.blocks_buf = [i for i in self.blocks]
        self.blocks_buf.shuffle()
        self.step_idx = 0
        self.free_fall = False
        self.current_block = None

    def render(self, render_mode="human"):
        pass
    