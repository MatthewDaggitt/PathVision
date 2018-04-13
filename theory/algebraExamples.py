import random
import re

from theory.algebra import *
from theory.pathalogicalAlgebra import pathalogicalAlgebra


def ftimes(f, a, i, j):
	for p in f.split(":"):
		if p == "c":
			return a
		if p[0] == "i":
			return a + int(p[1:])
		if p[0] == "r":
			if len(p) == 1:
				return float("inf")
			else:
				return max(a, int(p[1:]))
		if "t" in p:
			i = p.index("t")
			i1 = int(p[:i])
			i2 = int(p[i+1:])
			if a == i1:
				return i2
		
	print("ERROR " + f + " " + str(a))


# Verification functions

def fVerify(f):

	def matchC(f):
		return re.match("c\Z", f)

	def matchR(f):
		return f == "r" or (re.match("r\d+\Z", f))

	def matchI(f):
		return re.match("i\d+\Z", f)

	def matchT(f):
		return re.match("(\d+)t(\d+)\Z", f) and int(f[:f.index("t")]) <= int(f[f.index("t")+1:])

	if f:
		ps = f.split(":")
		if matchC(ps[-1]) or matchR(ps[-1]) or matchI(ps[-1]):
			for p in ps[:-1]:
				if not matchT(p):
					return False
			return True

	return False

def fRandom():

	r = random.randrange(5)
	
	if r == 0:
		return "c"
	if r == 1:
		return "i" + str(random.randrange(1,5))
	if r == 2:
		r2 = random.randrange(2)
		return str(r2) + "t" + str(random.randrange(r2+1,5)) + ":c"
	return "r"

## Examples

def intRandom():
	r = random.randrange(20)

	if r < 10:
		return r
	else:
		return None


# Example display algebras
def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

minPlus = DisplayAlgebra(
	name          		= "(N, min, +)",
	plus 	       		= min, 
	times         		= lambda x,y,i,j : x + y, 
	invalidRoute  		= float('inf'), 
	identityRoute 		= 0, 
	invalidEdge   		= float('inf'),
	defaultEdge			= 1, 
	randomEdge          = intRandom,
	validateEdgeString 	= isInt,
	parseEdgeString		= int,
	componentAlgebras 	= []
)

maxMin = DisplayAlgebra(
	name          		= "(N, max, min)",
	plus        		= max, 
	times         		= lambda x,y,i,j : min(x,y), 
	invalidRoute  		= 0, 
	identityRoute 		= float('inf'), 
	invalidEdge   		= 0, 
	defaultEdge			= 2, 
	randomEdge          = intRandom,
	validateEdgeString 	= isInt,
	parseEdgeString		= int,
	componentAlgebras	= []
)

shortestWidest = DisplayAlgebra.lexicographicProduct(maxMin, minPlus)

fRing = DisplayAlgebra(
	name          		= "F-custom",
	plus        		= min,
	times         		= ftimes,
	invalidRoute  		= float("inf"),
	identityRoute 		= 0,
	invalidEdge   		= "r",
	defaultEdge			= "c",
	randomEdge          = fRandom,
	validateEdgeString 	= fVerify,
	parseEdgeString		= lambda x : x,
	componentAlgebras	= []
)


examples = [
	minPlus,
	maxMin,
	shortestWidest,
	fRing,
	pathalogicalAlgebra
]