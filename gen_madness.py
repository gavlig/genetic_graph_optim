#TODO: second minimization
#TODO: multiprocessing for evolution process

import sys
import getopt
import random
import os
import multiprocessing
import math

#global in order to make it visible through all functions
verbose = False

def usage():
	print("available keys:\n"
        "--help\n"
        "--min-type=0-1\n"
        "--limit=1-inf\n"
        "--verbose=0-3\n"
        "--verts=3-inf\n"
		"--thrCount=1-inf\n"
        "--averMinDist=1-inf\n"
        "--popSize=2-inf\n"
        "--popGap1-inf\n\n"
		"where inf = infinite(theoretically. limited by your sanity and resources)\n\n"
		"short version: -h -v -m -l -ve -thc\n\n"
		"default values: \n"
		"min-type = 0\n"
		"limit = 4\n"
		"verbose = 0\n"
		"verts = 8\n"
		"thrCount = 10\n"
		"averMinDist=1.5\n"
		"popSize=20\n"
		"popGap=50\n"
		)

	
	
# Swap two values
def swap(a, b):
	#python, i love you here
	a, b = b, a

# Find distances between every two verts and take max from them
# Return [] if any there are less than 2 vertices
def depth(mat):
	if 1 <= verbose:
		print("\n   Calculating graph depth\n")
	
	#number of vertices in matrix
	vertCnt = len(mat)
	max = -1
	for i in range(0, vertCnt):
		for j in range(i + 1, vertCnt):

			if 2 <= verbose:
				print("\nlooking for path between {} and {}".format(i, j))

			dist = pathToVert(mat, i, j)
			if max < dist or -1 == max:
				max = dist
				if 2 <= verbose:
					print("new max distance: {}".format(dist))
	if dist:
		return max
	else:
		return -1

# Check matrix degree(maximum number of edges for one vertex)
# Matrix must be traingular
#
# return False - degree is bigger than limit
#		 True - degree is ok
def checkDegree(mat, limit):
	degree = 0
	#number of vertices in matrix
	vertCnt = len(mat)
	
	degree = []
	for i in range(vertCnt + 1):
		degree.append(0)
		
	for i in range(vertCnt):
		for j in range(i + 1):
			if mat[i][j]:
				degree[i + 1] += 1
				if limit < degree[i + 1]:
					return False
	for i in range(vertCnt):
		for j in range(vertCnt - 1, i - 1, -1):
			if mat[j][i]:
				degree[i] += 1
				if limit < degree[i]:
					return False 
	return degree

# get average minimal distance for graph
# modified for threading
def averMinDist(graph):
	if 1 <= verbose:
		print("\n   Calculating average minimal distance for graph\n")
	#number of vertices in matrix
	vertCnt = len(graph)
	distSum = 0
	distCnt = 0
	
	for i in range(0, vertCnt):
		for j in range(i + 1, vertCnt):
			
			if 2 <= verbose:
				print("\nlooking for path between {} and {}".format(i, j))
			
			dist = pathToVert(graph, i, j)
			if dist:
				distSum += dist
				distCnt += 1
				if 2 <= verbose:
					print("its length: {}".format(dist))
	if distSum and 0 != distCnt:
		return  distSum / distCnt
	else:
		return -1
		
# get average minimal distance for graph
# modified for threading
def averMinDistThr(graphNum, graph, queue):
	if 1 <= verbose:
		print("\n   Calculating average minimal distance for graph\n")
	#number of vertices in matrix
	vertCnt = len(graph)
	distSum = 0
	distCnt = 0
	
	for i in range(0, vertCnt):
		for j in range(i + 1, vertCnt):
			
			if 2 <= verbose:
				print("\nlooking for path between {} and {}".format(i, j))
			
			dist = pathToVert(graph, i, j)
			if dist:
				distSum += dist
				distCnt += 1
				if 2 <= verbose:
					print("its length: {}".format(dist))
	if distSum and 0 != distCnt:
		queue.put([graphNum, distSum / distCnt])
	else:
		queue.put([-1, -1])
	
# Find ramification for vertex where vertex number is row
# return False if there is no ramification, else - True
# row = current vertex number - 1
# prevVert = vertex we came from. Connection with prevVert doesn't count as
# ramification
def findRamification(mat, path, pathNum, row):
	#number of vertices in matrix
	vertCnt = len(mat)
	pathLen = len(path[pathNum])
	
	verts = []
	#making a list of visited verts(to avoid them in search of ramification)
	currPath = path[pathNum]
	for i in range(0,  len(path)):
		if i == pathNum:
			continue
		similarPath = [j for j, k in zip(currPath, path[i]) if j == k]	
		if similarPath == currPath and pathLen < len(path[i]):
			verts.append(path[i][pathLen])
	#out or range
	#-1 can appear when currVert is 0 and direction was vertical(see pathToVert)
	if vertCnt - 1 < row or row < -1:
		return False
		#NOTREACHED
		
	#edge counter. edgeCnt > 1 means we have a ramification here
	edgeCnt = 0
	for i in range(0, row + 1):
		#if 0 < mat[row][i] and i != prevVert and i not in verts:
		if 0 < mat[row][i] and i not in currPath and i not in verts:
			edgeCnt += 1
		if 1 < edgeCnt:
			return True
			#NOTREACHED
	
	#incrementing because row + 1 == col == actual vertex num
	row += 1
	for i in range(row, vertCnt):
		#if 0 < mat[i][row] and i + 1 != prevVert and i + 1 not in verts:
		if 0 < mat[i][row] and i + 1 not in currPath and i + 1 not in verts:
			edgeCnt += 1
		if 1 < edgeCnt:
			return True
			#NOTREACHED
			
	return False
	
# for internal use only. Part of the pathToVert function
# fndVert - actual vert founded
# orient - horizontal or vertical orientation(0 and 1)
def stepToVert(mat, fndVert, start, dest, path, pathNum, currVert, orient):
	#next vertex is the one we are looking for!
	if fndVert == dest:
		path[pathNum].append(fndVert)
		if currVert != start:
			return -2
			#NOTREACHED
		else:
			return -1
			#NOTREACHED
	newPathNum = pathNum
	ram = 0

	#it depends on the direction of matrix checking(see pathToVert)
	vertForRam = currVert
	if orient:
		vertForRam -= 1
	
	ram = findRamification(mat, path, pathNum, vertForRam)

	#ramification found so we create new instance of path to compare
	#with
	if ram:
		#creating new instance of path
		newPath = path[pathNum][:]
		path.append(newPath)
		newPathNum = len(path) - 1
	path[newPathNum].append(fndVert)
	#going recursive
	pathToVert(mat, start, dest, path, fndVert, newPathNum)

# Find distance from one vertex to another
# distance == len(path) - 1
# path should be two-dimensional list
def pathToVert(mat, start, dest, path = None, currVert = None, pathNum = 0):
	#number of vertices in matrix
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
			if path[pathNum][-1] == dest:
				break
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
			if path[pathNum][-1] == dest:
				break
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
		
		if 3 <= verbose:
			print("\npathToVert result:\n")
			print("paths found:{}".format(len(path)))
			
		pathNum = -1
		length = -1
		
		for i in range(0, len(path)):
			
			if 3 <= verbose:
				print("#{}; path:{}".format(i, path[i]))
				
			currLen = len(path[i])
			if currLen < length and path[i][-1] == dest and pathNum != -1:
				pathNum = i
				length = currLen
			elif pathNum == -1 and path[i][-1] == dest:
				pathNum = i
				length = currLen
				
		if 3 <= verbose:
			print("best path is #{}".format(pathNum))
			
		return len(path[pathNum]) - 1
	else:
		return 0

# Tournament selection of the individual from the whole population
# pop - population(vector of graphs)
# tSize - size of the tournament 
#
# return None if input parameters are invalid
#		 fittest graph on success
#
# reference - Luke S. Essentials of Metaheuristics" p.38
def selectInd(pop, tSize):
	if not pop or not tSize:
		return None
		#NOTREACHED
	
	popLen = len(pop)
	
	if popLen <= tSize:
		tSize = popLen - 1
		
	best = [-1, []]
	best[0] = random.randint(0, popLen - 1)
	best[1] = averMinDist(pop[best[0]])
	
	#looking for the fittest individual
	for i in range(1, tSize):
		if best[0] == i:
			continue
		num = random.randint(0, popLen - 1)
		AMD = averMinDist(pop[num])
		if AMD < best[1]:
			best[0] = i
			best[1] = AMD
	
	#popping it from vector
	best[1] = pop.pop(best[0])
	
	return best[1]

# Run func with funcArgs which doesn't change during cycle:
#
# thrCnt - number of threads we want to run at the same time
# ttlThrCnt - basically, it should be len(funcArg) as far as
# funcArgs - list of arguments to be processed in cycle
# func - function itself. Must consider last argument as queue
def runInThreads(ttlThrCnt, thrCnt, func, funcArgs):
	processes = []
	result = []
	resultQueue = multiprocessing.Queue()
	args_ = []
	for i in range(len(funcArgs)):
		args_.append(funcArgs[i])
	args_.append(resultQueue)
	
	procCnt = ttlThrCnt	#process quantity
	procCntMult = 1		#process quantity multiplier
	if thrCnt < ttlThrCnt:
		procCntMult = math.ceil(ttlThrCnt / thrCnt)
		print("procCntMult:{}".format(procCntMult))
		procCnt = thrCnt
		print("procCnt:{}".format(procCnt))

	itNum = 0			#iteration number
	for n in range(0, procCntMult):
		dec = 0			#inner cycle iteration num
		for i in range(0, procCnt):
			process = multiprocessing.Process(
				target = func,
				args = args_
				#args = [funcArgs, resultQueue]
			)
			process.start()
			processes.append(process)
			
			print("new process #{} started".format(itNum))
			
			itNum += 1
			dec += 1
			if ttlThrCnt < itNum + 1:
				break

		#wait until any of the proccess have `.put()` a result
		#while not resultQueue.empty():
		for i in range(dec):
			result.append(resultQueue.get())
			print("process ended")
			
	for process in processes: #then kill them all off
		process.terminate()
		
	return result


# Run func with funcArg as list in threads where:
#
# thrCnt - number of threads we want to run at the same time
# ttlThrCnt - basically, it should be len(funcArg) as far as
# funcArg - list of values to be processed in cycle
# func - function itself. Must consider last argument as queue
def runInThreadsIt(ttlThrCnt, thrCnt, func, funcArg):
	processes = []
	result = []
	resultQueue = multiprocessing.Queue()
	
	procCnt = ttlThrCnt	#process quantity
	procCntMult = 1		#process quantity multiplier
	if thrCnt < ttlThrCnt:
		procCntMult = math.ceil(ttlThrCnt / thrCnt)
		procCnt = thrCnt

	itNum = 0			#iteration number
	for n in range(0, procCntMult):
		dec = 0			#inner cycle iteration num
		for i in range(0, procCnt):
			process = multiprocessing.Process(
				target = func,
				args = [itNum, funcArg[itNum], resultQueue]
			)
			process.start()
			processes.append(process)
			
			print("new process #{} started".format(itNum))
			
			itNum += 1
			dec += 1
			if ttlThrCnt < itNum + 1:
				break

		#wait until any of the proccess have `.put()` a result
		#while not resultQueue.empty():
		for i in range(dec):
			result.append(resultQueue.get())
			print("process ended")
			
	for process in processes: #then kill them all off
		process.terminate()
		
	return result

# Minimize matrix by the rules of minType == 0 (see comments in main)
# mat - triangular matrix to optimize
# limit - fixed vertex degree
# popSize - the size of one population(should be even)
# generLim - limit of generations
# minType - see comments in main
#
# return 0 - matrix was successfully minimized
#
# reference - Luke S. Essentials of Metaheuristics" p.29
def minimizeMat0(graphSize, target, limit, popSize, generLim, thrLim):
	
	#sanity check
	if not graphSize or int(popSize) <= 0 or int(generLim) <= 0:
		return 1
		#NOTREACHED
	
	pop = []				#population
	
	print("\n   Starting population generation\n")
	
	#filling it in
	args = [graphSize, limit]
	result = runInThreads(popSize, thrLim, genRandomMat0Thr, args)
	for i in range(len(result)):
		pop.append(result[i])

	print("\n   Population generated\n")

	best = [None, -1]		#the best individual with lowest average
							#minimal distance (graph, AMD);
	gen = 0					#generation number;
	AMD = -1				#average minimal distance;

	#main loop
	while True:
		
		#
		#assess fitness
		#
		
		result = runInThreadsIt(popSize, thrLim, averMinDistThr, pop)
		
		for i in range(len(result)):
			if result[i][1] < best[1] or -1 == best[1]:
					best[0] = pop[result[i][0]]
					best[1] = result[i][1]

		print("\n   Fitness assessed\n")
				
		if best[1] <= target:
			print("\n   Target reached before generation number exceeded. "
				"Reached AMD = {}\n".format(best[1]))
			return best[0]
			#NOTREACHED
		
		newPop = []
		for i in range(int(popSize / 2)):
			
			print("evolution iteration: {}".format(i))
			
			#tournament size was taken from
			#Luke S. Essentials of Metaheuristics" p.38
			parentA = selectInd(pop, 2)
			parentB = selectInd(pop, 2)
			childA, childB = crossover(parentA, parentB)
			if None == childA and None == childB:
				print("Error: crossover operation failed with params: {} {}".
					format(parentA, parentB))
					
			childA, childB = bitFlipMutate(childA), bitFlipMutate(childB)
			if None == childA and None == childB:
				print("Error: mutation operation failed with params: {} {}".
					format(childA, childB))
			
			if isConnected(childA) and checkDegree(childA, limit):
				newPop.append(childA)
			else:
				newPop.append(genRandomMat0(graphSize, limit))
			
			if isConnected(childB) and checkDegree(childB, limit):
				newPop.append(childB)
			else:
				newPop.append(genRandomMat0(graphSize, limit))	
			
		pop = newPop
		gen += 1

		print("generation number: {}\nfittest AMD = {}".format(gen, best[1]))

		if generLim <= gen:
			print("\n   Target not reached. Generation number exceeded. "
				"Reached AMD = {}\n".format(best[1]))
			return best[0]
	

# Check if graph is connected(if we can reach any random vertex from another)
def isConnected(mat):
	if 1 <= verbose:
		print("\n   Checking if given graph is connected\n")
	visited = []
	currVert = []
	currVert.insert(0, 0)
	currVert.insert(1, 0)
	return isConnected_(mat, currVert, visited)

# Check if graph is connected(if we can reach any random vertex from another)
# recursive
# currVert[x][y] - current position in graph
# visited - list of visited vertices(list of vertex numbers)
def isConnected_(mat, currVert, visited):
	#number of vertices in matrix
	vertCnt = len(mat)
	x = currVert[0]
	y = currVert[1]
	#out or range
	if vertCnt - 1 < x or x < 0 or\
		vertCnt - 1 < y or y < 0:
		return False
		#NOTREACHED

	if len(visited) == vertCnt + 1:
		return True
		#NOTREACHED
	else:
		for i in range(x, vertCnt):
			if 0 < mat[i][y] and i + 1 not in visited and i < vertCnt:
				if 0 == len(visited):
					visited.append(i)
				currVert[0] = i + 1
				currVert[1] = i + 1
				visited.append(i + 1)
				if isConnected_(mat, currVert, visited):
					return True
					#NOTREACHED
	
	#checking in case last visited vertex was in first column
	if len(visited) == vertCnt + 1:
		return True
	else:
		return False

# Generate a simple random binary triangular matrix
# Example: 
# genRandomMat(4) will return something like
# [0]
# [0, 1]
# [1, 1, 0]
# [0, 1, 0, 1]
def genRandomMat(size):
	bit = 0
	mat = []
	for i in range(size):
		mat.insert(i, [])
		for j in range(i + 1):
			num = random.random()
			if 0.5 <= num:
				bit = 1
			else:
				bit = 0
			mat[i].insert(j, bit)

	return mat

def genRandomMat0(size, limit):
	bit = 0
	mat = []
	for i in range(size):
		mat.insert(i, [])
		for j in range(i + 1):
			mat[i].insert(j, 0)

	edge = []
	for i in range(0, size + 1):
		edge.insert(i, [])
	
	for i in range(0, size + 1):
		edge.insert(i, [])
		checked = []
		while len(edge[i]) < limit:
			num = random.randrange(0, size + 1)
			if num not in edge[i] and num != i and len(edge[num]) < limit:
				edge[i].append(num)
				edge[num].append(i)
			if num not in checked:
				checked.append(num)
			if len(checked) == size + 1:
				break

	#vertical
	for i in range(size):
		for j in range(size - 1, i - 1, -1):
			if j + 1 in edge[i]:
				mat[j][i] = 1

	return mat

# Generate a random binary triangular matrix sutisfying first 
# minimization type(minType == 0, vertex degree must be fixed)
def genRandomMat0Thr(size, limit, queue):
	res = False
	while not res:
		mat = genRandomMat0(size, limit)
		if isConnected(mat):
			res = True
	queue.put(mat)
	
# Perform bit-flip mutation on triangular matrix which will be processed as
# binary vector
def bitFlipMutate(mat):
	if not mat or not len(mat):
		return None
	#number of vertices in matrix
	vertCnt = len(mat)
	#matrix element count(mat should ONLY be triangular)
	elCnt = (vertCnt * vertCnt) / 2
	#probability of mutation
	#token from "Luke S. Essentials of Metaheuristics" p.30
	p = 1 / elCnt
	for i in range(vertCnt):
		for j in range(i + 1):
			num = random.random()
			if num <= p:
				#flipping to opposite(0 to 1 and 1 to 0)
				mat[i][j] = mat[i][j] ^ 1
	return mat

# Perform One-Point Crossover("Luke S. Essentials of Metaheuristics" p.30)
# mat0 and mat1 MUST have equal size, otherwise None, None will be returned
def crossover(mat0, mat1):
	#number of vertices in matrix
	vertCnt = len(mat0)
	if not len(mat1) or len(mat1) != vertCnt:
		return None, None
		#NOTREACHED
		
	#matrix element count(mat should ONLY be triangular)
	elCnt = int((vertCnt * vertCnt) / 2)
	
	pointSize = random.randrange(elCnt)
	cnt = 0
	for i in range(vertCnt):
		for j in range(i + 1):
			swap(mat0[i][j], mat1[i][j])
			cnt += 1
			if pointSize < cnt:
				break

	return mat0, mat1

# return 0 - program finished successfully
#		-1 - an exception occurred
def main(argv = None):
	if argv is None:
		argv = sys.argv
	try:
		opts, args = getopt.getopt(
			argv[1:],\
			"hv:m:l:ve:thc:amd:ps:pg:",\
			[
				"help",
				"min-type=",
				"limit=",
				"verbose=",
				"verts=",
				"thrCount=",
				"averMinDist=",
				"popSize=",
				"popGap="
			]
		)
	except getopt.GetoptError as err:
		print(err)
		usage()
		return -1
		#NOTREACHED
		
	if len(opts) == 0:
		usage()
		print("\n\n")
		
	"""
	minType: 0 - minimizing average min distance with fixed vertex degree
			 1 - minimizing average min distance and vert degree for fixed depth
	default - 0
	"""
	
	minType = 0
	limit = 4
	global verbose
	verbose = 0					#default
	verts = 8					#default
	thrCount = 10				#default
	amd = 1.5
	popSize = 20
	popGap = 50
	
	for opt, arg in opts:
		if opt in ("-v", "--verbose"):
			verbose = int(arg)
		elif opt in ("-h", "--help"):
			usage()
			return 0
			#NOTREACHED
		elif opt in ("-m", "--min-type"):
			minType = arg
		elif opt in ("-l", "--limit"):
			limit = arg
		elif opt in ("-ve", "--verts"):
			verts = arg
		elif opt in ("-thc", "--thrCount"):
			thrCount = arg
		elif opt in ("-amd", "--averMinDist"):
			amd = arg
		elif opt in ("-ps", "--popSize"):
			popSize = arg
		elif opt in ("-pg", "--popGap"):
			popGap = arg
		else:
			usage()
			#NOTREACHED

	#simple check on empty args
	if limit == 0:
		usage()
		return 0
		#NOTREACHED
	
	random.seed()
	
	best = minimizeMat0(verts, amd, limit, popSize, popGap, thrCount)
	
	print("minimization result:")
	for i in range(len(best)):
		print(best[i])	

if __name__ == "__main__":
	#TODO: add descriptions for errors
	ret = main()
	#add description here
	sys.exit(ret)

#
#
#
