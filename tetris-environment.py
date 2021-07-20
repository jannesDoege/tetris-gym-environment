import gym
import numpy as np
import random
import tkinter as tk
import time

# TODO update reset

class Tetris(gym.Env):
    """
    Custom Tetris Environment
    
    actions:
    0 -> do nothing

    1 -> move left

    2 -> move right

    3 -> rotate in positive direction

    4 -> rotate in negative direction

    observation is the whole playfield numpy array with shape (10,20) where 0 means there is no block and 1 means there is a block
    """
    WIDTH = 10
    HEIGHT = 20

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
        field = np.copy(self.board)

        field = np.where(field  == self.block_count, 0, field)
        for idx, i in enumerate(range(int(zero_zero[0]), int(zero_zero[0] + 4))):
            for val_idx, val in enumerate(block[idx]):
                if field[i][int(val_idx + zero_zero[1])] != (0 and val) and val != 0:
                    possible = False
                else: field[i][val_idx + zero_zero[1]] = val
        return field, possible

    def __init__(self):
        self.board = np.zeros((Tetris.WIDTH, Tetris.HEIGHT), dtype=np.uint8)
        self.blocks_buf = [i for i in Tetris.TETRAMINOS]
        random.shuffle(self.blocks_buf)
        self.next_blocks = [self.blocks_buf.pop(0), self.blocks_buf.pop(0)]
        self.step_idx = 0
        self.current_block = None
        self.block_count = 0
        self.rewards = [0, 1, 4, 8, 16]
        self.free_fall = False
        self.block_a = None
        self.done = False
        self._row = 0
        self._column = 0

        obs_spaces = gym.spaces.Tuple(
            gym.spaces.Box(low=0, high=1, shape=(Tetris.WIDTH, Tetris.HEIGHT), dtype=np.uint8),
            # two arrays (one for each block) with shape 4x4
            gym.spaces.Box(low=0, high=1, shape=(2, 4, 4))
        )
        self.observation_space = gym.spaces.Dict(obs_spaces)
        self.action_space = gym.spaces.Discrete(5)

        self.window = tk.Tk()
        self.window.resizable(False, False)
        self.window.geometry(f"{300 + 2*10}x{600 + 20}")
        self.canvas = tk.Canvas(self.window, width=300, height=600, background="#BBBBBB")

    def step(self, action):
        reward = 0.0
        if self.done:
            return (np.clip(self.board, 0,1), np.clip(np.array(self.next_blocks))), reward, self.done, None
        self.step_idx += 1
        cleared_lines = 0

        if len(self.blocks_buf) == 0:
            self.blocks_buf = [i for i in Tetris.TETRAMINOS]
            random.shuffle(self.blocks_buf)
        
        if not self.free_fall:
            self.block_count += 1
            self.current_block = self.next_blocks.pop(0)
            self.next_blocks.append(self.blocks_buf.pop(0))
            self._row = 0

            self.block_a = self._convert_points_to_array(self.current_block)
            self._column = int(Tetris.WIDTH/2) - 2 + 1

            # insert new block and check for done
            if not self.done:
                f, possible = self._insert_block(self.block_a, (int(Tetris.WIDTH/2-2), 0)) 
                if possible: self.board = np.copy(f)
                else: self.done = True; 
            self.free_fall = True
            return (np.clip(self.board, 0,1), np.clip(np.array(self.next_blocks))), reward, self.done, None

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
                    self._column -= 1

                if Tetris.ACTIONS[action] == "move_right":
                    zeros = [i for i in to_move]
                    ones = [(i[0]+1, i[1]) for i in zeros]
                    self._column += 1

                for col, row in zeros:
                    self.board[col][row] = 0
                for col, row in ones:
                    self.board[col][row] = self.block_count
        
        # rotate left or right
        if self.free_fall and (Tetris.ACTIONS[action] == "rotate_pos" or Tetris.ACTIONS[action] == "rotate_neg"):
            new_block = np.copy(self.current_block)
                            
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
            block_to_insert = np.copy(new_block)

            # put down
            minimum = np.amin(block_to_insert, axis=0)
            if Tetris.ACTIONS[action] == "rotate_pos":
                for i in range(len(block_to_insert)):
                    block_to_insert[i][1] -= minimum[1]
                    block_to_insert[i][0] -= minimum[0]
            else:
                for i in range(len(block_to_insert)):
                    block_to_insert[i][1] -= minimum[1]
                    block_to_insert[i][0] -= minimum[0]
            new_block_t = [(i, j) for i, j in new_block]
            new_block_a = self._convert_points_to_array(block_to_insert)

            # check if rotation is possible and rotate or dont rotate
            f, possible = self._insert_block(new_block_a, (self._column, self._row))
            if possible:
                # save in fields
                self.current_block = [i for i in new_block_t]
                self.block_a = np.copy(new_block_a)
                
                self.board = np.copy(f)

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
                if i == self.block_count:
                    self._row += 1

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
        return (np.clip(self.board, 0,1), np.clip(np.array(self.next_blocks))), reward, self.done, None

    def reset(self):
        self.board = np.zeros((Tetris.WIDTH, Tetris.HEIGHT))
        self.blocks_buf = [i for i in Tetris.TETRAMINOS]
        random.shuffle(self.blocks_buf)
        self.step_idx = 0
        self.free_fall = False
        self.current_block = None

    def render(self, render_mode="human", ms: int = 1000):

        
        self.canvas.delete("all")
        self.canvas.create_rectangle(2, 2, 300, 600)
        for idx_col, column in enumerate(self.board[::-1]):
            for idx_val, val in enumerate(column):
                color = "#FF0000" if val != 0 else ""
                self.canvas.create_rectangle(idx_col*30, idx_val*30, 30+idx_col*30, 30+idx_val*30, fill=color)

        self.canvas.pack()
        #self.window.after(ms, lambda: self.window.destroy())
        self.window.update()
        time.sleep(ms/1000)

t = Tetris()

obs, reward, done, info = None, None, None, None
for i in range(8):
    obs, reward, done, info = t.step(3)
    print(reward, done, t.free_fall, t.block_count)
    print(t.board)
    t.render()

#print(reward, done, info)
#print(obs)
    