from __future__ import print_function
import copy, random, math
MOVES = {0:'up', 1:'left', 2:'down', 3:'right'}

class State:
	"""game state information"""
	# Hint: probably need the tile matrix, which player's turn, score, previous move
	def __init__(self, matrix, player, score, pre_move):
		# matrix should be passed in as a deep copy
		self.matrix = matrix
		# '0' means max player and '1' means chance player
		self.player = player
		self.score = score
		self.pre_move = pre_move
		# list that contains all the children of this state
		self.children = []
	def highest_tile(self):
		"""Return the highest tile here (just a suggestion, you don't have to)"""
		value = 0
		for row in range(4):
			for col in range(4):
				# find the highest tile
				value = max(value, self.matrix[row][col])
		return value

class Gametree:
	"""main class for the AI"""
	# Hint: Two operations are important. Grow a game tree, and then compute minimax score.
	# Hint: To grow a tree, you need to simulate the game one step.
	# Hint: Think about the difference between your move and the computer's move.
	def __init__(self, root, depth):
		# root matrix is already passed in as a deep copy in 2048.py
		# create the root state
		# self.root = State(root, 0, 0, -1)
		self.root = root
		self.depth = depth
		# list that contains all the terminal states
		self.terminal = []
		# dictionary that contains the minimax value for each state
		self.value_dict = {}
	def grow_once(self, state):
		"""Grow the tree one level deeper"""
		# if the player is the max player
		if state.player == 0:
			for i in range(4):
				# create a child simulator for this direction
				child_simulator = Simulator(copy.deepcopy(state.matrix), state.score)
				# make the move of this direction
				child_simulator.move(i)
				# check whether this move is available or not
				if child_simulator.can_move == True:
					# create a child state for this direction
					child_state = State(copy.deepcopy(child_simulator.tileMatrix), 1 - state.player, child_simulator.total_points, i)
					# update the children list of the parent state
					state.children.append(child_state)
			# this state is a terminal state if it has no child
			if len(state.children) == 0:
				# update the terminal state list
				self.terminal.append(state)
		# if the player is the chance player
		elif state.player == 1:
			for row in range(4):
				for col in range(4):
					if state.matrix[row][col] == 0:
						# create a child state for this open spot
						child_state = State(copy.deepcopy(state.matrix), 1 - state.player, state.score, state.pre_move)
						# put a 2-tile on this open spot
						child_state.matrix[row][col] = 2
						# update the children list of the parent state
						state.children.append(child_state)
			# this state is a terminal state if it has no child
			if len(state.children) == 0:
				# update the terminal state list
				self.terminal.append(state)
	def grow(self, state, height):
		"""Grow the full tree from root"""
		# the state is terminal state if height is 0
		if height == 0:
			self.terminal.append(state)
		else:
			# grow one level deeper first
			self.grow_once(state)
			for i in state.children:
				# recursion
				self.grow(i, height - 1)
	def minimax(self, state):
		"""Compute minimax values on the tree"""
		# if the state is terminal state
		if state in self.terminal:
			"""Extra Credits"""
			# self.value_dict[state] = self.compute_score(state)
			# return self.value_dict[state]
			"""Comment below lines when running the extra credits part"""
			# update the dictionary
			self.value_dict[state] = state.score + state.highest_tile()
			return state.score + state.highest_tile()
		# if the state is the max player
		elif state.player == 0:
			# initialize the value
			value = float('-Inf')
			for i in state.children:
				value = max(value, self.minimax(i))
			# update the dictionary
			self.value_dict[state] = value
			return value
		# if the state is the chance player
		elif state.player == 1:
			# initialize the value
			value = 0.0
			# calculate the expected value of the subtree
			for i in state.children:
				value = value + self.minimax(i) * (1.0 / float(len(state.children)))
			# update the dictionary
			self.value_dict[state] = value
			return value
	def expectimax(self, matrix, depth, player):
		if depth == 0:
			# self.value_dict[state] = self.compute_score(matrix)
			#self.value_dict[matrix] = float(self.compute_score(matrix))
			return float(self.compute_score(matrix))
		elif player == 0:
			value = 0.0
			for i in range(4):
				new_matrix = copy.deepcopy(matrix)
				simulator = Simulator(new_matrix, 0)
				simulator.move(i)
				value = max(value, self.expectimax(simulator.tileMatrix, depth - 1, 1 - player))
			#self.value_dict[matrix] = value
			return value
		elif player == 1:
			value = 0.0
			counter = 0.0
			for row in range(4):
				for col in range(4):
					if matrix[row][col] == 0:
						counter = counter + 1.0
						new_matrix = copy.deepcopy(matrix)
						new_matrix[row][col] = 2
						value = value + self.expectimax(new_matrix, depth - 1, 1 - player)
			#self.value_dict[matrix] = value
			if counter == 0:
				return 0
			else:
				return value / counter
	def compute_decision(self):
		"""Derive a decision"""
		# build the tree
		#self.grow(self.root, self.depth)
		# the minimax algorithm
		#minimax_value = self.minimax(self.root)
		decision = -1
		value = -1
		# get the decision for the root
		#for i in self.root.children:
		#	if minimax_value == self.value_dict[i]:
		#		decision = i.pre_move
		#		break
		for i in range(4):
			# print(i)
			new_root = copy.deepcopy(self.root)
			simulator = Simulator(new_root, 0)
			simulator.move(i)
			if simulator.can_move == True:
				#continue
				new_value = self.expectimax(simulator.tileMatrix, self.depth - 1, 1)
				#print(value)
				#print(new_value)
				if new_value > value:
					decision = i
					value = new_value
		#print(value)
		print(MOVES[decision])
		return decision
	def compute_score(self, matrix):
		offset = 0
		for row in range(4):
			for col in range(4):
				# go through the neighbors of this tile
				if 0 <= row + 1 <= 3 and 0 <= col <= 3:
					offset = offset + abs(matrix[row][col] - matrix[row + 1][col])
				if 0 <= row - 1 <= 3 and 0 <= col <= 3:
					offset = offset + abs(matrix[row][col] - matrix[row - 1][col])
				if 0 <= row <= 3 and 0 <= col + 1 <= 3:
					offset = offset + abs(matrix[row][col] - matrix[row][col + 1])
				if 0 <= row <= 3 and 0 <= col - 1 <= 3:
					offset = offset + abs(matrix[row][col] - matrix[row][col - 1])
		value = 0
		for i in range(4):
			for j in range(4):
				# calculate the value of the matrix with the weight
				value = value + (matrix[i][j] * self.weight(i, j))
		return value - offset
	def weight(self, row, col):
		# create a matrix with each tile having certain weight
		m = [[6, 5, 4, 3], [5, 4, 3, 2], [4, 3, 2, 1], [3, 2, 1, 0]]
		return m[row][col]

class Simulator:
	"""Simulation of the game"""
	# Hint: You basically need to copy all the code from the game engine itself.
	# Hint: The GUI code from the game engine should be removed.
	# Hint: Be very careful not to mess with the real game states.
	def __init__(self, matrix, score):
		self.total_points = score
		self.default_tile = 2
		self.board_size = 4
		# pygame.init()
		# self.surface = pygame.display.set_mode((400, 500), 0, 32)
		# pygame.display.set_caption("2048")
		# self.myfont = pygame.font.SysFont("arial", 40)
		# self.scorefont = pygame.font.SysFont("arial", 30)
		self.undoMat = []
		# matrix should be passed in as a deep copy
		self.tileMatrix = matrix
		# whether a specific direction is allowed or not
		self.can_move = False
	# Make a move of certain direction
	def move(self, direction):
		self.addToUndo()
		for i in range(0, direction):
			self.rotateMatrixClockwise()
		if self.canMove():
			self.moveTiles()
			self.mergeTiles()
			self.can_move = True
			# self.placeRandomTile()
		for j in range(0, (4 - direction) % 4):
			self.rotateMatrixClockwise()
		# self.printMatrix()
	# Move the tiles
	def moveTiles(self):
		tm = self.tileMatrix
		for i in range(0, self.board_size):
			for j in range(0, self.board_size - 1):
				while tm[i][j] == 0 and sum(tm[i][j:]) > 0:
					for k in range(j, self.board_size - 1):
						tm[i][k] = tm[i][k + 1]
					tm[i][self.board_size - 1] = 0
	# Merge the tiles
	def mergeTiles(self):
		# pass
		tm = self.tileMatrix
		for i in range(0, self.board_size):
			for k in range(0, self.board_size - 1):
				if tm[i][k] == tm[i][k + 1] and tm[i][k] != 0:
					tm[i][k] = tm[i][k] * 2
					tm[i][k + 1] = 0
					self.total_points += tm[i][k]
					self.moveTiles()
	# Check whether the game is over or not
	def checkIfCanGo(self):
		tm = self.tileMatrix
		for i in range(0, self.board_size ** 2):
			if tm[int(i / self.board_size)][i % self.board_size] == 0:
				return True
		for i in range(0, self.board_size):
			for j in range(0, self.board_size - 1):
				if tm[i][j] == tm[i][j + 1]:
					return True
				elif tm[j][i] == tm[j + 1][i]:
					return True
		return False
	# Check whether it can make the certain move or not
	def canMove(self):
		tm = self.tileMatrix
		for i in range(0, self.board_size):
			for j in range(1, self.board_size):
				if tm[i][j-1] == 0 and tm[i][j] > 0:
					return True
				elif (tm[i][j-1] == tm[i][j]) and tm[i][j-1] != 0:
					return True
		return False
	# Rotate the matrix clockwise
	def rotateMatrixClockwise(self):
		tm = self.tileMatrix
		for i in range(0, int(self.board_size/2)):
			for k in range(i, self.board_size- i - 1):
				temp1 = tm[i][k]
				temp2 = tm[self.board_size - 1 - k][i]
				temp3 = tm[self.board_size - 1 - i][self.board_size - 1 - k]
				temp4 = tm[k][self.board_size - 1 - i]
				tm[self.board_size - 1 - k][i] = temp1
				tm[self.board_size - 1 - i][self.board_size - 1 - k] = temp2
				tm[k][self.board_size - 1 - i] = temp3
				tm[i][k] = temp4
	# Convert to linear matrix
	def convertToLinearMatrix(self):
		m = []
		for i in range(0, self.board_size ** 2):
			m.append(self.tileMatrix[int(i / self.board_size)][i % self.board_size])
		m.append(self.total_points)
		return m
	def addToUndo(self):
		self.undoMat.append(self.convertToLinearMatrix())
