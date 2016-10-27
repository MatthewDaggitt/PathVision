from theory.algebra import *

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

class DisplayAlgebra():

	def __init__(self, A, name, defaultEdge, validate, parse, componentAlgebras):
		self.A = A
		self.name = name
		self.defaultEdge = defaultEdge
		self.validate = validate
		self.parse = parse
		self.components = componentAlgebras

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
			[DA1, DA2]
		)


	@staticmethod
	def trackPaths(DA):
		return DisplayAlgebra(
			Algebra.trackPaths(DA.A),
			DA.name + " + paths",
			DA.defaultEdge,
			DA.validate,
			DA.parse,
			[DA]
		)


def fVerify(f):
	if f:
		if f == "c" or f == "0t4":
			return True
		if f[:3] == "inc" and len(f) == 4:
			return isNumber(f[3])
		if f[0] == "s" and len(f) == 3:
			return isNumber(f[1]) and isNumber(f[2])
	return False


minPlus = DisplayAlgebra(minPlus, "(N, min, +)", 1, isNumber, int, [])
maxMin = DisplayAlgebra(maxMin, "(N, max, min)", 2, isNumber, int, [])
shortestWidest = DisplayAlgebra.lexicographicProduct(maxMin, minPlus)
fRing = DisplayAlgebra(fRing, "F-custom", "c", fVerify, lambda x : x, [])

examples = [
	minPlus,
	maxMin,
	shortestWidest,
	fRing
]