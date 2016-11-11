
import networkx as nx

class AugmentedGraph():

	def __init__(self):
		self.G = nx.DiGraph()
		self.G.add_node(0)

		self.pos = nx.circular_layout(self.G)
		self.labelled = {n:True for n in self.G}

		self.selectedEdge = None
		self.selectedNode = None
		self.sourceNode = self.G.nodes()[0]

	# Node operations

	def addNode(self, x, y):
		n = len(self.G)
		self.G.add_node(n)
		self.pos[n] = [x, y]
		self.labelled[n] = True

		self.relabel()

	def deleteNode(self, n):
		del self.pos[n]
		del self.labelled[n]

		self.G.remove_node(n)

		if n == self.sourceNode:
			self.sourceNode = self.G.nodes()[0]

		self.relabel()


	def moveNode(self, n, x, y):
		self.pos[n] = [x , y]

	def selectNode(self, n):
		self.selectedNode = n

	def deselectNode(self):
		self.selectedNode = None

	def setSource(self, n):
		self.sourceNode = n

	def toggleLabel(self, n):
		self.labelled[n] = not self.labelled[n]

	# Edge operations

	def addEdge(self, e, w):
		self.G.add_edge(*e, weight=w)

	def deleteEdge(self, e):
		self.G.remove_edge(*e)

	def selectEdge(self, e):
		self.selectedEdge = e

	def deselectEdge(self):
		self.selectedEdge = None

	def setSelectedEdgeValue(self, value):
		a, b = self.selectedEdge
		self.G[a][b]['weight'] = value

	def resetEdgeValues(self, value):
		for a, b in self.G.edges():
			self.G[a][b]['weight'] = value



	# Getters

	def relabel(self, mapping=None):
		if not mapping:
			mapping = {n : i for i, n in enumerate(self.G)}
		
		self.pos = {mapping[n] : self.pos[n] for n in self.G}
		self.labelled = {mapping[n] : self.labelled[n] for n in self.G}
		self.sourceNode = mapping[self.sourceNode]
		nx.relabel_nodes(self.G,mapping,False)

	def loadFromAdjacencyMatrix(self, adM):
		self.G = nx.DiGraph()

		for i in range(len(adM)):
			self.G.add_node(i)

		for i in range(len(adM)):
			for j in range(len(adM)):
				if adM[i][j]:
					self.G.add_edge(i, j, weight=adM[i][j])

		self.sourceNode
		self.pos = nx.circular_layout(self.G)
		self.labelled = {n:True for n in self.G}