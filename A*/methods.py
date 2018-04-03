from __future__ import print_function
#Use priority queues from Python libraries, don't waste time implementing your own
#Check https://docs.python.org/2/library/heapq.html
from heapq import *


class Agent:
    def __init__(self, grid, start, goal, type):
        self.actions = [(0,-1),(-1,0),(0,1),(1,0)]
        self.grid = grid
        self.came_from = {}
        self.checked = []
        self.start = start
        self.grid.nodes[start[0]][start[0]].start = True
        self.goal = goal
        self.grid.nodes[goal[0]][goal[1]].goal = True
        self.new_plan(type)
    def new_plan(self, type):
        self.finished = False
        self.failed = False
        self.type = type
        if self.type == "dfs" :
            self.frontier = [self.start]
            self.checked = []
        elif self.type == "bfs":
            # pass
            # initialize the frontier for breadth first search
            self.frontier = [self.start]
            self.checked = []
        elif self.type == "ucs":
            # [Hint] you need a dictionary that keeps track of cost
            # [Hint] you probably also need something like this: heappush(self.frontier, (0, self.start))
            # pass
            self.frontier = []
            # initialize the cost dictionary
            self.gcost_dict = {}
            heappush(self.frontier, (0, self.start))
            self.checked = []
            # put the cost for the initial state into dictionary
            self.gcost_dict[self.start] = 0
        elif self.type == "astar":
            # pass
            self.frontier = []
            # initialize the cost dictionary
            self.gcost_dict = {}
            heappush(self.frontier, (0, self.start))
            self.checked = []
            # put the cost for the initial state into dictionary
            self.gcost_dict[self.start] = 0
    def show_result(self):
        current = self.goal
        if (self.type == "astar" or self.type == "ucs"):
            # print out the cost of the path
            print("final cost: ", self.gcost_dict[current])
        while not current == self.start:
            current = self.came_from[current]
            self.grid.nodes[current[0]][current[1]].in_path = True
    def make_step(self):
        # [Hint] dfs and bfs should look very similar
        if self.type == "dfs":
            self.dfs_step()
        elif self.type == "bfs":
            self.bfs_step()
        # [Hint] ucs and astar should look very similar
        elif self.type == "ucs":
            self.ucs_step()
        elif self.type == "astar":
            self.astar_step()
    def dfs_step(self):
        # check whether the frontier is empty or not
        # no path exists if failed is true
        if not self.frontier:
            self.failed = True
            print("no path")
            return
        current = self.frontier.pop()
        print("popped: ", current)
        # mark the popped node on the grid as checked
        # mark the popped node on the grid as not in the frontier
        # put the popped node into the checked list
        self.grid.nodes[current[0]][current[1]].checked = True
        self.grid.nodes[current[0]][current[1]].frontier = False
        self.checked.append(current)
        # expand the popped node
        for i, j in self.actions:
            # all the nodes around the popped node (left, right, above, below)
            nextstep = (current[0]+i, current[1]+j)
            # no need to explore this node if it is already checked or in the frontier
            # see what happens if you disable this check here
            if nextstep in self.checked or nextstep in self.frontier:
                print("expanded before: ", nextstep)
                continue
            # check whether this node is out of range of the grid or not
            if 0 <= nextstep[0] < self.grid.row_range:
                if 0 <= nextstep[1] < self.grid.col_range:
                    # check whether this node is an obstacle on the grid or not
                    if not self.grid.nodes[nextstep[0]][nextstep[1]].puddle:
                        if nextstep == self.goal:
                            self.finished = True
                        # add this node into the frontier
                        self.frontier.append(nextstep)
                        # mark this node on the grid as in the frontier
                        self.grid.nodes[nextstep[0]][nextstep[1]].frontier = True
                        # remember the path to reach this node (book-keeping)
                        self.came_from[nextstep] = current
                        print("pushed: ", nextstep)
                    else:
                        print("puddle at: ", nextstep)
                else:
                    print("out of column range: ", nextstep)
            else:
                print("out of row range: ", nextstep)
    def bfs_step(self):
        # check whether the frontier is empty or not
        # no path exists if failed is true
        if not self.frontier:
            self.failed = True
            print("no path")
            return
        current = self.frontier.pop()
        print("popped: ", current)
        # mark the popped node on the grid as checked
        # mark the popped node on the grid as not in the frontier
        # put the popped node into the checked list
        self.grid.nodes[current[0]][current[1]].checked = True
        self.grid.nodes[current[0]][current[1]].frontier = False
        self.checked.append(current)
        # expand the popped node
        for i, j in self.actions:
            # all the nodes around the popped node (left, right, above, below)
            nextstep = (current[0]+i, current[1]+j)
            # no need to explore this node if it is already checked or in the frontier
            if nextstep in self.checked or nextstep in self.frontier:
                print("expanded before: ", nextstep)
                continue
            # check whether this node is out of range of the grid or not
            if 0 <= nextstep[0] < self.grid.row_range:
                if 0 <= nextstep[1] < self.grid.col_range:
                    # check whether this node is an obstacle or not
                    if not self.grid.nodes[nextstep[0]][nextstep[1]].puddle:
                        if nextstep == self.goal:
                            self.finished = True
                        # add this node into the first position of the frontier
                        self.frontier.insert(0, nextstep)
                        # mark this node on the grid as in the frontier
                        self.grid.nodes[nextstep[0]][nextstep[1]].frontier = True
                        # remember the path to reach this node (book-keeping)
                        self.came_from[nextstep] = current
                        print("pushed: ", nextstep)
                    else:
                        print("puddle at: ", nextstep)
                else:
                    print("out of column range: ", nextstep)
            else:
                print("out of row range: ", nextstep)
    def ucs_step(self):
        # [Hint] you can get the cost of a node by node.cost()
        if not self.frontier:
            self.finished = True
            print("no path")
            return
        # pop the node from the heap
        current_node = heappop(self.frontier)[1]
        print("current node: ", current_node)
        # print(self.frontier)
        # get the current cost for the popped node from the dictionary
        current_cost = self.gcost_dict[current_node]
        print("current cost: ", current_cost)
        print("popped: ", current_node)
        # mark the popped node on the grid as checked
        # mark the popped node on the grid as not in the frontier
        # put the popped node into the checked list
        self.grid.nodes[current_node[0]][current_node[1]].checked = True
        self.grid.nodes[current_node[0]][current_node[1]].frontier = False
        self.checked.append(current_node)
        # expand the popped node
        for i, j in self.actions:
            # all the nodes around the popped node (left, right, above, below)
            nextstep = (current_node[0]+i, current_node[1]+j)
            # check whether this node is out of range of the grid or not
            if 0 <= nextstep[0] < self.grid.row_range:
                if 0 <= nextstep[1] < self.grid.col_range:
                    node = self.grid.nodes[nextstep[0]][nextstep[1]]
                    # avoid the obstacle on the grid
                    if not node.puddle:
                        # no need to explore this node if it is already explored before
                        if not nextstep in self.checked:
                            if nextstep == self.goal:
                                self.finished = True
                            nextcost = current_cost + node.cost()
                            # add the cost to the dictionary for this node
                            self.gcost_dict[nextstep] = nextcost
                            # avoid the duplicate in the frontier
                            if not (nextcost, nextstep) in self.frontier:
                                # push to the heap
                                heappush(self.frontier, (self.gcost_dict[nextstep], nextstep))
                                node.frontier = True
                                # remember the path to reach this node (book-keeping)
                                self.came_from[nextstep] = current_node
                                print("pushed: ", nextstep)
                            else:
                                print("already in the frontier: ", nextstep)
                        else:
                            print("checked: ", nextstep)
                    else:
                        print("puddle at: ", nextstep)
                else:
                    print("out of width range: ", nextstep)
            else:
                print("out of length range: ", nextstep)
    # [Hint] you need to declare a heuristic function for Astar
    def hcost(self, n, goal):
        # calculate the Manhattan distance to the goal
        x = abs(n[0] - goal[0])
        y = abs(n[1] - goal[1])
        return 5 * (x + y)
    def astar_step(self):
        if not self.frontier:
            self.finished = True
            print("no path")
            return
        # pop the node from the heap
        current_node = heappop(self.frontier)[1]
        print("current node: ", current_node)
        # get the current cost for the popped node from the dictionary
        current_cost = self.gcost_dict[current_node]
        print("current cost: ", current_cost)
        print("popped: ", current_node)
        # mark the popped node on the grid as checked
        # mark the popped node on the grid as not in the frontier
        # put the popped node into the checked list
        self.grid.nodes[current_node[0]][current_node[1]].checked = True
        self.grid.nodes[current_node[0]][current_node[1]].frontier = False
        self.checked.append(current_node)
        # expand the popped node
        for i, j in self.actions:
            # all the nodes around the popped node (left, right, above, below)
            nextstep = (current_node[0]+i, current_node[1]+j)
            # check whether this node is out of range of the grid or not
            if 0 <= nextstep[0] < self.grid.row_range:
                if 0 <= nextstep[1] < self.grid.col_range:
                    node = self.grid.nodes[nextstep[0]][nextstep[1]]
                    # avoid the obstacle on the grid
                    if not node.puddle:
                        # no need to explore this node if it is already explored before
                        if not nextstep in self.checked:
                            if nextstep == self.goal:
                                self.finished = True
                            nextcost = current_cost + node.cost()
                            # add the cost to the dictionary for this node
                            self.gcost_dict[nextstep] = nextcost
                            # avoid the duplicate in the frontier
                            if not (nextcost + self.hcost(nextstep, self.goal), nextstep) in self.frontier:
                                # push to the heap
                                heappush(self.frontier, (nextcost + self.hcost(nextstep, self.goal), nextstep))
                                node.frontier = True
                                # remember the path to reach this node (book-keeping)
                                self.came_from[nextstep] = current_node
                                print("pushed: ", nextstep)
                            else:
                                print("already in the frontier: ", nextstep)
                        else:
                            print("checked: ", nextstep)
                    else:
                        print("puddle at: ", nextstep)
                else:
                    print("out of width range: ", nextstep)
            else:
                print("out of length range: ", nextstep)
