
import functools

def iterate(algebra, state, idM, adM):

	n = len(state)
	newState = [[algebra.zero for _ in range(n)] for _ in range(n)]

	for i in range(n):
		for j in range(n):
			candidateRoutes = [algebra.times(adM[i][k], state[k][j], i) for k in range(n)] + [idM[i][j]]
			newState[i][j] = functools.reduce(algebra.plus, candidateRoutes)

	return newState