from math import sqrt, log
from randplay import *
import random
import copy
import time

class State:
    def __init__(self, grid, player):
        self.grid = grid
        self.player = player
        # the number of times this state leads to a win
        self.win = 0.0
        # the number of times this state gets visited
        self.visited = 0.0
        # for selection, example: (state, (r,c))
        self.children = []
        # for backprobagation
        self.parent = None
        # for checking whether this state is a terminal state or not
        self.terminal = False

class MCTS:
    def __init__(self, grid, player):
        self.root = State(copy.deepcopy(grid), player)
    def uct_search(self):
        start_time = time.time()
        while time.time() - start_time < 6:
            # selection and expansion
            new_state = self.tree_policy(self.root)
            # simulation
            result = self.default_policy(new_state)
            # backprobagation
            self.backprobagation(new_state, result)
        # return the best move
        return (self.best_child(self.root))[1]
    def tree_policy(self, state):
        # while the state is not terminal
        while state.terminal == False:
            # create the simulator
            simulator = Randplay(copy.deepcopy(state.grid), state.player)
            # if the state is not fully expanded
            if len(simulator.get_options(state.grid)) != 0:
                # expand the state
                return self.expand(state)
            # else choose the best child
            else:
                state = (self.best_child(state))[0]
        return state
    def expand(self, state):
        # create the simulator
        simulator = Randplay(copy.deepcopy(state.grid), state.player)
        # choose the untried action
        if state.player == 'w':
            r, c = simulator.make_move()
        elif state.player == 'b':
            r, c = simulator.get_optimal_option(simulator.grid)
        # set the piece
        simulator.set_piece(r, c)
        # check the result
        simulator.check_win(r, c)
        # create the newly expanded state
        next_player = 'b'
        if state.player == 'b':
            next_player = 'w'
        new_state = State(copy.deepcopy(simulator.grid), next_player)
        # append the new_state to the children list of the state
        state.children.append((new_state, (r, c)))
        # update the parent of the new_state
        new_state.parent = state
        # check whether this state is terminal state or not
        if simulator.game_over:
            new_state.terminal = True
        # return the newly expanded state
        return new_state
    def best_child(self, state):
        value = float('-inf')
        best_child = None
        for child in state.children:
            # apply the upper-confidence bound
            child_value = (child[0].win / child[0].visited) + (2.0 * float(sqrt(2.0 * float(log(state.visited)) / child[0].visited)))
            # find the best child
            if child_value > value:
                value = child_value
                best_child = child
        # return the best child
        return best_child
    def default_policy(self, state):
        # check whether the newly expanded state is terminal or not
        if state.terminal:
            # return the result
            if state.player == 'b':
                return "w_won"
            elif state.player == 'w':
                return "b_won"
        # create the simulator
        simulator = Randplay(copy.deepcopy(state.grid), state.player)
        # choose the random move
        r, c = simulator.make_move()
        # set the piece
        simulator.set_piece(r, c)
        # check the result
        simulator.check_win(r, c)
        if simulator.game_over:
            # return the result
            if simulator.winner == 'b':
                return "b_won"
            elif simulator.winner == 'w':
                return "w_won"
        else:
            # decide the next player
            next_player = 'b'
            if state.player == 'b':
                next_player = 'w'
            # create the next state
            next_state = State(copy.deepcopy(simulator.grid), next_player)
            # recursion
            self.default_policy(next_state)
    def backprobagation(self, state, result):
        # back up to the root
        while state:
            # increment the number of times this state gets visited
            state.visited = state.visited + 1.0
            # if the black piece wins
            if result == "b_won":
                # if this state represents a move made by the black
                if state.player == 'w':
                    # increment the number of times this state leads to a win
                    state.win = state.win + 1.0
            # if the white piece wins
            elif result == "w_won":
                # if this state represents a move made by the white
                if state.player == 'b':
                    # increment the number of times this state leads to a win
                    state.win = state.win + 1.0
            state = state.parent
