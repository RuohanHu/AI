from __future__ import print_function
import random, copy
import os

class Grid:
	def __init__(self, problem):
		self.spots = [(i, j) for i in range(1, 10) for j in range(1, 10)]
		self.domains = {}
		# need a dictionary that maps each spot to its related spots
		self.peers = {} 
		# initialize the dictionary
		for i in range(1, 10):
			for j in range(1, 10):
				self.peers[(i, j)] = []
		for i in range(1, 10):
			for j in range(1, 10):
				# all the spots in the same column
				for k in range(1, 10):
					self.peers[(i, j)].append((k, j))
				# all the spots in the same row
				for k in range(1, 10):
					self.peers[(i, j)].append((i, k))
				# all the spots in the same 3 x 3 grid
				r = i - (i % 3) + 1
				c = j - (j % 3) + 1
				# make the row match to the start row of the grid
				if i == 3:
					r = 1
				elif i == 6:
					r = 4
				elif i == 9:
					r = 7
				# make the column match to the start column of the grid
				if j == 3:
					c = 1
				elif j == 6:
					c = 4
				elif j == 9:
					c = 7
				for m in range(0, 3):
					for n in range(0, 3):
						self.peers[(i, j)].append((r + m, c + n))
		self.parse(problem)
	def parse(self, problem):
		for i in range(0, 9):
			for j in range(0, 9):
				c = problem[i * 9 + j] 
				if c == '.':
					self.domains[(i + 1, j + 1)] = range(1, 10)
				else:
					self.domains[(i + 1, j + 1)] = [ord(c) - 48]
	def display(self):
		for i in range(0, 9):
			for j in range(0, 9):
				d = self.domains[(i + 1, j + 1)]
				if len(d) == 1:
					print(d[0], end='')
				else: 
					print('.', end='')
				if j == 2 or j == 5:
					print(" | ", end='')
			print()
			if i == 2 or i == 5:
				print("---------------")

class Solver1:
	def __init__(self, grid):
		# sigma is the assignment function
		self.sigma = {}
		self.grid = grid
		# get the current assignment
		for i in self.grid.domains:
			if (len(self.grid.domains[i])) == 1:
				self.sigma[i] = self.grid.domains[i][0]
	def solve(self):
		# update the domain if the search is successful
		if self.search(self.sigma):
			for i in self.grid.domains:
				self.grid.domains[i] = [self.sigma[i]]
			return True
		else:
			return False
	def search(self, sigma):
		# return sigma if all the variables are assigned
		if len(sigma) == 81:
			return True
		# select an unassigned variable
		decision = None
		for i in self.grid.spots:
			# make the decision
			if i not in sigma:
				decision = i
				break
		# choose the value for the decision
		for value in self.grid.domains[decision]:
			# initialize a dictionary for inferences
			inferences = {}
			# check whether the decision is consistent with the current assignment
			if self.consistent(decision, value, sigma):
				# add the decision to the assignment
				sigma[decision] = value
				# make inferences based on the decision (Here we pass the copy of the domain)
				success, inferences = self.infer(sigma, copy.deepcopy(self.grid.domains))
				if success:
					# add the inferences to the assignment 
					for i in inferences:
						sigma[i] = inferences[i]
					# recursion
					result = self.search(sigma)
					if result:
						return True
			# backtrack if conflict occurs
			# remove the decision
			sigma.pop(decision, None)
			# remove the inferences based on the decision
			for j in inferences:
				sigma.pop(j, None)
		return False
	def consistent(self, spot, value, sigma):
		# return false if the value is not consistent with the current assignment
		for i in self.grid.peers[spot]:
			# if the value already appears in the related spots
			if i in sigma and i != spot:
				if sigma[i] == value:
					return False
		return True
	def infer(self, sigma, domains):
		inferences = {}
		# apply arc consistency to make the inferences
		for i in sigma:
			for j in self.grid.peers[i]:
				if j != i and (j not in sigma):
					# remove the value in the domain of related spots
					if sigma[i] in domains[j]:
						domains[j].remove(sigma[i])
					# failure if the domain becomes empty
					if len(domains[j]) == 0:
						return (False, {})
		# update the inferences
		for i in domains:
			# the domain only contains single value
			if len(domains[i]) == 1 and (i not in sigma):
				for j in self.grid.peers[i]:
					# check whether there is other domain which contains the same single value
					if j != i and domains[j] == domains[i]:
						return (False, {})
				inferences[i] = domains[i][0]
		return (True, inferences)

class Solver2:
	def __init__(self, grid):
		# sigma is the assignment function
		self.sigma = {}
		self.grid = grid
		# get the current assignment
		for i in self.grid.domains:
			if (len(self.grid.domains[i])) == 1:
				self.sigma[i] = self.grid.domains[i][0]
	def solve(self):
		# update the domain if the search is successful
		if self.search(self.sigma):
			for i in self.grid.domains:
				self.grid.domains[i] = [self.sigma[i]]
			return True 
		else:
			return False
	def search(self, sigma):
		# return sigma if all the variables are assigned
		if len(sigma) == 81:
			return True
		# select an unassigned variable
		decision = None
		for i in self.grid.spots:
			# make the decision
			if i not in sigma:
				decision = i
				break
		# choose the value for the decision
		for value in self.grid.domains[decision]:
			# initialize a dictionary for inferences
			inferences = {}
			# initialize a dictionary for pruned values
			pruned_value = {}
			# check whether the decision is consistent with the current assignment
			if self.consistent(decision, value, sigma):
				# add the decision to the assignment
				sigma[decision] = value
				# make inference based on the decision (Here we pass the domain directly)
				success, inferences, pruned_value = self.infer(sigma, self.grid.domains)
				if success:
					# add the inferences to the assignment 
					for i in inferences:
						sigma[i] = inferences[i]
					# recursion
					result = self.search(sigma)
					if result:
						return True
			# backtrack if conflict occurs
			# remove the decision
			sigma.pop(decision, None)
			# remove the inferences based on the decision
			for j in inferences:
				sigma.pop(j, None)
			# add the pruned value back to the domain
			for k in pruned_value:
				for m in pruned_value[k]:
					self.grid.domains[k].append(m)
		return False
	def consistent(self, spot, value, sigma):
		# return false if the value is not consistent with the current assignment
		for i in self.grid.peers[spot]:
			# if the value already appears in the related spots
			if i in sigma and i != spot:
				if sigma[i] == value:
					return False
		return True
	def infer(self, sigma, domains):
		# dictionary that stores the inferences
		inferences = {}
		# dictionary that stores the value that gets pruned 
		pruned_value = {}
		# initialize the dictionary
		for i in self.grid.spots:
			pruned_value[i] = []
		# apply arc consistency to prune the domain
		for i in sigma:
			for j in self.grid.peers[i]:
				if j != i and (j not in sigma):
					# prune the domain of related spots
					if sigma[i] in domains[j]:
						domains[j].remove(sigma[i])
						# add the pruned value to the dictionary
						pruned_value[j].append(sigma[i])
					# failure if the domain becomes empty
					if len(domains[j]) == 0:
						return (False, {}, pruned_value)
		# update the inferences
		for i in domains:
			# the domain only contains single value
			if len(domains[i]) == 1 and (i not in sigma):
				for j in self.grid.peers[i]:
					# check whether there is other domain which contains the same single value
					if j != i and domains[j] == domains[i]:
						return (False, {}, pruned_value)
				inferences[i] = domains[i][0]
		return (True, inferences, pruned_value)

class Encoder:
	def __init__(self, grid):
		self.grid = grid
		# dictionary that maps 0 through 15 to its binary represention
		self.binary = {}
		for i in range(0, 16):
			self.binary[i] = '{0:04b}'.format(i)
		# represent the value of each spot with 4 propositional variables
		self.variable = {}
		for i in self.grid.spots:
			self.variable[i] = []
		i = 1
		for j in self.grid.spots:
			self.variable[j].append(str(i))
			self.variable[j].append(str(i + 1))
			self.variable[j].append(str(i + 2))
			self.variable[j].append(str(i + 3))
			i = i + 4
		# list that contains all the encoding results
		self.encoding_result = []
	def encode(self):
		# encode the given values
		for i in self.grid.spots:
			# get the spot with given value
			if len(self.grid.domains[i]) == 1:
				# get the given value
				value = self.grid.domains[i][0]
				# get the given value in binary
				value_binary = self.binary[value]
				k = 0
				for j in value_binary:
					encoding = ""
					if j == '1':
						encoding = encoding + self.variable[i][k] + " 0\n"
					else:
						encoding = encoding + "-" + self.variable[i][k] + " 0\n"
					# add the result to the encoding result list
					self.encoding_result.append(encoding)
					k = k + 1
		# encode the condition that each unassigned spot can only pick value from 1 through 9
		for i in self.grid.spots:
			# get the unassigned spot
			if len(self.grid.domains[i]) != 1:
				for j in range(0, 16):
					# can not pick value from 10 through 15 or 0
					if j == 0 or j in range(10, 16):
						# get the value from 10 through 15 or 0 in binary
						value_binary = self.binary[j]
						l = 0
						encoding = ""
						for k in value_binary:
							if k == '1':
								encoding = encoding + "-" + self.variable[i][l] + " "
							else:
								encoding = encoding + self.variable[i][l] + " "
							l = l + 1
						# add a 0 to the end of each clause
						encoding = encoding + "0\n"
						# add the result to the encoding result list
						self.encoding_result.append(encoding)
		# encode the constraints
		for i in self.grid.spots:
			# get the peers of each spot
			for j in self.grid.peers[i]:
				if j != i:
					# if this spot is unassigned
					if len(self.grid.domains) != 1:
						# for each value from 1 through 9
						for k in range(1, 10):
							encoding = ""
							# get the value in binary
							value_binary = self.binary[k]
							m = 0
							for l in value_binary:
								if l == "1":
									encoding = encoding + "-" + self.variable[i][m] + " "
								else:
									encoding = encoding + self.variable[i][m] + " "
								m = m + 1
							m = 0
							for l in value_binary:
								if l == "1":
									encoding = encoding + "-" + self.variable[j][m] + " "
								else:
									encoding = encoding + self.variable[j][m] + " "
								m = m + 1
							# add a 0 to the end of each clause
							encoding = encoding + "0\n"
							# add the result to the encoding result list
							self.encoding_result.append(encoding)
					# if this spot is already given value
					else:
						# get the value of this assigned spot
						value = self.grid.domains[i][0]
						# get the value in binary representation
						value_binary = self.binary[value]
						encoding = ""
						m = 0
						for l in value_binary:
							if l == "1":
								encoding = encoding + "-" + self.variable[i][m] + " "
							else:
								encoding = encoding + self.variable[i][m] + " "
							m = m + 1
						m = 0
						for l in value_binary:
							if l == "1":
								encoding = encoding + "-" + self.variable[j][m] + " "
							else:
								encoding = encoding + self.variable[j][m] + " "
							m = m + 1
						# add a 0 to the end of each clause
						encoding = encoding + "0\n"
						# add the result to the encoding result list
						self.encoding_result.append(encoding)
	def solve(self):
		# encode
		self.encode()
		# use a dictionary to remove the repeated string
		encode_dictionary = {}
		for i in self.encoding_result:
			encode_dictionary[i] = None
		# open the .cnf file
		cnf_file = open("sudoku.cnf", "w")
		# write the header
		cnf_file.write("p cnf 324 " + str(len(encode_dictionary)) + "\n")
		# write the clauses
		for i in encode_dictionary:
			cnf_file.write(i)
		# close the .cnf file
		cnf_file.close()
		os.system("./picosat sudoku.cnf > output")
		# open the output file
		output_file = open("output", "r")
		result = []
		first_line = True
		for line in output_file:
			# split the line
			l = line.split()
			# check whether the formula is satisfiable or not
			if first_line:
				if l[1] != "SATISFIABLE":
					# close the output file
					output_file.close()
					return False
				first_line = False
			else:
				for i in l:
					# the character is not v or 0
					if i != "v" and int(i) != 0:
						if int(i) < 0:
							result.append("0")
						else:
							result.append("1")
		index = 0
		values = []
		# get the binary value for each spot
		while index < len(result):
			value = ""
			value = result[index] + result[index + 1] + result[index + 2] + result[index + 3]
			values.append(value)
			index = index + 4
		k = 0
		for row in range(1, 10):
			for col in range(1, 10):
				# update the domain
				self.grid.domains[(row, col)] = [int(values[k], 2)]
				k = k + 1
		# close the output file
		output_file.close()
		return True

		
easy = ["..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..",
"2...8.3...6..7..84.3.5..2.9...1.54.8.........4.27.6...3.1..7.4.72..4..6...4.1...3"]

hard = ["4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......",
"52...6.........7.13...........4..8..6......5...........418.........3..2...87....."]

# Task 1
print("====Problem====")
g = Grid(easy[1])
# display the original problem
g.display()
s = Solver1(g)
if s.solve():
	print("====Solution===")
	# display the solution
	g.display()
else:
	print("==No solution==")


# Task 2
print("====Problem====")
g = Grid(easy[1])
# display the original problem
g.display()
s = Solver2(g)
if s.solve():
	print("====Solution===")
	# display the solution
	g.display()
else:
	print("==No solution==")


# Task 3
print("====Problem====")
g = Grid(easy[1])
# display the original problem
g.display()
# create the encoder
e = Encoder(g)
if e.solve():
	print("====Solution===")
	# display the solution
	g.display()
else:
	print("==No solution==")

