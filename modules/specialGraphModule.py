import threading
import tkinter

import settings
import theory.bellmanFord as bellmanFord
import theory.algebraExamples as algebraExamples
from theory.pathalogicalAlgebra import *
from modules.shared.dialogs.size import SizeDialog

################
## Controller ##
################

class SpecialGraphController():

	def __init__(self, mode, parent):
		#self._model = SpecialGraphModel(self)
		self._view  = SpecialGraphView(self, parent)
		self._mode  = mode

	def generatePathalogicalGraph(self, n):
		adM = generatePathalogicalAdjacencyMatrix(n)

		self._mode.graphController.loadGraphFromAdjacencyMatrix(adM)
		self._mode.problemTopologyChanged()

	"""
	def startSearch(self):
		runs, size = self._view.getSearchParameters()
		algebra = self._mode.algebraController.getComputationAlgebra()

		self._view.enterSearchState()
		self._model.startSearch(algebra, runs, size)

	def endSearch(self):
		self._model.endSearch()
		self._view.enterStandbyState()

	def updateProgress(self, progress, currentScore):
		self._view.updateProgress(progress, currentScore)

	def updateResult(self, adjacencyMatrix, sourceNode):
		self._mode.graphController.loadGraphFromAdjacencyMatrix(adjacencyMatrix)
		self._mode.graphController.setSourceNode(sourceNode)
		self._mode.problemTopologyChanged()
	"""

"""
###########
## Model ##
###########

class SpecialGraphModel():
	def __init__(self, controller):
		self.controller = controller

	############
	## Interface

	def startSearch(self, algebra, totalRuns, graphSize):
		# Core search parameters
		self.totalRuns		= totalRuns
		self.graphSize 		= graphSize
		self.algebra 		= algebra

		# Derived search parameters
		self.idM 		= bellmanFord.createIdentityMatrix(algebra, graphSize)
		
		# Start the search
		threading.Thread(target=self._runSearch).start()
		self.searching = True

	def endSearch(self):
		self.searching = False

	#####################
	## Internal functions

	def _createRandomAdjacencyMatrix(self, size):
		return [[self.algebra.randomEdge() if i != j else self.algebra.invalidEdge 
					for i in range(size)] 
						for j in range(size)]
		
	def _runSearch(self):
		
		updateFrequency = int(self.totalRuns/100)

		bestScore 		= 0
		bestInstance 	= None

		for i in range(self.totalRuns):
			adM = self._createRandomAdjacencyMatrix(self.graphSize)
			score = self._calculateScore(adM)
			
			if score > bestScore:
				bestScore    = score
				bestInstance = adM
				self._newBestFound(adM)

			if i % updateFrequency == 0:
				self.controller.updateProgress(i/self.totalRuns, bestScore)

			if not self.searching:
				break
		
		self.controller.updateProgress(1.0, bestScore)
		self.controller.endSearch()

	# Calculates how long a given adjacency matrix adM takes to converge
	def _calculateScore(self, adM):
		routingComputation = bellmanFord.solve(self.algebra, self.idM, self.idM, adM)
		return len(routingComputation) - 2

	# Simplifies the search result by testing if we can remove each edge one by one
	def _optimiseSearchResult(self, adM):
		score = self._calculateScore(adM)

		for i in range(len(adM)):
			for j in range(len(adM)):
				entry = adM[i][j]
				adM[i][j] = self.algebra.invalidEdge

				newScore = self._calculateScore(adM)
				if newScore < score:
					if self.algebra == algebraExamples.fRing and adM[i][j] != "c":
						adM[i][j] = "c"
						newScore = self._calculateScore(adM)
						if newScore < score:
							adM[i][j] = entry
					else:
						adM[i][j] = entry

	# Replaces all invalid edges with no edges at all
	def _cleanSearchResult(self, adM):
		for i in range(len(adM)):
			for j in range(len(adM)):
				if adM[i][j] == self.algebra.invalidEdge:
					adM[i][j] = None

	# Calculates the source node for which the computation takes the longest to converge
	def _calculateBestSourceNode(self,adM):
		states = bellmanFord.solve(self.algebra, self.idM, self.idM, adM)

		sourceNode = -1
		for i in range(len(adM)):
			if [row[i] for row in states[-2]] != [row[i] for row in states[-3]]:
				sourceNode = i
				break
		return sourceNode
	
	def _newBestFound(self, adM):
		self._optimiseSearchResult(adM)
		sourceNode = self._calculateBestSourceNode(adM)
		self._cleanSearchResult(adM)

		self.controller.updateResult(adM, sourceNode)
"""


##########
## View ##
##########

class SpecialGraphView(tkinter.Frame):

	def __init__(self, controller, parent):
		tkinter.Frame.__init__(self, parent, borderwidth=settings.BORDER_WIDTH, relief=tkinter.GROOVE)
		self.controller = controller

		self.headerL = tkinter.Label(self, text="Special graphs", font="TkHeadingFont")

		"""
		self.iterationsL = tkinter.Label(self, text="Iterations:", anchor="e")
		self.iterationsE = tkinter.Entry(self, width=10)
		self.iterationsE.insert(0, 1000)

		self.sizeL = tkinter.Label(self, text="Nodes:")
		self.sizeE = tkinter.Entry(self, width=10)
		self.sizeE.insert(0, 5)

		self.progressL = tkinter.Label(self, text="Results:")
		self.progressDL = tkinter.Label(self, justify=tkinter.LEFT)

		self.searchB = tkinter.Button(self, width=15)
		"""
		self.generatePathB = tkinter.Button(self, width=22, text="Generate pathalogical example", command=self.generatePathalogical)
		self.headerL.grid(		row=0,column=0,sticky="W",columnspan=2)
		"""
		self.iterationsL.grid(	row=1,column=0,sticky="W",pady=(5,2.5))
		self.iterationsE.grid(	row=1,column=1,sticky="W",pady=(5,2.5),  padx=(10,0))
		self.sizeL.grid(		row=2,column=0,sticky="W",pady=(2.5,2.5))
		self.sizeE.grid(		row=2,column=1,sticky="W",pady=(2.5,2.5),padx=(10,0))
		self.progressL.grid(	row=3,column=0,sticky="W",pady=(2.5,2.5))
		self.progressDL.grid(	row=3,column=1,sticky="W",pady=(2.5,2.5),padx=(10,0))
		self.searchB.grid(		row=4,column=0,sticky="", pady=(2.5,5),columnspan=2)
		"""
		self.generatePathB.grid(row=1,column=0,sticky="", pady=(2.5,5),columnspan=2)
		self.columnconfigure(1,weight=1)
		"""

		#self.enterStandbyState()

	############
	## Getters

	def getSearchParameters(self):
		runs = int(self.iterationsE.get())
		size = int(self.sizeE.get())
		return runs, size

	############
	## Actions

	def enterStandbyState(self):
		self.iterationsE.configure(state=tkinter.NORMAL)
		self.sizeE.configure(state=tkinter.NORMAL)
		self.searchB.configure(text="Start searching", command=self.controller.startSearch)

	def enterSearchState(self):
		self.iterationsE.configure(state=tkinter.DISABLED)
		self.sizeE.configure(state=tkinter.DISABLED)
		self.searchB.configure(text="Stop searching", command=self.controller.endSearch)

	def updateProgress(self, progress, bestScore):
		text = "{} rounds ({}%)".format(bestScore, int(100*progress))
		self.progressDL.configure(text=text)
		"""

	def generatePathalogical(self):
		root = self.controller._mode.app
		dialog = SizeDialog(root)
		size = dialog.result

		if size is not None:
			self.controller.generatePathalogicalGraph(size)