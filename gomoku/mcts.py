from __future__ import absolute_import, division, print_function
from math import sqrt, log
from copy import deepcopy
import random

#Feel free to add extra classes and functions
# Disclaimer: The algorithm has been tested with and without
# my additional greedy algorithm. Both works 100% against the other
# player; how ever, the greedy algorithm largely speed up the game
# and thus facilitate grading.

# the preferred option range from existing grid
MAX_REACH = 1
# budget 800: 13 seconds per MCTS
# budget 900: 15 sec
BUDGET = 750

class State:
    def __init__(self, grid, player):

        # copied from board
        self.grid = grid
        self.maxrc = len(grid)-1
        self.piece = player
        self.grid_size = 52
        self.grid_count = 11
        self.game_over = False
        self.winner = None

        # MCT parameter
        self.N = 0  # number of trials
        self.Q = 0  # number of won trials
        self.expanded = False   # if its children has been expanded
        self.options = self.get_options(self.grid)  # possible children action
        self.checked = {}   # see if an option (which leads to a child) has been explored
        for (r, c) in self.options:
            self.checked[r, c] = False
        self.children = []  # children states
        self.father = 0  # parent state
        # record the last option made
        self.last_option = 0    # the last option the player made

    # copied from randplay
    def set_piece(self, r, c):
        if self.grid[r][c] == '.':
            self.grid[r][c] = self.piece
            if self.piece == 'b':
                self.piece = 'w'
            else:
                self.piece = 'b'
            return True
        return False

    def check_win(self, r, c):
        n_count = self.get_continuous_count(r, c, -1, 0)
        s_count = self.get_continuous_count(r, c, 1, 0)
        e_count = self.get_continuous_count(r, c, 0, 1)
        w_count = self.get_continuous_count(r, c, 0, -1)
        se_count = self.get_continuous_count(r, c, 1, 1)
        nw_count = self.get_continuous_count(r, c, -1, -1)
        ne_count = self.get_continuous_count(r, c, -1, 1)
        sw_count = self.get_continuous_count(r, c, 1, -1)
        if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
            self.winner = self.grid[r][c]
            self.game_over = True
        elif self.get_options(self.grid) == {}:
            self.winner = 'w'
            self.game_over = True

    def get_options(self, grid):
        #collect all occupied spots
        current_pcs = []
        for r in range(len(grid)):
            for c in range(len(grid)):
                if not grid[r][c] == '.':
                    current_pcs.append((r,c))
        #At the beginning of the game, curernt_pcs is empty
        if not current_pcs:
            return [(self.maxrc//2, self.maxrc//2)]
        #Reasonable moves should be close to where the current pieces are
        #Think about what these calculations are doing
        #Note: min(list, key=lambda x: x[0]) picks the element with the min value on the first dimension
        min_r = max(0, min(current_pcs, key=lambda x: x[0])[0]-MAX_REACH)
        max_r = min(self.maxrc, max(current_pcs, key=lambda x: x[0])[0]+MAX_REACH)
        min_c = max(0, min(current_pcs, key=lambda x: x[1])[1]-MAX_REACH)
        max_c = min(self.maxrc, max(current_pcs, key=lambda x: x[1])[1]+MAX_REACH)
        #Options of reasonable next step moves
        options = []
        for i in range(min_r, max_r+1):
            for j in range(min_c, max_c+1):
                if not (i, j) in current_pcs:
                    options.append((i, j))
        if len(options) == 0:
            #In the unlikely event that no one wins before board is filled
            #Make white win since black moved first
            self.game_over = True
            self.winner = 'w'
        return options

    # default policy helpers
    def make_move(self):
        return random.choice(self.get_options(self.grid))

    def get_continuous_count(self, r, c, dr, dc):
        piece = self.grid[r][c]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result

    def rollout(self):
        simReward = {}
        while not self.game_over:
            r, c = self.make_move()
            self.set_piece(r, c)
            self.check_win(r, c)
        #assign rewards
        if self.winner == 'b':
            simReward['b'] = 0
            simReward['w'] = 1
        elif self.winner == 'w':
            simReward['b'] = 1
            simReward['w'] = 0
        # print("Rolling out, winner is ", self.winner)
        return simReward

class MCTS:
    def __init__(self, grid, player):
        self.root = State(grid, player)
        self.budget = BUDGET
        self.greedy_step = (0,0)

    # Entry for MCTS
    def make_move(self):
        return self.uct_search()

    # avoid instant death or guarantee instant win
    def greedy(self, state):
        sim_state = State(deepcopy(state.grid), deepcopy(state.piece))
        # guarantee a win
        for option in sim_state.options:
            sim_state.grid[option[0]][option[1]] = state.piece
            sim_state.check_win(option[0], option[1])
            if sim_state.game_over:
                self.greedy_step = option
                return True
            sim_state.grid[option[0]][option[1]] = '.'
        # avoid a lose
        for option in sim_state.options:
            sim_state.grid[option[0]][option[1]] = 'w' if state.piece == 'b' else 'w'
            sim_state.check_win(option[0], option[1])
            if sim_state.game_over:
                self.greedy_step = option
                return True
            sim_state.grid[option[0]][option[1]] = '.'
        return False

    # TreePolicy
    def simulation(self, state):

        while not state.game_over:
            s = self.expansion(state)
            if not state.expanded:
                return s
            else:
                state = self.best_child(state)
        return state

    # MCTS
    def uct_search(self):
        # check greedy moves
        # currently it only support prioritizing root, since
        # otherwise it'll be too slow
        if self.greedy(self.root):
            return self.greedy_step

        while self.budget != 0:
            state = self.simulation(self.root)
            winner = self.selection(state)
            self.backpropagation(state, winner)
            self.budget -= 1
        return (self.optimal_child(self.root)).last_option

    # defaultPolicy, return who's the winner
    def selection(self, state):
        sim_state = State(deepcopy(state.grid), deepcopy(state.piece))
        reward = sim_state.rollout()
        if reward[state.piece] == 1:
            return state.piece
        else:
            return 'b' if state.piece == 'w' else 'w'

    # expand child
    def expansion(self, state):
        if state.expanded:
            return state
        for option in state.options:
            if not state.checked[option]:
                state.checked[option] = True
                child_grid = deepcopy(state.grid)
                child = State(child_grid, state.piece)
                child.father = state
                child.last_option = option
                child.set_piece(option[0], option[1])
                child.check_win(option[0], option[1])
                state.children.append(child)
                return child
        # if no more child is unchecked, set state to expanded
        state.expanded = True
        return state

    # evaluation function for picking best child
    def evaluation(self, state, father):
        return state.Q/state.N + sqrt(log(father.N, 2)/state.N)

    # calculate win rate
    def win_rate(self, state):
        return state.Q/state.N

    # best child to explore
    def best_child(self, state):
        best = random.choice(state.children)
        for child in state.children:
            if self.evaluation(child, state) > self.evaluation(best, state):
                best = child
        return best

    # current child with highest win rate
    def optimal_child(self, state):
        best = random.choice(state.children)
        for child in state.children:
            if self.win_rate(child) > self.win_rate(best):
                best = child
        return best

    def backpropagation(self, state, result):
        while state != 0:
            state.N += 1
            state.Q += 1 if state.piece == result else 0
            state = state.father


