import tkinter
import copy
import progressbar
from collections import defaultdict

import settings
from theory.orders import PathPartialOrder, Related
from theory.algebra import DisplayAlgebra
import theory.bellmanFord as bellmanFord

################
## Controller ##
################

class OrderSearchController():

	###########
	## Setup
		
	def __init__(self, mode, parent):
		self._mode = mode
		self._view = OrderSearchView(self, parent)


	def searchAllAlgebras(self):
		graph 			= self._mode.choiceController.getGraph()
		paths 		 	= self._mode.pathDisplayController.getPaths()

		self.eliminateSymmetries(graph, paths)


	def orderToPathAlgebra(self, order, name):
		invalidRoute  = None
		identityRoute = ()
		invalidEdge   = None

		def plus(x,y):
			if x == invalidRoute:
				return y
			if y == invalidRoute:
				return x
			elif order.getRelation(x,y) == Related.LESS_THAN:
				return x
			else:
				return y

		def times(e, v, i, j):
			if e == invalidEdge or v == invalidRoute or i in v:
				return invalidRoute

			if v == ():
				return (i,j)
			else:
				return (i,) + v

		return DisplayAlgebra(
			name				= name,
			plus 				= plus,
			times 				= times,
			invalidRoute        = invalidRoute,
			identityRoute       = identityRoute,
			invalidEdge         = invalidEdge,
			defaultEdge			= 1,
			randomEdge			= lambda:defaultEdge,
			validateEdgeString	= lambda x : x == "1",
			parseEdgeString		= int,
			componentAlgebras	= []
		)



	"""
	def generateTotalOrders(self, partialOrder):

		def generate():
			nextUnknown = partialOrder.getNextUnknown()
			if nextUnknown:
				p, q = nextUnknown
				partialOrder.assertOrder(p,q)
				for totalOrder in generate():
					yield totalOrder
				partialOrder.undoLastAssertion()

				partialOrder.assertOrder(q,p)
				for totalOrder in generate():
					yield totalOrder
				partialOrder.undoLastAssertion()
			else:
				yield partialOrder
		return generate()
	"""

	def _switchElements(self, path, x, y):
		result = []
		for i in path:
			if i == x:
				result.append(y)
			elif i == y:
				result.append(x)
			else:
				result.append(i)
		return tuple(result)

	"""
		symmetryGroup -- list of n integers
		availablePaths -- list of n lists of paths
	"""
	def _calculateSymmetryBreak(self, symmetryGroup, availablePaths):
		pathChoices = list(combinations(availablePaths[0], 2))
		pathScores  = [len((set(p[1:]) | set(q[1:])) & set(symmetryGroup)) for p,q in pathChoices]
		score, (p, q) = min(zip(pathScores, pathChoices))

		remaining = list((set(p[1:]) | set(q[1:])) & set(symmetryGroup))
		n = len(remaining)

		results = []
		ps = [self._switchElements(p, p[0], remaining[j]) for j in range(n)]
		qs = [self._switchElements(q, q[0], remaining[j]) for j in range(n)]

		newAvailablePaths = [[p for p in availablePaths[i] if p != ps[i]] for i in range(len(symmetryGroup))]

		for i in range(n+1):
			# Calculate the assertions
			assertions = []
			for j in range(n):
				assertions.append((ps[j],qs[j]) if j < i else (qs[j],ps[j]))

			# Calculate the symmetries
			newSymmetries = []
			if i >= 2:
				newSymmetryGroup = remaining[:i]
				newAvailablePaths = [newAvailablePaths[k][::] for k in newSymmetryGroup]
				newSymmetries.append((newSymmetryGroup, newAvailablePaths))
			elif i <= n - 2:
				newSymmetryGroup = set(remaining[i:])
				newAvailablePaths = [newAvailablePaths[k][::] for k in newSymmetryGroup]
				newSymmetries.append((newSymmetryGroup, newAvailablePaths))

			results.append((assertions, newSymmetries))

		"""
		for r in results:
			print(r)
		"""

		return results

	def eliminateSymmetries(self, graph, paths):
		n 				= len(graph.nodes())
		idRow 			= [(0,) if i == 0 else None for i in range(n)]

		groupedPaths = defaultdict(list)
		for p in paths:
			if len(p) > 1:
				groupedPaths[p[0]].append(p)

		print("Grouped")
		pathsBySource = {s:g for s,g in groupedPaths.items()}
		for g in pathsBySource.values():
			g.sort(key=lambda p: p[::-1])
			g.sort(key=len)
			print(g)
		print("")

		partialOrders = []
		toSearch = [(PathPartialOrder(paths), [set(range(1,n))], 0, 1, 0)]
		for _ in range(1):
			partialOrder, symmetries, k, l, depth = toSearch.pop()

			if not symmetries:
				partialOrders.append(partialOrder)
			else:
				group = symmetries.pop()
				e = next(iter(group))
				p = pathsBySource[e][k]
				q = pathsBySource[e][l]

				results = self._calculateSymmetryBreak(group, p, q)
				for assertions, newGroups in results:
					newPartialOrder = partialOrder.clone()
					for p, q in assertions:
						newPartialOrder.assertOrder(p,q)

					newSymmetries = copy.deepcopy(symmetries)
					newSymmetries.extend(newGroups)

					toSearch.append((newPartialOrder, newSymmetries))

		return [PathPartialOrder(paths)]



	def score(self, graph, paths):
		partialOrders   = self.eliminateSymmetries(graph, paths)

		n 				= len(graph.nodes()) 
		idRow 			= [(0,) if i == 0 else None for i in range(n)]
		partialOrder 	= None
		maxTime        	= 0
		maxDepth        = 0
		maxAssertions   = []
		count           = 0
		progressDiv 	= 1.0/len(partialOrders)

		progressBar = progressbar.ProgressBar(
			redirect_stdout=True, 
			widgets = [
				progressbar.DynamicMessage('Score'),
				" | ",
				progressbar.DynamicMessage('SearchDepth'),
				" | ",
				progressbar.DynamicMessage('Explored'),
				" | ",
				progressbar.Percentage(),
				" | ",
				progressbar.Timer()
			]
		)

		def log(progressPercentage):
			nonlocal count, maxTime, maxDepth
			count += 1
			if count % 100 == 0:
				progressBar.update(progressPercentage, Score=maxTime, SearchDepth=maxDepth, Explored=count)

		def times(i,k,path):
			if (k not in graph[i]) or (path is None) or (i in path):
				return None
			else:
				return (i,) + path

		def iterate(previousState, currentState, time, depth, progress):
			for i in range(len(currentState), n):
				candidateRoutes = [times(i,k,previousState[k]) for k in range(n)] + [idRow[i]]

				bestRoute = None
				for route in candidateRoutes:
					if bestRoute is None:
						bestRoute = route
					elif route is not None:
						relation = partialOrder.getRelation(bestRoute, route)
						if relation == Related.GREATER_THAN:
							bestRoute = route
						elif relation == Related.UNKNOWN:
							partialOrder.assertOrder(bestRoute, route)
							iterate(previousState, copy.deepcopy(currentState), time, depth+1, progress)
							partialOrder.undoLastAssertion()

							partialOrder.assertOrder(route, bestRoute)
							iterate(previousState, copy.deepcopy(currentState), time, depth+1, progress + progressDiv*(0.5**(depth+1)))
							partialOrder.undoLastAssertion()
							return

				currentState.append(bestRoute)

			if currentState == previousState:
				nonlocal maxTime, maxDepth
				if time > maxTime:
					maxTime = time
					maxAssertions = partialOrder.getAssertions()
					print("New best", maxAssertions)
				if depth > maxDepth:
					maxDepth = depth
				log(progress*100)
			else:
				iterate(currentState, [], time+1, depth, progress)

		for i, partialOrder in enumerate(partialOrders):
			iterate(idRow, [], 0, 0, i*progressDiv)

		print(maxTime, maxAssertions)




##########
## View ##
##########

class OrderSearchView(tkinter.Frame):
	
	def __init__(self, controller, parent, *args, **kwargs):
		tkinter.Frame.__init__(self, parent, *args, **kwargs, borderwidth=settings.BORDER_WIDTH, relief=tkinter.GROOVE)
		self.controller = controller

		self.headerL = tkinter.Label(self, text="Search", font="TkHeadingFont")
		self.searchB = tkinter.Button(self, compound=tkinter.LEFT, text="Search for best ordering", command=controller.searchAllAlgebras)
		
		self.headerL.grid(row=0,column=0,sticky="W")
		self.searchB.grid(row=1,column=0,sticky="",padx=5,pady=5)
		self.grid_columnconfigure(0, weight=1)