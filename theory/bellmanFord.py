
import functools

def createIdentityMatrix(algebra, size):
	return [[algebra.identityRoute if i == j else algebra.invalidRoute 
				for j in range(size)] 
					for i in range(size)]

def createAdjacencyMatrix(algebra, graph):
	size = len(graph)
	return [[graph[i][j]['weight'] if j in graph[i] else algebra.invalidEdge 
				for j in range(size)] 
					for i in range(size)]

def iterate(algebra, state, idM, adM):
	n = len(state)
	newState = [[0 for _ in range(n)] for _ in range(n)]

	for i in range(n):
		for j in range(n):
			candidateRoutes = [algebra.times(adM[i][k], state[k][j], i, k) for k in range(n)] + [idM[i][j]]
			newState[i][j] = functools.reduce(algebra.plus, candidateRoutes)

	return newState

def solve(algebra, state, idM, adM, limit=1000):
	states = [state, iterate(algebra, state, idM, adM)]
	while len(states) < limit and states[-1] != states[-2]:
		states.append(iterate(algebra, states[-1], idM, adM))
	return states






def singleIterate(algebra, state, idM, adM):
	n = len(state)
	newState = [0 for _ in range(n)]

	for i in range(n):
		candidateRoutes = [algebra.times(adM[i][k], state[k], i, k) for k in range(n)] + [idM[i][0]]
		newState[i] = functools.reduce(algebra.plus, candidateRoutes)

	return newState

def singleSolve(algebra, state, idM, adM, limit=1000):
	states = [state, singleIterate(algebra, state, idM, adM)]
	while len(states) < limit and states[-1] != states[-2]:
		states.append(singleIterate(algebra, states[-1], idM, adM))
	return states