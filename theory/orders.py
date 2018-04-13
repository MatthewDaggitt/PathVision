from collections import defaultdict
from enum import Enum
from itertools import combinations
import copy

class Related(Enum):
	LESS_THAN		= -1,
	EQUAL_TO 		= 0,
	GREATER_THAN	= 1,
	UNKNOWN			= 2

class PathPartialOrder():
	def __init__(self, paths):
		pathsBySource = defaultdict(list)
		for p in paths:
			pathsBySource[p[0]].append(p)

		n = len(paths)
		indices = {p:i for i,p in enumerate(paths)}
		ordering = [[Related.EQUAL_TO if x == y else Related.UNKNOWN for x in range(n)] for y in range(n)]

		for pIndex, p in enumerate(paths):
			for i in range(1,len(p)-1):
				pm = p[i:]
				pmIndex = indices[pm]
				ordering[pmIndex][pIndex] = Related.LESS_THAN
				ordering[pIndex][pmIndex] = Related.GREATER_THAN
				

		self.paths 	  		= list(paths)
		self.pathsBySource 	= pathsBySource
		self.indices  		= indices
		self.ordering 		= ordering
		self.toUpdate 		= []
		self.assertions 	= []


	#############
	## Actions ##
	#############

	def assertOrder(self,p,q):
		if p == q:
			raise Exception("Trying to order the same path " + p)

		self._currentAssertions = []
		self._assertOrder(self.indices[p], self.indices[q])
		self._propagate()

	def _assertOrder(self, pIndex, qIndex):
		if self.ordering[pIndex][qIndex] != Related.UNKNOWN or self.ordering[qIndex][pIndex] != Related.UNKNOWN:
			raise Exception("Ordering already instantiated")

		self.ordering[pIndex][qIndex] = Related.LESS_THAN
		self.ordering[qIndex][pIndex] = Related.GREATER_THAN

		delta = (pIndex, qIndex)
		self.toUpdate.append(delta)
		self._currentAssertions.append(delta)

	def _propagate(self):
		while self.toUpdate:
			pIndex, qIndex = self.toUpdate.pop()

			# Propagate within groups of the same length
			for i in range(len(self.ordering)):
				if i != pIndex and i != qIndex:
					if self.ordering[i][pIndex] == Related.LESS_THAN and self.ordering[i][qIndex] == Related.UNKNOWN:
						self._assertOrder(i,qIndex)
					if self.ordering[qIndex][i] == Related.LESS_THAN and self.ordering[pIndex][i] == Related.UNKNOWN:
						self._assertOrder(pIndex,i)

		self.assertions.append(self._currentAssertions)

	def undoLastAssertion(self):
		deltas = self.assertions.pop()
		for pIndex, qIndex in deltas:
			self.ordering[pIndex][qIndex] = Related.UNKNOWN
			self.ordering[qIndex][pIndex] = Related.UNKNOWN

	def isTotal(self):
		return not any([Related.UNKNOWN in row for row in self.ordering])

	#############
	## Getters ##
	#############

	def getRelation(self,p,q):
		return self.ordering[self.indices[p]][self.indices[q]]

	def getSourceOrdering(self, source):
		paths = self.pathsBySource[source]

		heights = []
		for p in paths:
			height = 0
			for q in paths:
				pIndex = self.indices[p]
				qIndex = self.indices[q]
				if self.ordering[pIndex][qIndex] == Related.GREATER_THAN:
					height += 1
			heights.append(height)
		sortedPaths = [p for _,p in sorted(zip(heights,paths))]
		return sortedPaths

	def getNextUnknown(self):
		for source, pathsBySource in self.pathsBySource.items():
			n = len(pathsBySource)
			for p, q in combinations(pathsBySource,2):
				pIndex = self.indices[p]
				qIndex = self.indices[q]
				if self.ordering[pIndex][qIndex] == Related.UNKNOWN:
					return (p, q)
		return None

	def getAssertions(self):
		return [(self.paths[l[0][0]], self.paths[l[0][1]]) for l in self.assertions]

	def clone(self):
		return copy.deepcopy(self)

	"""
	def _printTransitivity(self,i,j,k):
		print("{} < {} and {} < {} so by transitivity {} < {}".format(
			self.paths[i], self.paths[j],
			self.paths[j], self.paths[k],
			self.paths[i], self.paths[k]
		))
	"""

	def _printUnknowns(self):
		print("")
		print("Unknowns")
		print("========")
		for p, q in combinations(paths,2):
			if self.ordering[self.index[p]][self.index[q]] == Related.UNKNOWN:
				print(p,q)

	def _printRelations(self):
		print("")
		print("All")
		print("========")
		strLabels = [str(p) for p in self.paths]
		s = [[""] + strLabels] +[[label] + [str(e) for e in row] for row, label in zip(self.ordering, strLabels)]
		lens = [max(map(len, col)) for col in zip(*s)]
		fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
		table = [fmt.format(*row) for row in s]
		print('\n'.join(table))








class PathPartialOrder2():
	def __init__(self, paths):
		pathsBySource = defaultdict(list)
		for p in paths:
			pathsBySource[p[0]].append(p)

		indicesBySource = {}
		for source, sourcePaths in pathsBySource.items():
			indicesBySource[source] = {p:i for i,p in enumerate(sourcePaths)}

		orderingsBySource = {}
		for source in pathsBySource:
			n = len(pathsBySource[source])
			orderingsBySource[source] = [[Related.EQUAL_TO if x == y else Related.UNKNOWN for x in range(n)] for y in range(n)]

		self.paths = paths
		self.pathsBySource 		= pathsBySource
		self.indicesBySource 	= indicesBySource
		self.orderingsBySource 	= orderingsBySource
		self.toUpdate = []
		self.assertions = []


	#############
	## Actions ##
	#############

	def assertOrder(self,p,q):
		if p == q:
			raise Exception("Trying to order the same path " + p)
		if p[0] != q[0]:
			raise Exception("Paths {} and {} do not have the same source and destination".format(p,q))

		self._currentAssertions = []
		self._assertOrder(p[0], self.indicesBySource[p[0]][p], self.indicesBySource[q[0]][q])
		self._propagate()

	def _assertOrder(self, source, pIndex, qIndex):
		ordering = self.orderingsBySource[source]
		if ordering[pIndex][qIndex] != Related.UNKNOWN or ordering[qIndex][pIndex] != Related.UNKNOWN:
			raise Exception("Ordering already instantiated")

		ordering[pIndex][qIndex] = Related.LESS_THAN
		ordering[qIndex][pIndex] = Related.GREATER_THAN

		delta = (source, pIndex, qIndex)
		self.toUpdate.append(delta)
		self._currentAssertions.append(delta)

	def _propagate(self):
		while self.toUpdate:
			source, pIndex, qIndex = self.toUpdate.pop()

			# Propagate within groups of the same length
			ordering = self.orderingsBySource[source]
			for i in range(len(ordering)):
				if i != pIndex and i != qIndex:
					if ordering[i][pIndex] == Related.LESS_THAN and ordering[i][qIndex] == Related.UNKNOWN:
						self._assertOrder(source,i,qIndex)
					if ordering[qIndex][i] == Related.LESS_THAN and ordering[pIndex][i] == Related.UNKNOWN:
						self._assertOrder(source,pIndex,i)

			# Propagate over strictly increasing relationships
			p = self.pathsBySource[source][pIndex]
			q = self.pathsBySource[source][qIndex]
			for i in range(1,len(p)-1):
				r = p[i:]
				rSource = r[0]
				rSourceIndices = self.indicesBySource[rSource]
				rSourceOrdering = self.orderingsBySource[rSource]
				rIndex = rSourceIndices[r]

				# Can optimise this loop by finding parents
				for s in self.pathsBySource[rSource]:
					if self._isSubpathOf(q,s):
						sIndex = rSourceIndices[s]
						if rSourceOrdering[rIndex][sIndex] == Related.UNKNOWN:
							self._assertOrder(rSource, rIndex, sIndex)

		self.assertions.append(self._currentAssertions)

	def _isSubpathOf(self,p,q):
		if len(p) > len(q):
			return False

		for i in range(1,len(p)+1):
			if p[-i] != q[-i]:
				return False
		return True

	def undoLastAssertion(self):
		deltas = self.assertions.pop()
		for (source, pIndex, qIndex) in deltas:
			ordering = self.orderingsBySource[source]
			ordering[pIndex][qIndex] = Related.UNKNOWN
			ordering[qIndex][pIndex] = Related.UNKNOWN

	#############
	## Getters ##
	#############

	def getRelation(self,p,q):
		if p[0] != q[0]:
			raise Exception("Paths {} and {} do not have the same source and destination".format(p,q))
		pIndex = self.indicesBySource[p[0]][p]
		qIndex = self.indicesBySource[q[0]][q]
		return self.orderingsBySource[p[0]][pIndex][qIndex]

	def getSourceOrdering(self, source):
		ordering = self.orderingsBySource[source]
		paths    = self.pathsBySource[source]
		n = len(ordering)

		heights = [sum(1 for j in range(n) if ordering[i][j] == Related.GREATER_THAN) for i in range(n)]
		sortedPaths = [p for _,p in sorted(zip(heights,paths))]
		return sortedPaths

	def getNextUnknown(self):
		for source, ordering in self.orderingsBySource.items():
			n = len(ordering)
			for i in range(n):
				for j in range(n):
					if ordering[i][j] == Related.UNKNOWN:
						paths = self.pathsBySource[source]
						return (paths[i], paths[j])
		return None

	def clone(self):
		return copy.deepcopy(self)

	"""
	def _printTransitivity(self,i,j,k):
		print("{} < {} and {} < {} so by transitivity {} < {}".format(
			self.paths[i], self.paths[j],
			self.paths[j], self.paths[k],
			self.paths[i], self.paths[k]
		))
	"""

	def _printUnknowns(self):
		print("")
		print("Unknowns")
		print("========")
		for source, sourcePaths in self.pathsBySource.items():
			print("---{}---".format(source))
			ordering = self.orderingsBySource[source]
			index = self.indicesBySource[source]
			for p, q in combinations(sourcePaths,2):
				if ordering[index[p]][index[q]] == Related.UNKNOWN:
					print(p,q)

	def _printRelations(self):
		print("")
		print("All")
		print("========")
		for source, sourcePaths in self.pathsBySource.items():
			print("---{}---".format(source))
			strLabels = [str(p) for p in sourcePaths]
			s = [[""] + strLabels] +[[label] + [str(e) for e in row] for row, label in zip(self.orderingsBySource[source], strLabels)]
			lens = [max(map(len, col)) for col in zip(*s)]
			fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
			table = [fmt.format(*row) for row in s]
			print('\n'.join(table))