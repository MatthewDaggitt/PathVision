import math
import random
import pickle
import threading
import tkinter

import networkx as nx


from settings import *

import theory.algebra as algebra
import theory.bellmanFord as bellmanFord
import theory.displayAlgebra as displayAlgebra
import theory.graph as graph

from frames.display import Display
from frames.generalControls import GeneralControls
from frames.navigationControls import NavigationControls


class App(tkinter.Frame):

	def __init__(self):
		tkinter.Frame.__init__(self)

		# Choose ttk themes
		for theme in ["aqua","vista","xpnative","clam"]:
			if theme in tkinter.ttk.Style().theme_names():
				tkinter.ttk.Style().theme_use(theme)
				break

		# Setup user interface
		self.master.title("PathVision")
		self.pack(fill=tkinter.BOTH, expand=True)

		self._display = Display(self, self)
		self._navigationControls = NavigationControls(self, self)
		self._generalControls = GeneralControls(self, self)

		self._display.grid(row=0, column=0, sticky="NESW", padx=(15,5), pady=(15,5))
		self._navigationControls.grid(row=1, column=0, sticky="EW", padx=(15,5), pady=5)
		self._generalControls.grid(row=0, column=1, rowspan=2, sticky="NS", padx=(5,15), pady=5)
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)


		# Setup app data
		self.AG = graph.AugmentedGraph()
		self.A = None
		self.CA = None
		self.states = None
		self.time = None


		# Load default example and run
		self._load("examples/non_linear_counterexample.pv")

		self.master.protocol("WM_DELETE_WINDOW", self.on_close)
		tkinter.mainloop()




	###########
	## Nodes ##
	###########

	def addNode(self, x, y):
		self.AG.addNode(x, y)
		if self.states:
			self.stopCalculating()
		self.draw()

	def deleteNode(self, n):
		self.AG.deleteNode(n)
		if self.states:
			self.stopCalculating()
		self.draw()

	def selectNode(self, n):
		self.AG.selectNode(n)
		self.draw()

	def deselectNode(self):
		self.AG.deselectNode()
		self.draw()

	def moveNode(self, n, x, y):
		self.AG.moveNode(n, x, y)
		self.draw()

	def toggleNodeLabel(self, n):
		self.AG.toggleLabel(n)
		self.draw()

	def setSourceNode(self, n):
		self.AG.setSource(n)
		if self.time:
			self.time = 0
			self.timeChanged()
		self.draw()


	
	######################
	## Edge alterations ##
	######################

	def addEdge(self, e):
		self.AG.addEdge(e, self.A.defaultEdge)
		if self.states:
			self.stopCalculating()
		self.draw()

	def deleteEdge(self, e):
		if e == self.AG.selectedEdge:
			self.deselectEdge()
		self.AG.deleteEdge(e)

		if self.states:
			self.stopCalculating()
		self.draw()

	def selectEdge(self, e):
		a, b = e
		self.AG.selectEdge(e)
		self._generalControls.edgeSelected(self.AG.G[a][b]['weight'])
		self.draw()

	def deselectEdge(self):
		self.AG.deselectEdge()
		self._generalControls.edgeDeselected()
		self.draw()

	def setSelectedEdgeValue(self, value):
		self.AG.setSelectedEdgeValue(value)
		if self.states:
			self.stopCalculating()
		self.draw()

	

	#########################
	## Algebra alterations ##
	#########################

	def setAlgebra(self, A, reset):
		if self.A == A:
			return

		self.A = A
		self.CA = displayAlgebra.DisplayAlgebra.trackPaths(A) if self.withPaths else A

		self._generalControls.algebraChanged(A)
		if self.AG.selectedNode:
			self.deselectNode()
		if self.AG.selectedEdge:
			self.deselectEdge()

		if reset:
			self.AG.resetEdgeValues(A.defaultEdge)

		self.stopCalculating()
		self.draw()


	def setWithPaths(self, v):
		self.withPaths = v
		self._generalControls.withPathsChanged(v)

		if self.A:
			self.CA = displayAlgebra.DisplayAlgebra.trackPaths(self.A) if self.withPaths else self.A



	############################
	## Minimal example search ##
	############################

	def startSearch(self, iterations, n):
		self.searching = True

		idM = self._createIdentityMatrix(n)

		updateFrequency = int(iterations/100)

		def worker():
			i = 0
			itMax = 0
			adMax = None

			while self.searching and i < iterations:
				adM = [[self.CA.randomEdge() if i != j else None for i in range(n)] for j in range(n)]
				it = len(bellmanFord.solve(self.CA.A, idM, idM, adM)) - 2
				
				if it > itMax:
					self._optimiseSearchResult(idM, adM, it)
					self._loadSearchResult(adM)

					itMax = it
					adMax = adM

				i += 1
				if i % updateFrequency == 0:
					self._generalControls.searchUpdate(i, itMax)

			if self.searching:
				self.endSearch()

		t = threading.Thread(target=worker)
		t.start()

	def endSearch(self):
		self.searching = False
		self._generalControls.searchEnded()

	def _optimiseSearchResult(self, idM, adM, iterations):
		for i in range(len(adM)):
			for j in range(len(adM)):
				oldValue = adM[i][j]
				adM[i][j] = None

				newIterations = len(bellmanFord.solve(self.CA.A, idM, idM, adM)) - 2
				if newIterations < iterations:
					if self.A == displayAlgebra.fRing and adM[i][j] != "c":
						adM[i][j] = "c"
						newIterations = len(bellmanFord.solve(self.CA.A, idM, idM, adM)) - 2
						if newIterations < iterations:
							adM[i][j] = oldValue
					else:
						adM[i][j] = oldValue

	def _loadSearchResult(self, adM):
		self.AG.loadFromAdjacencyMatrix(adM)

		# Find source node
		idM = self._createIdentityMatrix(len(adM))

		states = bellmanFord.solve(self.CA.A, idM, idM, adM)

		sourceNode = -1
		for i in range(len(adM)):
			if [row[i] for row in states[-2]] != [row[i] for row in states[-3]]:
				sourceNode = i
				break

		self.setSourceNode(sourceNode)

	

	###########################
	## Calculating solutions ##
	###########################
	
	def startCalculating(self):
		n = len(self.AG.G)

		self.idM = self._createIdentityMatrix(n)
		self.adM = self._createAdjacencyMatrix()

		i = 2
		self.states = [self.idM, bellmanFord.iterate(self.CA.A, self.idM, self.idM, self.adM)]
		while i <= n*n and self.states[-1] != self.states[-2]:
			newState = bellmanFord.iterate(self.CA.A, self.states[-1], self.idM, self.adM)
			self.states.append(newState)
			i += 1

		self.time = 0
		self.timeChanged()

		self._navigationControls.startedCalculating()
		self._display.startedCalculating()
		self.draw()

	def stopCalculating(self):
		self.states = None
		self.time = None

		self._navigationControls.stoppedCalculating()
		self._display.stoppedCalculating()
		self.draw()

	def _stateAt(self, time):
		return [row[self.AG.sourceNode] for row in self.states[time]]

	def _createIdentityMatrix(self, n):
		if self.withPaths:
			return [[(self.A.A.one, [i]) if i == j else None for j in range(n)] for i in range(n)]
		else:
			return [[self.A.A.one if i == j else self.A.A.zero for j in range(n)] for i in range(n)]

	def _createAdjacencyMatrix(self):
		n = len(self.AG.G)
		if self.withPaths:
			return [[self.AG.G[i][j]['weight'] if j in self.AG.G[i] else None for j in range(n)] for i in range(n)]
		else:
			return [[self.AG.G[i][j]['weight'] if j in self.AG.G[i] else self.A.A.zero for j in range(n)] for i in range(n)]



	#####################
	## Time navigation ##
	#####################

	def moveToStart(self):
		self.time = 0
		self.timeChanged()

	def moveBack(self):
		self.time -= 1
		self.timeChanged()

	def moveForwards(self):
		self.time += 1
		if self.time == len(self.states) - 1:
			self.states.append(bellmanFord.iterate(self.CA.A, self.states[-1], self.idM, self.adM))
		self.timeChanged()

	def moveToEnd(self):
		i = 0
		while i + 1 < len(self.states):
			if self._stateAt(i) == self._stateAt(i+1):
				self.time = i
				break
			i += 1

		self.timeChanged()

	def timeChanged(self):

		convergedNow = self._stateAt(self.time) == self._stateAt(self.time+1)
		convergedThen = self._stateAt(-2) == self._stateAt(-1)

		canProceed = not convergedNow
		canProceedToEnd = canProceed and convergedThen

		self._navigationControls.timeChanged(self.time, canProceed, canProceedToEnd)
		self._display.timeChanged(self.time, canProceed)

		self.draw()


	#############
	## Drawing ##
	#############

	def _createNodeLabel(self, n):
		if not self.AG.labelled[n]:
			return ""

		v = self.states[self.time][n][self.AG.sourceNode]
		if not v or not self.withPaths:
			return v

		x, p = v

		if len(p) <= 3:
			return v

		return "(" + str(x) + ", [" + str(p[0]) + "," + str(p[1]) + ",...," + str(p[-1]) + "])"


	def draw(self):

		nodeLabels = {n : self._createNodeLabel(n) if self.states else "" for n in self.AG.G.nodes()}
		nodePositions = self.AG.pos
		nodeColours = [SOURCE_NODE_COLOUR if n == self.AG.sourceNode else NODE_COLOUR for n in self.AG.G.nodes()]
		nodeOutlinesWidths = [3.0 if n == self.AG.selectedNode else 1.0 for n in self.AG.G.nodes()]
		edgeWidths = [2.0 if e == self.AG.selectedEdge else 1.0 for e in self.AG.G.edges()]


		self._display.draw(self.AG.G, nodeLabels, nodePositions, nodeColours, nodeOutlinesWidths, edgeWidths)


	####################
	## Storing graphs ##
	####################

	def save(self):
		filename = tkinter.filedialog.asksaveasfilename()
		if filename:
			self._save(filename)
			

	def _save(self, filename):
		file = open(filename, 'wb')

		pickle.dump({
			"edgeList" : list(nx.generate_edgelist(self.AG.G)),
			"pos" : self.AG.pos,
			"source" : self.AG.sourceNode,
			"algebra" : self.A.name,
			"withPaths" : self.withPaths
		}, file)


	def load(self):
		filename = tkinter.filedialog.askopenfilename()
		if filename:
			self._load(filename)

	def _load(self, filename):
		data = pickle.load(open(filename, 'rb'))

		self.AG.G = nx.parse_edgelist(data['edgeList'], nodetype=int, create_using=nx.DiGraph())
		self.AG.sourceNode = data['source']
		self.AG.pos = data['pos']
		self.AG.labelled = {n:True for n in self.AG.G}
		self.setWithPaths(data['withPaths'])

		for A in displayAlgebra.examples:
			if A.name == data['algebra']:
				self.setAlgebra(A, False)

		self.draw()



	###################
	## Window events ##
	###################

	def on_close(self):
		self.searching = False
		self.destroy()
		quit()


if __name__ == '__main__':
	App()
	sys.exit()