from itertools import permutations

class Order():

	def __init__(self, labels):
		self.labels = labels
		self.index = {l:i for i,l in enumerate(labels)}
		self.lookup = [["x" if x == y else 0 for y in range(len(labels))] for x in range(len(labels))]
		self.toUpdate = []

	def assertOrder(self, x, y):
		if x == y:
			raise Exception("Trying to order the same element " + x)
		self._assertOrder(self.index[x], self.index[y])

	def _assertOrder(self,ix,iy):
		if self.lookup[ix][iy] or self.lookup[ix][iy]:
			raise Exception("Ordering already instantiated")

		self.lookup[ix][iy] = -1
		self.lookup[iy][ix] = 1
		self.toUpdate.append((ix,iy))

	def getOrder(self,x,y):
		ix = self.index[x]
		iy = self.index[y]
		return self.lookup[ix][iy]

	def propagate(self):
		print("Propagating")
		while self.toUpdate:
			ix, iy = self.toUpdate.pop()

			for i in range(len(self.labels)):
				if i != ix and i != iy:
					if self.lookup[i][ix] < 0 and not self.lookup[i][iy]:
						self._assertOrder(i,iy)
						self._printTransitivity(i,ix,iy)
					if self.lookup[iy][i] > 0 and not self.lookup[ix][i]:
						self._assertOrder(ix,i)
						self._printTransitivity(ix,iy,i)

	def _printTransitivity(self,i,j,k):
		print("{} < {} and {} < {} so by transitivity {} < {}".format(
			self.labels[i], self.labels[j],
			self.labels[j], self.labels[k],
			self.labels[i], self.labels[k]
		))

	def print(self):
		print("")
		strLabels = [str(l) for l in self.labels]
		s = [[""] + strLabels] +[[label] + [str(e) for e in row] for row, label in zip(self.lookup, strLabels)]
		lens = [max(map(len, col)) for col in zip(*s)]
		fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
		table = [fmt.format(*row) for row in s]
		print('\n'.join(table))
		print("")

n = 2

paths = []
for l in range(n+1):
	paths.extend(permutations(range(1,n+1),l))

order = Order(paths)
order.propagate()
order.print()

for p in paths:
	for l in range(len(p)):
		order.assertOrder(p[:l],p)
order.print()

order.assertOrder((2,),(1,))
order.propagate()
order.print()