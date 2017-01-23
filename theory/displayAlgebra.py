import random
import re

from theory.algebra import *

class DisplayAlgebra():

	def __init__(self, A, name, defaultEdge, validate, parse, componentAlgebras, randomEdge):
		self.A = A
		self.name = name
		self.defaultEdge = defaultEdge
		self.validate = validate
		self.parse = parse
		self.components = componentAlgebras
		self.randomEdge = randomEdge

	def __repr__(self):
		return self.name



	@staticmethod
	def lexicographicProduct(DA1, DA2):
		return DisplayAlgebra(
			Algebra.lexicographicProduct(DA1.A, DA2.A),
			DA1.name + "-x-" + DA2.name,
			[DA1.defaultEdge , DA2.defaultEdge],
			lambda v : DA1.validate(v[0]) and DA2.validate(v[1]),
			lambda v : (parse(v[0]) , parse(v[1])),
			[DA1, DA2],
			lambda : (DA1.randomEdge(), DA2.randomEdge())
		)


	@staticmethod
	def trackPaths(DA):
		return DisplayAlgebra(
			Algebra.trackPaths(DA.A),
			DA.name + " + paths",
			DA.defaultEdge,
			DA.validate,
			DA.parse,
			[DA],
			DA.randomEdge
		)


# Verification functions

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
	return None

def intRandom():
	r = random.randrange(20)

	if r < 10:
		return r
	else:
		return None


# Example display algebras

minPlus = DisplayAlgebra(minPlus, "(N, min, +)", 1, isInt, int, [], intRandom)
maxMin = DisplayAlgebra(maxMin, "(N, max, min)", 2, isInt, int, [], intRandom)
shortestWidest = DisplayAlgebra.lexicographicProduct(maxMin, minPlus)
fRing = DisplayAlgebra(fRing, "F-custom", "c", fVerify, lambda x : x, [], fRandom)

examples = [
	minPlus,
	maxMin,
	shortestWidest,
	fRing
]