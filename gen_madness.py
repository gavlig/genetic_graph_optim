#TODO: graphDepth
#TODO: genRandomMat
#TODO: algo itself
#TODO: finish verbose mode
#TODO: converting normal matrix to triangle

import sys
import getopt
import json
import random
#import math

#global in order to make it visible through all functions
verbose = False

def usage():
	print("usage is not implemented yet")
	
# Load file with json-formatted data and parse it 
# return matrix of incidece on success
# [] on failure(could not open file)
def loadGraph(inputFilePath):
	inputFile = open(inputFilePath, "r", encoding="utf-8")
	#check if file is open
	if inputFile is None:
		print("Error: Could not open file {}".format(inputFilePath))
		return []
		
	data = json.load(inputFile)
	mat = data.get("Matrix")
	if mat == None:
		mat = []
	return mat

# Swap two values
def swap(a, b):
	#python, i love you here
	a, b = b, a

# Find distances between every two verts and take max from them
# Return [] if any there are less than 2 vertices
def depth(mat):
	#number of vertices in matrix
	vertCnt = len(mat)
	dists = []
	for i in range(0, vertCnt):
		for j in range(i + 1, vertCnt):
			
			if 2 <= verbose:
				print("\nlooking for path between {} and {}".format(i, j))
			
			max = -1
			dist = pathToVert(mat, i, j)
			if max < dist or -1 == max:
				max = dist
				if 2 <= verbose:
					print("new max distance: {}".format(dist))
	if dist:
		return max(dists)
	else:
		return []

# Define matrix degree(maximum number of edges for one vertex)
# Matrix must be traingular
def matDegree(mat):
	degree = 0
	#number of vertices in matrix
	vertCnt = len(mat)
	
	for i in range(vertCnt):
		buff = 0
		for j in range(i):
			if mat[i][j]:
				buff += 1
		if degree < buff:
			degree = buff
	
	return degree

#
def averMinDist(mat):
	visited = []
	currVert = []
	currVert.insert(0, 0)
	currVert.insert(1, 0)
	dist = 0
	return averMinDist(mat, currVert, visited, dist)

# Recursive. For internal use. Use averMinDist(mat) to get average minimal
# distance for matrix
def averMinDist(mat, visited, currVert, dist):
	global verbose
	#number of vertices in matrix
	vertCnt = len(mat)
	x = currVert[0]
	y = currVert[1]
	#out or range
	if vertCnt - 1 < x or x < 0 or\
		vertCnt - 1 < y or y < 0:
		return False
		#NOTREACHED

	print("current vertex: {}".format(currVert))
	print("visited: {}".format(visited))

	if len(visited) == vertCnt + 1:
		return True
		#NOTREACHED
	else:
		for i in range(x, vertCnt):
			for j in range(i, vertCnt):
				#print("checking vert: {},{}, val: {}".format(i, y, mat[i][y]))
				if 0 < mat[i][y]:# and i + 1 not in visited and i < vertCnt:
					if 0 == len(visited):
						visited.append(i)
					currVert[0] = i + 1
					currVert[1] = i + 1
					#if 0 == len(visited) and 1 == mat[0][0]:
					#	visited.append(1)
					visited.append(i + 1)
					isConnected(mat, currVert, visited)
					if len(visited) == vertCnt + 1:
						return True
	return False

# Find ramification for vertex where vertex number is col
# return False if there is no ramification, else - True
# prevVert = vertex we came from. Connection with prevVert doesn't count as
# ramification
def findRamificationVer(mat, col, row = None, prevVert = -1):
	#number of vertices in matrix
	vertCnt = len(mat)
	if row == None:
		row = col
	#out or range
	if vertCnt - 1 < row or row < 0 or\
		vertCnt - 1 < col or col < 0:
		return False
		#NOTREACHED
	#edge counter. edgeCnt > 1 -> we have a ramification here
	edgeCnt = 0
	for i in range(row, vertCnt):
		if 0 < mat[i][col] and i != prevVert:
			edgeCnt += 1
		if 1 < edgeCnt:
			return True
			#NOTREACHED

	return False
	
# Find ramification for vertex where vertex number is col
# return False if there is no ramification, else - True
# prevVert = vertex we came from. Connection with prevVert doesn't count as
# ramification
def findRamificationHor(mat, col, row, prevVert = -1):
	#number of vertices in matrix
	vertCnt = len(mat)
	#out or range
	if vertCnt - 1 < row or row < 0 or\
		vertCnt - 1 < col or col < 0:
		return False
		#NOTREACHED
	#edge counter. edgeCnt > 1 -> we have a ramification here
	edgeCnt = 0
	for i in range(col, -1, -1):
		if 0 < mat[row][i] and i != prevVert:
			edgeCnt += 1
		if 1 < edgeCnt:
			return True
			#NOTREACHED

	return False
	
# Find ramification for vertex where vertex number is row
# return False if there is no ramification, else - True
# prevVert = vertex we came from. Connection with prevVert doesn't count as
# ramification
def findRamification(mat, row, prevVert = -1):
	col = row + 1
	#number of vertices in matrix
	vertCnt = len(mat)
	#out or range
	if vertCnt - 1 < row or row < 0 or\
		vertCnt - 1 < col or col < 0:
		return False
		#NOTREACHED
	#edge counter. edgeCnt > 1 -> we have a ramification here
	edgeCnt = 0
	for i in range(0, col + 1):
		if 0 < mat[row][i] and i != prevVert:
			edgeCnt += 1
		if 1 < edgeCnt:
			return True
			#NOTREACHED
	for i in range(row, vertCnt):
		if 0 < mat[i][col] and i != prevVert:
			edgeCnt += 1
		if 1 < edgeCnt:
			return True
			#NOTREACHED
	return False

# for internal use only. Part of the pathToVert function
# fndVert - actual vert founded
# orient - horizontal or vertical orientation(0 and 1)
def stepToVert(mat, fndVert, start, dest, path, pathNum, currVert, orient):
	vertCnt = len(mat)
	prevVert = -1
	
	if path and path[pathNum][-1] == vertCnt and 1 != len(path[pathNum]):
		prevVert = path[pathNum][-2]
	elif path and 1 != len(path[pathNum]):
		prevVert = path[pathNum][-1]
	
	if fndVert == dest:
		path[pathNum].append(fndVert)
		#print("i == {} == dest so i'm outta here".format(fndVert, dest))
		if currVert != start:
			return -2
			#NOTREACHED
		else:
			return -1
			#NOTREACHED
	newPathNum = pathNum
	ram = 0
	#a piece of legendary crappo-messcode
	if orient:
		ram = findRamificationVer(mat, currVert, fndVert - 1, prevVert)
		if not ram:
			ram = findRamificationHor(mat, currVert - 1, currVert - 1, prevVert)
	elif not ram:
		ram = findRamificationHor(mat, fndVert, currVert, prevVert)
		if not ram:
			ram = findRamificationVer(mat, currVert + 1, currVert + 1, prevVert)

	"""
	if orient:
		ram = findRamificationVer(mat, currVert, fndVert, prevVert)
		if not ram:
			ram |= findRamificationHor(mat, currVert, fndVert - 1, prevVert)
	elif not ram:
		print(currVert, fndVert)
		ram |= findRamificationVer(mat, fndVert + 1, currVert, prevVert)
		if not ram:
			ram |= findRamificationHor(mat, currVert, fndVert, prevVert)
	"""
	#print("ram is {}".format(ram))
	#ramification found so we create new instance of path to compare
	#with
	if ram:
		#creating new instance of path
		newPath = path[pathNum][:]
		path.append(newPath)
		newPathNum = len(path) - 1
		#print("ramification occurred for pathNum: {}".format(pathNum))
	#print("moving to vert #{}".format(fndVert))
	path[newPathNum].append(fndVert)
	#going recursive
	#print("oldPathNum:{} newPathNum:{} path:{}".format(pathNum, newPathNum, path[newPathNum]))
	pathToVert(mat, start, dest, path, fndVert, newPathNum)

# Find distance from one vertex to another
# distance == len(path)
# path should be two-dimensional list
# path[0][] is the shortest path
def pathToVert(mat, start, dest, path = None, currVert = None, pathNum = 0):
	#number of vertices in matrix
	#print("currVert: {}".format(currVert))
	global verbose
	
	vertCnt = len(mat)
	if None == currVert:
		currVert = start
	if None == path:
		path = []
		path.insert(0, [])
	if start == currVert and (None == path or not path[0]):
		path[0].append(start)
	shifted = 0
	
	#horizontal
	if 0 < currVert and currVert <= vertCnt and path[pathNum][-1] != dest:
		# indexes are shifted because we use triangular matrix
		currVert -= 1
		shifted = 1
		for i in range(currVert, -1, -1):
			if 0 < mat[currVert][i] and (i not in path[pathNum] or i == dest):
				out = stepToVert(mat, i, start, dest, path, pathNum, currVert, 0)
				if -2 == out:
					return
				elif -1 == out:
					break
	#vertical
	if 0 <= currVert and currVert < vertCnt and path[pathNum][-1] != dest:
		if shifted:
			currVert += 1
			shifted = 0
		for i in range(currVert, vertCnt):
			if 0 < mat[i][currVert] and (i + 1 not in path[pathNum] or i + 1 == dest) :
				out = stepToVert(mat, i + 1, start, dest, path, pathNum, currVert, 1)
				if -2 == out:
					return
				elif -1 == out:
					break
	
	if shifted:
		currVert += 1
	
	#we returned to start point so it's time to find optimal path
	if 1 < len(path[0]) and currVert == path[0][0]:
		
		if 2 <= verbose:
			print("\npathToVert result:\n")
			print("paths found:{}".format(len(path)))
			
		pathNum = -1
		length = -1
		
		#if 2 <= verbose:
		#	print("#0; path:{}".format(path[0]))
			
		for i in range(0, len(path)):
			
			if 2 <= verbose:
				print("#{}; path:{}".format(i, path[i]))
				
			currLen = len(path[i])
			if currLen < length and path[i][-1] == dest and pathNum != -1:
				pathNum = i
				length = currLen
			elif pathNum == -1 and path[i][-1] == dest:
				pathNum = i
				length = currLen
				
		if 2 <= verbose:
			print("best path is #{}".format(pathNum))
			
		return len(path[pathNum])

#
def minimizeMat(minType):
	print("minimizeMat is not implemented yet")

# Overloaded
# Check if graph is connected(if we can reach any random vertex from another)
def isConnected(mat):
	visited = []
	currVert = []
	currVert.insert(0, 0)
	currVert.insert(1, 0)
	return isConnected(mat, currVert, visited)

# Check if graph is connected(if we can reach any random vertex from another)
# recursive
# currVert[x][y] - current position in graph
# visited - list of visited vertices(list of vertex numbers)
def isConnected(mat, currVert, visited):
	#number of vertices in matrix
	vertCnt = len(mat)
	x = currVert[0]
	y = currVert[1]
	#out or range
	if vertCnt - 1 < x or x < 0 or\
		vertCnt - 1 < y or y < 0:
		return False
		#NOTREACHED

	#print("current vertex: {}".format(currVert))
	#print("visited: {}".format(visited))

	if len(visited) == vertCnt + 1:
		return True
		#NOTREACHED
	else:
		for i in range(x, vertCnt):
			#print("checking vert: {},{}, val: {}".format(i, y, mat[i][y]))
			if 0 < mat[i][y] and i + 1 not in visited and i < vertCnt:
				if 0 == len(visited):
					visited.append(i)
				currVert[0] = i + 1
				currVert[1] = i + 1
				visited.append(i + 1)
				return isConnected(mat, currVert, visited)
	return False

# Generate a random binary triangular matrix
# Example: 
# genRandomMat(4) will return something like
# [0]
# [0, 1]
# [1, 1, 0]
# [0, 1, 0, 1]
def genRandomMat(size, limit):
	bit = 0
	mat = []
	for i in range(size):
		degree = 0
		mat.insert(i, [])
		for j in range(i + 1):
			num = random.random()
			if 0.5 <= num and degree <= limit:
				bit = 1
				degree += 1
			else:
				bit = 0
			mat[i].insert(j, bit)

	return mat
	
# Perform bit-flip mutation on triangular matrix which will be processed as
# binary vector
def bitFlipMutate(mat):
	#number of vertices in matrix
	vertCnt = len(mat)
	#matrix element count(mat should ONLY be triangular)
	elCnt = (vertCnt * vertCnt) / 2
	#probability of mutation
	#token from "Luke S. Essentials of Metaheuristics" p.30
	p = 1 / size
	for i in range(vertCnt):
		for j in range(i + 1):
			num = random.random()
			if num <= p:
				mat[i][j] = -mat[i][j]
	return mat

# Perform One-Point Crossover("Luke S. Essentials of Metaheuristics" p.30)
# mat0 and mat1 MUST have equal size, otherwise [], [] will be returned
def crossover(mat0, mat1):
	#number of vertices in matrix
	vertCnt = len(mat0)
	if len(mat1) != vertCnt:
		return [], []
		#NOTREACHED
		
	#matrix element count(mat should ONLY be triangular)
	elCnt = (vertCnt * vertCnt) / 2
	
	pointSize = random.randrange(elCnt)
	for i in range(pointSize, elCnt):
		for j in range(i + 1):
			swap(mat0[i][j], mat1[i][j])

	return mat0, mat1

# return 0 - program finished successfully
#		-1 - an exception occurred
#		 1 - could not open file
#		 2 - input matrix is empty
def main(argv = None):
	if argv is None:
		argv = sys.argv
	try:
		opts, args = getopt.getopt(
			argv[1:],\
			"hi:v:m:l:",\
			["help", "input=", "min-type=", "limit=", "verbose="])
	except getopt.GetoptError as err:
		print(err)
		usage()
		return -1
		#NOTREACHED
		
	if len(opts) == 0:
		usage()
		return 0
		#NOTREACHED
		
	output = None
	inputFilePath = ""
	
	"""
	minType: 0 - minimizing average min distance with fixed vertex degree
			 1 - minimizing average min distance and vert degree for fixed depth
	default - 0
	"""
	
	minType = 0
	limit = 0
	global verbose
	
	for opt, arg in opts:
		if opt in ("-v", "--verbose"):
			verbose = int(arg)
		elif opt in ("-h", "--help"):
			usage()
			return 0
			#NOTREACHED
		elif opt in ("-i", "--input"):
			inputFilePath = arg
		elif opt in ("-m", "--min-type"):
			minType = arg
		elif opt in ("-l", "--limit"):
			limit = arg
		else:
			usage()
			return 0
			#NOTREACHED

	#simple check on empty args
	if inputFilePath == "" or limit == 0:
		usage()
		return 0
		#NOTREACHED
		
	matVertsNum = 0
	mat = []
	matEdges = 0
	matDepth = 0
	matAverMinDist = 0 
	matDegree = 0
	mat = loadGraph(inputFilePath)
	
	#matrix was empty of file doesn't exist
	if 0 == len(mat):
		return 2
		#NOTREACHED

	if verbose:
		print("Matrix len is: {}\nInitial matrix:".format(len(mat)))
		for i in range(len(mat)):
			print("matrix[{}]: {}".format(i, mat[i]))
			
	matDepth = depth(mat)
	print("depth is {}".format(matDepth))
	
	"""
	visited = []
	currVert = []
	currVert.insert(0, 0)
	currVert.insert(1, 0)
	if isGraphConnected(mat, currVert, visited):
		print("Graph is connected")
	else:
		print("Graph is not connected")
	"""
	
	if not minType:
		print("minType 0 is not yet implemented")
	else:
		print("minType 1 is not yet implemented")

if __name__ == "__main__":
	#TODO: add descriptions for errors
	ret = main()
	#add description here
	sys.exit(ret)

#
#
#
