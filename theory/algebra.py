


class Algebra():

	def __init__(self, plus, times, invalidRoute, identityRoute, invalidEdge):
		self.plus = plus
		self.times = times
		self.invalidRoute = invalidRoute
		self.identityRoute = identityRoute
		self.invalidEdge = invalidEdge

	@staticmethod
	def lexicographicProduct(A1, A2):

		def lexPlus(v1, v2):
			s1, t1 = v1
			s2, t2 = v2

			s = A1.plus(s1,s2) 
			if s == s1 and s != s2:
				return (s, t1)
			if s != s1 and s == s2:
				return (s, t2)
			if s == s1 and s == s2:
				return (s, A2.plus(t1,t2))
			raise Exception("The plus operator of " + A1.name + " is not selective!")

		def lexTimes(v1, v2, i):
			s1, t1 = v1
			s2, t2 = v2
			return A1.times(s1, s2, i), A2.times(t1, t2, i)

		lexInvalidRoute = (A1.invalidRoute, A2.invalidRoute)
		lexIdentityRoute = (A1.identityRoute, A2.identityRoute)
		lexInvalidEdge = (A1.invalidEdge, A2.invalidEdge)

		return Algebra(lexPlus, lexTimes, lexInvalidRoute, lexIdentityRoute, lexInvalidEdge)


	@staticmethod
	def trackPaths(A):

		def pathsAdd(v,w):
			if v is None:
				return w
			if w is None:
				return v

			x, p = v
			y, q = w

			r = A.plus(x,y)
			
			if x == y:
				if len(p) < len(q):
					return v
				if len(q) < len(p):
					return w
				if p < q:
					return v
				return w
			if r == x:
				return v
			if r == y:
				return w
			raise Exception("The plus operator of " + A.name + " is not selective!")


		def pathsTimes(e,v,i):
			if e is None or v is None:
				return None

			x, p = v
			if i in p:
				return None

			if A.times(e,x,i) == A.invalidRoute:
				return None

			return (A.times(e,x,i), [i] + p)

		p_one = None

		return Algebra(pathsAdd, pathsTimes, [], None, A.invalidEdge)




## Examples

def ftimes(f, a, _):
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


minPlus = Algebra(min, lambda x,y,_ : x + y, float('inf'), 0, float('inf'))
maxMin = Algebra(max, lambda x,y,_ : min(x,y), 0, float('inf'), 0)
fRing = Algebra(min, ftimes, float("inf"), 0, "r")