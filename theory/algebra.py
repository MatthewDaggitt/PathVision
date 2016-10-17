


class Algebra():

	def __init__(self, plus, times, zero, one):
		self.plus = plus
		self.times = times
		self.zero = zero
		self.one = one

	@staticmethod
	def lexicographicProduct(A1, A2):

		def l_plus(v1, v2):
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

		def l_times(v1, v2, i):
			s1, t1 = v1
			s2, t2 = v2
			return A1.times(s1, s2, i), A2.times(t1, t2, i)

		l_zero = (A1.zero, A2.zero)
		l_one = (A1.one, A2.one)

		return Algebra(l_plus, l_times, l_zero, l_one)


	@staticmethod
	def trackPaths(A):

		def p_add(v,w):
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


		def p_times(e,v,i):
			if e is None or v is None:
				return None

			x, p = v
			
			if i in p:
				return None

			return (A.times(e,x,i), [i] + p)

		p_one = None

		return Algebra(p_add, p_times, [], None)


minPlus = Algebra(min, lambda x,y,_ : x + y, float('inf'), 0)
maxMin = Algebra(max, lambda x,y,_ : min(x,y), 0, float('inf'))