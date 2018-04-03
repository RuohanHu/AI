import random

class Randplay:
    def __init__(self, grid, player):
        self.grid = grid
        self.maxrc = len(grid)-1
        self.piece = player
        self.grid_size = 26
        self.grid_count = 19
        self.game_over = False
        self.winner = None
    def get_options(self, grid):
        #collect all occupied spots
        current_pcs = []
        for r in range(len(grid)):
            for c in range(len(grid)):
                if not grid[r][c] == '.':
                    current_pcs.append((r,c))
        #At the beginning of the game, curernt_pcs is empty
        if not current_pcs:
            return [(self.maxrc/2, self.maxrc/2)]
        #Reasonable moves should be close to where the current pieces are
        #Think about what these calculations are doing
        #min(list, key=lambda x: x[0]) picks the element with the min value on the first dimension
        min_r = max(0, min(current_pcs, key=lambda x: x[0])[0]-1)
        max_r = min(self.maxrc, max(current_pcs, key=lambda x: x[0])[0]+1)
        min_c = max(0, min(current_pcs, key=lambda x: x[1])[1]-1)
        max_c = min(self.maxrc, max(current_pcs, key=lambda x: x[1])[1]+1)
        #Options of reasonable next step moves
        options = []
        for i in range(min_r, max_r+1):
            for j in range(min_c, max_c+1):
                if not (i, j) in current_pcs:
                    options.append((i,j))
        if len(options) == 0:
            #In the unlikely event that no one wins before board is filled
            #Make white win since black moved first
            self.game_over = True
            self.winner = 'w'
        return options
    def get_optimal_option(self, grid):
        # collect all the black pieces
        current_black_pcs = []
        for r in range(len(grid)):
            for c in range(len(grid)):
                if grid[r][c] == 'b':
                    current_black_pcs.append((r,c))
        # at the beginning of the game, curernt_black_pcs is empty
        if len(current_black_pcs) == 0:
            return (self.maxrc/2, self.maxrc/2)
        # collect all the available spots around the black pieces
        around_black_spots = []
        for i, j in current_black_pcs:
            if (j - 1) >= 0 and grid[i][j - 1] == '.':
                around_black_spots.append((i, j - 1))
            if (i - 1) >= 0 and (j - 1) >= 0 and grid[i - 1][j - 1] == '.':
                around_black_spots.append((i - 1, j - 1))
            if (j + 1) <= self.maxrc and (i - 1) >= 0 and grid[i - 1][j + 1] == '.':
                around_black_spots.append((i - 1, j + 1))
            if (j + 1) <= self.maxrc and (i + 1) <= self.maxrc and grid[i + 1][j + 1] == '.':
                around_black_spots.append((i + 1, j + 1))
            if (i + 1) <= self.maxrc and (j - 1) >= 0 and grid[i + 1][j - 1] == '.':
                around_black_spots.append((i + 1, j - 1))
            if (i - 1) >= 0 and grid[i - 1][j] == '.':
                around_black_spots.append((i - 1, j))
            if (j + 1) <= self.maxrc and grid[i][j + 1] == '.':
                around_black_spots.append((i, j + 1))
            if (i + 1) <= self.maxrc and grid[i + 1][j] == '.':
                around_black_spots.append((i + 1, j))
        if len(around_black_spots) == 0:
            # In the unlikely event that no one wins before board is filled
            # Make white win since black moved first
            self.game_over = True
            self.winner = 'w'
        i = random.randint(0, len(around_black_spots)-1)
        return around_black_spots[i]
    def make_move(self):
        options = self.get_options(self.grid)
        m = random.randint(0,len(options)-1)
        return options[m]
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
    def set_piece(self, r, c):
        if self.grid[r][c] == '.':
            self.grid[r][c] = self.piece
            if self.piece == 'b':
                self.piece = 'w'
            else:
                self.piece = 'b'
            return True
        return False
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
