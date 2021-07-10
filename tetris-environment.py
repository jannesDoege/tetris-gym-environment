import gym
import numpy as np
import random

from numpy.core.einsumfunc import _einsum_dispatcher

class Tetris(gym.Env):
    WIDTH = 10
    HEIGHT = 40
    
    TETRAMINOS = [
        [(0,0), (0,1), (1,0), (2,0)], # lblock
        [(0,0), (0,1), (1,1), (2,1)], # jblock 
        [(0,1), (1,0), (1,1), (2,0)], # sblock 
        [(0,0), (1,0), (1,1), (2,1)], # zblock 
        [(0,0), (1,0), (1,1), (2,0)], # tblock 
        [(0,0), (1,0), (2,0), (3,0)], # iblock 
        [(0,0), (0,1), (1,0), (1,1)]  # sqrblock
    ]

    def __init__(self):
        self.board = np.zeros((Tetris.WIDTH, Tetris.HEIGHT))
        self.blocks_buf = [i for i in Tetris.TETRAMINOS]
        self.blocks_buf = random.shuffle(self.blocks_buf)
        self.step_idx = 0
        self.current_block = None
        self.block_count = 0
        self.rewards = [0, 1, 4, 8, 16]
        self.free_fall = True

        # TODO observation_space
        # TODO action_space

    def step(self, action):
        reward = 0.0
        cleared_lines = 0

        # TODO put blocks in the game
        # TODO action (move left, right and rotate left, right)

        self.step_idx += 1

        if self.step_idx % len(Tetris.TETRAMINOS) == 0:
            self.blocks_buf = [i for i in Tetris.TETRAMINOS]
        
        if not self.free_fall:
            self.block_count += 1
            self.current_block = self.blocks_buf.pop(0)

        else:
            for i in range(1, self.block_count+1):
                fall = None
                for j in self.board:
                    for n, k in enumerate(j):
                        # check if it is block and if there is not block below
                        if k == i and j[int(n)-1] == 0:
                            fall = True
                        else: fall = False
                # do sticky fall
                if fall:
                    for idx, column in enumerate(self.board):
                        for n, num in enumerate(column):
                            if num == i:
                                self.board[idx][int(n)] = 0.0
                                self.board[idx][int(n-1)] = i
                
                if i == self.block_count and fall:
                    self.free_fall = True
                else:
                    self.free_fall = False

        # set all values to zero if line is to clear
        board_as_rows = np.reshape(self.board, (Tetris.HEIGHT, Tetris.WIDTH))
        for i, row, in enumerate(board_as_rows):
            if (row != 0).all():
                row[:] = 0.0
                cleared_lines += 1
        self.board = np.reshape(board_as_rows, (Tetris.WIDTH, Tetris.HEIGHT))
        
        reward = self.rewards[cleared_lines]

        return reward, self.board, 

    def reset(self):
        self.board = np.zeros((10, 40))
        self.blocks_buf = [i for i in Tetris.TETRAMINOS]
        self.blocks_buf = random.shuffle(self.blocks_buf)
        self.step_idx = 0
        self.free_fall = False
        self.current_block = None

    def render(self, render_mode="human"):
        pass

t = Tetris()
t.step(3)
    