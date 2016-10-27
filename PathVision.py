import math
import random
import pickle

import tkinter
from tkinter import ttk

import networkx as nx

import theory.algebra as algebra
import theory.bellmanFord as bellmanFord
import theory.displayAlgebra as displayAlgebra
import theory.graph as graph
from frames.display import Display
from frames.controls import Controls



######### Themes ###########

desiredOrder = ["aqua","vista","xpnative","clam"]

for theme in desiredOrder:
	if theme in tkinter.ttk.Style().theme_names():
		tkinter.ttk.Style().theme_use(theme)
		break


####### Settings ###########

class App(tkinter.Frame):

	def __init__(self):
		tkinter.Frame.__init__(self)

		self.master.title("PathVision")
		self.master.protocol("WM_DELETE_WINDOW", self.on_close)

		self.display = Display(self)
		self.display.pack(fill=tkinter.BOTH, expand=True, side="left", padx=(15,5), pady=15)#fill=BOTH, expand=1

		self.controls = Controls(self)
		self.controls.pack(fill=tkinter.Y, side="right", padx=(5,15), pady=5)

		self.AG = graph.AugmentedGraph()
		self.A = None
		self.CA = None
		self.states = None
		self.time = None

		self.setWithPaths(True)
		self._load("examples/example1.pv")

		self.setWithPaths(True)
		self.stopCalculating()
		self.setAlgebra(displayAlgebra.maxMin, True)

		self.pack()
		tkinter.mainloop()



	# Window events

	def on_close(self):
		self.destroy()
		quit()


	# Graph adjustments

	def addNode(self, x, y):
		self.AG.addNode(x, y)
		if self.states:
			self.startCalculating()

	def deleteNode(self, n):
		self.AG.deleteNode(n)
		if self.states:
			self.startCalculating()

	def selectNode(self, n):
		self.AG.selectNode(n)

	def deselectNode(self):
		self.AG.deselectNode()

	def moveNode(self, n, x, y):
		self.AG.moveNode(n, x, y)


	def setSource(self, n):
		self.AG.setSource(n)

		if self.time:
			self.time = 0
			self.timeChanged()

		self.display.draw()

	def addEdge(self, e):
		self.AG.addEdge(e, self.A.defaultEdge)
		if self.states:
			self.startCalculating()

	def deleteEdge(self, e):
		if e == self.AG.selectedEdge:
			self.deselectEdge()

		self.AG.deleteEdge(e)
		if self.states:
			self.startCalculating()

	def selectEdge(self, e):
		a, b = e
		self.AG.selectEdge(e)
		self.controls.edgeSelected(self.AG.G[a][b]['weight'])

	def deselectEdge(self):
		self.AG.deselectEdge()
		self.controls.edgeDeselected()

	def setSelectedEdgeValue(self, value):
		self.AG.setSelectedEdgeValue(value)
		if self.states:
			self.startCalculating()
		else:
			self.display.draw()


	# Algebra adjustments

	def setAlgebra(self, A, reset):
		if self.A == A:
			return

		self.A = A
		self.CA = displayAlgebra.DisplayAlgebra.trackPaths(A) if self.withPaths else A

		self.controls.algebraChanged(A)
		if self.AG.selectedNode:
			self.deselectNode()
		if self.AG.selectedEdge:
			self.deselectEdge()

		if reset:
			self.AG.resetEdgeValues(A.defaultEdge)

		self.stopCalculating()
		self.display.draw()


	def setWithPaths(self, v):
		self.withPaths = v
		self.controls.withPathsChanged(v)

		if self.A:
			self.CA = displayAlgebra.DisplayAlgebra.trackPaths(self.A) if self.withPaths else self.A




	# Calculations

	def stateAt(self, time):
		return [row[self.AG.sourceNode] for row in self.states[time]]

	def startCalculating(self):
		nodes = self.AG.G.nodes()
		n = len(nodes)

		if self.withPaths:
			self.idM = [[(self.A.A.one, [i]) if i == j else None for j in range(n)] for i in range(n)]
			self.adM = [[self.AG.G[i][j]['weight'] if j in self.AG.G[i] else None for j in range(n)] for i in range(n)]
		else:
			self.idM = [[self.A.A.one if i == j else self.A.A.zero for j in range(n)] for i in range(n)]
			self.adM = [[self.AG.G[i][j]['weight'] if j in self.AG.G[i] else self.A.A.zero for j in nodes] for i in nodes]

		i = 2
		self.states = [self.idM, bellmanFord.iterate(self.CA.A, self.idM, self.idM, self.adM)]
		while i <= n and self.states[-1] != self.states[-2]:
			newState = bellmanFord.iterate(self.CA.A, self.states[-1], self.idM, self.adM)
			self.states.append(newState)
			i += 1

		self.time = 0
		self.timeChanged()
		self.display.startedCalculating()


	def stopCalculating(self):
		self.states = []
		self.time = None
		self.display.stoppedCalculating()

	def moveToStart(self):
		self.time = 0
		self.timeChanged()

	def moveBack(self):
		self.time -= 1
		self.timeChanged()

	def moveForwards(self):
		self.time += 1
		if self.time == len(self.states):
			self.states.append(bellmanFord.iterate(self.CA.A, self.states[-1], self.idM, self.adM))
		self.timeChanged()

	def moveToEnd(self):
		i = 0
		while i + 1 < len(self.states):
			if self.stateAt(i) == self.stateAt(i+1):
				self.time = i
				break
			i += 1

		self.timeChanged()

	def timeChanged(self):

		convergedNow = self.stateAt(self.time) == self.stateAt(self.time+1)
		convergedThen = self.stateAt(-2) == self.stateAt(-1)

		canProceed = not convergedNow
		canProceedToEnd = canProceed and convergedThen

		self.display.timeChanged(self.time, canProceed, canProceedToEnd)



	# Loading and saving

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
		self.setWithPaths(data['withPaths'])


		for A in displayAlgebra.examples:
			if A.name == data['algebra']:
				self.setAlgebra(A, False)

		self.display.draw()


	def _printState(self, state):
		print("")
		for row in state:
			print(row)

if __name__ == '__main__':
	App()
	sys.exit()