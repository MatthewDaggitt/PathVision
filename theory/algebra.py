class Algebra():

	def __init__(self, plus, times, invalidRoute, identityRoute, invalidEdge):
		self.plus 			= plus
		self.times 			= times
		self.invalidRoute 	= invalidRoute
		self.identityRoute 	= identityRoute
		self.invalidEdge 	= invalidEdge

	@staticmethod
	def lexicographicProduct(A, B):

		def lexPlus(v1, v2):
			s1, t1 = v1
			s2, t2 = v2

			s = A.plus(s1,s2) 
			if s == s1 and s != s2:
				return (s, t1)
			if s != s1 and s == s2:
				return (s, t2)
			if s == s1 and s == s2:
				return (s, B.plus(t1,t2))
			raise Exception("The plus operator of " + A.name + " is not selective!")

		def lexTimes(v1, v2, i, j):
			s1, t1 = v1
			s2, t2 = v2
			return A.times(s1, s2, i, j), B.times(t1, t2, i, j)

		return Algebra(
			plus 			= lexPlus,
			times 			= lexTimes,
			invalidRoute 	= (A.invalidRoute, B.invalidRoute), 
			identityRoute 	= (A.identityRoute, B.identityRoute), 
			invalidEdge 	= (A.invalidEdge, B.invalidEdge)
		)


	@staticmethod
	def trackPaths(A):

		invalidRoute  = None
		identityRoute = (A.identityRoute, [])
		invalidEdge   = A.invalidEdge

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


		def pathsTimes(e,v,i,j):
			if e == invalidEdge or v == invalidRoute:
				return invalidRoute

			x, p = v

			# Remove looping paths
			if i in p:
				return invalidRoute

			# Convert invalid routes
			y = A.times(e,x,i,j)
			if y == A.invalidRoute:
				return invalidRoute

			q = [i] + p if p != [] else [i,j]
			return (y,q)

		return Algebra(
			plus 			= pathsAdd,
			times 			= pathsTimes,
			invalidRoute 	= invalidRoute,
			identityRoute 	= identityRoute,
			invalidEdge 	= invalidEdge
		)

class DisplayAlgebra(Algebra):

	def __init__(self, name, plus, times, invalidRoute, identityRoute, invalidEdge, defaultEdge, randomEdge, validateEdgeString, parseEdgeString, componentAlgebras):
		Algebra.__init__(self, plus, times, invalidRoute, identityRoute, invalidEdge)
		self.name         	 	= name
		self.defaultEdge  	 	= defaultEdge
		self.validateEdgeString	= validateEdgeString
		self.parseEdgeString 	= parseEdgeString
		self.componentAlgebras	= componentAlgebras
		self.randomEdge   	 	= randomEdge

	def __repr__(self):
		return self.name

	@staticmethod
	def lexicographicProduct(A, B):
		base = Algebra.lexicographicProduct(A, B)

		return DisplayAlgebra(
			name				= A.name + "-x-" + B.name,
			plus 				= base.plus,
			times 				= base.times,
			invalidRoute        = base.invalidRoute,
			identityRoute       = base.identityRoute,
			invalidEdge         = base.invalidEdge,
			defaultEdge			= [A.defaultEdge , B.defaultEdge],
			randomEdge			= lambda : (A.randomEdge(), B.randomEdge()),
			validateEdgeString	= lambda v : A.validateEdgeString(v[0]) and B.validateEdgeString(v[1]),
			parseEdgeString		= lambda v : (A.parseEdgeString(v[0]), B.parseEdgeString(v[1])),
			componentAlgebras	= [A, B]
		)

	@staticmethod
	def trackPaths(A):
		base = Algebra.trackPaths(A)

		def randomEdge():
			edge = A.randomEdge()
			if edge == A.invalidEdge:
				return base.invalidEdge
			else:
				return edge

		return DisplayAlgebra(
			name				= A.name + " + paths",
			plus 				= base.plus,
			times 				= base.times,
			invalidRoute        = base.invalidRoute,
			identityRoute       = base.identityRoute,
			invalidEdge         = base.invalidEdge,
			defaultEdge			= A.defaultEdge,
			randomEdge			= randomEdge,
			validateEdgeString	= A.validateEdgeString,
			parseEdgeString		= A.parseEdgeString,
			componentAlgebras	= [A]
		)