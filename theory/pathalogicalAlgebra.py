from theory.algebra import *

def plus(x, y):
	if x is None:
		return y
	if y is None:
		return x

	lx, px = x
	ly, py = y

	if lx < ly:
		return x
	if ly < lx:
		return y

	if len(px) < len(py):
		return x
	if len(py) < len(px):
		return y

	if px < py:
		return x
	else:
		return y

def times(f, x, i, j):
	if x is None:
		return None

	if f is None:
		return None

	l, p = x

	if i in p:
		return None

	# Distributivity violation
	if j % 2 == 0 and p == (j,j-1,0):
		return None

	# Block routes from gadget leg
	if j % 2 == 1 and p == (j,0) and i != j + 1:
		return None

	# Only accept routes from preceeding neighbour in junk phase
	if len(p) > 2 and (j != i - 1 and i != p[-2]+1):
		return None

	if j == 0:
		nl = i
	else:
		nl = l
	np = (i,) + p if p != () else (i,j)
	return (nl , np)


pathalogicalAlgebra = DisplayAlgebra(
	name          		= "Pathalogical",
	plus        		= plus,
	times         		= times,
	invalidRoute  		= None,
	identityRoute 		= (0 , ()),
	invalidEdge   		= None,
	defaultEdge			= "e",
	randomEdge          = lambda : "e",
	validateEdgeString 	= lambda f : f == "e",
	parseEdgeString		= lambda x : x,
	componentAlgebras	= []
)





def generatePathalogicalAdjacencyMatrix(n):
	adM = [[None for _ in range(n)] for _ in range(n)]

	# Create distributivity violations
	for i in range(0,n,2):
		adM[i][0] = "e"
		adM[i-1][0] = "e"
		adM[i][i-1] = "e"

	# Create initial violation spreading links
	for i in range(2,n,2):
		for j in range(i+1,n):
			adM[j][i] = "e"

	# Create violation circulation links
	for i in range(2,n,2):
		for j in range(i+1,n):
			if j != n - 1:
				adM[j+1][j] = "e"
			else:
				adM[i+1][j] = "e"

	return adM