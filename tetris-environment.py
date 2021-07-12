import gym
import numpy as np
import random

# TODO fix falling

class Tetris(gym.Env):
    """
    Custom Tetris Environment
    
    actions:
    0 -> do nothing

    1 -> move left

    2 -> move right

    3 -> rotate in positive direction

    4 -> rotate in negative direction

    observation is the whole playfield numpy array with shape (10,40) where 0 means there is no block and 1 means there is a block
    """
    WIDTH = 10
    HEIGHT = 40

    # (y,x)
    TETRAMINOS = [
        [(0,0), (1,0), (0,1), (0,2)], # lblock
        [(0,0), (1,0), (1,1), (2,1)], # jblock 
        [(1,0), (0,1), (1,1), (0,2)], # sblock 
        [(0,0), (0,1), (1,1), (1,2)], # zblock 
        [(0,0), (0,1), (1,1), (0,2)], # tblock 
        [(0,0), (0,1), (0,2), (0,3)], # iblock 
        [(0,0), (1,0), (0,1), (1,1)]  # sqrblock
    ]

    ACTIONS = {
        0: "nothing",
        1: "move_left",
        2: "move_right",
        3: "rotate_pos",
        4: "rotate_neg"
    }

    def __init__(self):
        self.board = np.zeros((Tetris.WIDTH, Tetris.HEIGHT), dtype=np.uint8)
        self.blocks_buf = [i for i in Tetris.TETRAMINOS]
        random.shuffle(self.blocks_buf)
        self.step_idx = 0
        self.current_block = None
        self.block_count = 0
        self.rewards = [0, 1, 4, 8, 16]
        self.free_fall = False
        self.block_a = None
        self.done = False

        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(Tetris.WIDTH, Tetris.HEIGHT), dtype=np.uint8)
        self.action_space = gym.spaces.Discrete(5)

    def step(self, action):
        reward = 0.0

        if self.done:
            return np.clip(self.board, 0,1), reward, self.done, None

        self.step_idx += 1

        cleared_lines = 0

        # TODO action (move left, right and rotate left, right)

        if self.step_idx % len(Tetris.TETRAMINOS) == 0:
            self.blocks_buf = [i for i in Tetris.TETRAMINOS]
            random.shuffle(self.blocks_buf)
        
        if not self.free_fall:
            self.block_count += 1
            self.current_block = self.blocks_buf.pop(0)

            # convert the points to array (columns(points)) ordered top to bottom
            self.block_a = np.zeros((4,4))
            for i in range(0,4):
                self.block_a[self.current_block[i][1]][self.current_block[i][0]] = self.block_count     
       
            # insert new block and check for done
            if not self.done:
                for idx, i in enumerate(range(int(Tetris.WIDTH/2-2), int(Tetris.WIDTH/2+2))):
                    for val_idx, val in enumerate(self.block_a[idx]):
                        if self.board[i][val_idx] != 0 and val != 0:
                            self.done = True
                            return np.clip(self.board, 0,1), reward, self.done, None
                        else: self.board[i][val_idx] = val
            self.free_fall = True
        ls=[]
        # TODO fix entry to for loop
        # check if a certain number should fall or not
        for i in range(1, self.block_count+1):
            fall = None
            el_count = 0
            for j in self.board:
                for n, k in enumerate(j):
                    if n == Tetris.HEIGHT -1:
                        if k == i:
                            fall = False
                        continue
                    
                    # check if it is block and if there is not block below
                    if k == i and j[int(n)+1] == 0 and n != 39 and fall != False:
                        fall = True
                        el_count += 1
                    if(k == i and (j[int(n)+1] != 0 and j[int(n)+1] != i) or n == Tetris.HEIGHT-1): fall = False                    
            
            # which values should be chnanged to fall
            change_to_zero = []
            change_to_one = []
            if fall:
                for idx, column in enumerate(self.board):
                    for n, num in enumerate(column):
                        if num == i and n != 39:
                            ls.append(i)
                            change_to_zero.append((idx, int(n)))
                            change_to_one.append((idx, int(n+1)))
            
            # change values for fall                             
            for i, j in change_to_zero:
                self.board[i][j] = 0
            for i, j in change_to_one:
                self.board[i][j] = 1
            
            
            # set free_fall to False, if the current Block has landed
            if i == self.block_count and fall:
                self.free_fall = True
            elif i == self.block_count:
                self.free_fall = False

        # set all values to zero if line is to clear
        board_as_rows = np.reshape(self.board, (Tetris.HEIGHT, Tetris.WIDTH))
        for i, row, in enumerate(board_as_rows):
            if (row != 0).all():
                row[:] = 0.0
                cleared_lines += 1
        self.board = np.reshape(board_as_rows, (Tetris.WIDTH, Tetris.HEIGHT))
        
        reward = self.rewards[cleared_lines]

        # observation, reward, done, info
        return np.clip(self.board, 0,1), reward, self.done, None

    def reset(self):
        self.board = np.zeros((10, 40))
        self.blocks_buf = [i for i in Tetris.TETRAMINOS]
        random.shuffle(self.blocks_buf)
        self.step_idx = 0
        self.free_fall = False
        self.current_block = None

    def render(self, render_mode="human"):
        # TODO create render window
        pass

t = Tetris()


for i in range(1,41):
    obs, reward, done, info = t.step(3)
    print(reward, done, t.free_fall)
    print(obs[2:6])
    