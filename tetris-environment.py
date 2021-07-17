import gym
import numpy as np
import random

# TODO update self._column, self._row 
# TODO set old blocks after rotation to 0

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

    # [[a, b], [c, d]]
    _pos_rot_mat = np.array([[0, 1], [-1, 0]])
    _neg_rot_mat = np.array([[0, -1], [1, 0]])
    
    # convert the points to array (columns(points)) ordered top to bottom
    def _convert_points_to_array(self, points):
        points_a = np.zeros((4, 4))
        for i in range(0, 4):
            points_a[points[i][1]][points[i][0]] = self.block_count
        return points_a
    
    def _insert_block(self, block, zero_zero: tuple):
        possible = True
        field = np.array(self.board, copy = False)
        for idx, i in enumerate(range(int(zero_zero[0]), int(zero_zero[0] + 4))):
            for val_idx, val in enumerate(block[idx]):
                if field[i][int(val_idx + zero_zero[1])] != 0 and val != 0:
                    possible = False
                else: field[i][val_idx] = val
        return field, possible

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
        self._row = 0
        self._column = 0

        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(Tetris.WIDTH, Tetris.HEIGHT), dtype=np.uint8)
        self.action_space = gym.spaces.Discrete(5)

    def step(self, action):
        reward = 0.0
        if self.done:
            return np.clip(self.board, 0,1), reward, self.done, None
        self.step_idx += 1
        cleared_lines = 0

        if len(Tetris.TETRAMINOS) == 0:
            self.blocks_buf = [i for i in Tetris.TETRAMINOS]
            random.shuffle(self.blocks_buf)
        
        if not self.free_fall:
            self.block_count += 1
            self.current_block = self.blocks_buf.pop(0)
            self._row = 0

            self.block_a = self._convert_points_to_array(self.current_block)
       
            # insert new block and check for done
            if not self.done:
                f, possible = self._insert_block(self.block_a, (int(Tetris.WIDTH/2-2), 0)) 
                if possible: self.board = np.array(f, copy=False) 
                else: self.done = True; return np.clip(self.board, 0,1), reward, self.done, None 
            self.free_fall = True

        # move left or right
        if self.free_fall and (Tetris.ACTIONS[action] == "move_left" or Tetris.ACTIONS[action] == "move_right"):
            # check if there is space to move
            to_move = []
            move = True
            for idx_c, column in enumerate(self.board):
                for idx_val, val in enumerate(column):
                    if val == self.block_count:
                        
                        to_move.append((idx_c, idx_val))
                    else: continue
                    if Tetris.ACTIONS[action] == "move_left" and ((self.board[idx_c-1][idx_val] != 0 and self.board[idx_c-1][idx_val] != self.block_count) or idx_c == 0):
                        move = False
                    if idx_c == Tetris.WIDTH-1:
                        move = False
                        continue
                    if Tetris.ACTIONS[action] == "move_right" and self.board[idx_c+1][idx_val] != 0 and self.board[idx_c+1][idx_val] != self.block_count:
                        move = False            

            if move:
                if Tetris.ACTIONS[action] == "move_left":
                    zeros = [i for i in to_move]
                    ones = [(i[0]-1, i[1]) for i in zeros]

                if Tetris.ACTIONS[action] == "move_right":
                    zeros = [i for i in to_move]
                    ones = [(i[0]+1, i[1]) for i in zeros]
                for col, row in zeros:
                    self.board[col][row] = 0
                for col, row in ones:
                    self.board[col][row] = self.block_count
        
        # rotate left or right
        if self.free_fall and (Tetris.ACTIONS[action] == "rotate_pos" or Tetris.ACTIONS[action] == "rotate_neg"):
            new_block = np.array(self.current_block, copy=False)
                            
            # center all points (rotation will happen around origin)
            for idx, point in enumerate(self.current_block):
                i, j = point
                new_block[idx] = (i-2, j-2)

            # rotate all points
            for idx, point in enumerate(new_block):
                if Tetris.ACTIONS[action] == "rotate_pos":
                    new_point = Tetris._pos_rot_mat.dot(point)
                else:
                    new_point = Tetris._neg_rot_mat.dot(point)
                new_block[idx] = new_point

            # add 2 to each scalar to avoid neg numbers which cause problems when indexing arrays
            for idx, point in enumerate(new_block):
                new_block[idx][0] += 2
                new_block[idx][1] += 2

            # put down
            minimum = np.amin(new_block, axis=0)
            if Tetris.ACTIONS[action] == "rotate_pos":
                for i in range(len(new_block)):
                    new_block[i][1] -= minimum[1]
            else:
                for i in range(len(new_block)):
                    new_block[i][0] -= minimum[0]
                
            new_block_t = [(j, i) for i, j in new_block]
            new_block_a = self._convert_points_to_array(new_block)

            # check if rotation is possible and rotate or dont rotate
            f, possible = self._insert_block(new_block_a, (self._column, self._row))
            if possible:
                # save in fields
                self.current_block = [i for i in new_block_t]
                self.block_a = np.array(new_block_a, copy=False)
                
                self.board = np.array(f, copy = False)

        # check if a certain number should fall or not        
        for i in range(1, self.block_count+1):
            fall = None
            for j in self.board:
                for n, k in enumerate(j):
                    if n == Tetris.HEIGHT -1:
                        if k == i: fall = False
                        continue
                    # check if it is block and if there is not block below
                    if k == i and j[int(n)+1] == 0 and fall != False: fall = True
                    if(k == i and j[int(n)+1] != 0 and j[int(n)+1] != i): fall = False
            
            # which values should be chnanged to fall
            change_to_zero = []
            change_to_one = []
            if fall:
                for idx, column in enumerate(self.board):
                    for n, num in enumerate(column):
                        if num == i and n != 39:
                            change_to_zero.append((idx, int(n)))
                            change_to_one.append((idx, int(n+1)))
            
            # change values for fall                             
            for y, j in change_to_zero:
                self.board[y][j] = 0
            for y, j in change_to_one:

                self.board[y][j] = i
            
            # set free_fall to False, if the current Block has landed
            if i == self.block_count and fall:
                self.free_fall = True
            if not fall and i == self.block_count:
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

obs, reward, done, info = None, None, None, None
for i in range(5):
    obs, reward, done, info = t.step(3)
    print(reward, done, t.free_fall, t.block_count)
    print(obs[:])
#print(reward, done, info)
#print(obs)
    