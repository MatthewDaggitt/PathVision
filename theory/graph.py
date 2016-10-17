
import networkx as nx

class AugmentedGraph():

	def __init__(self):
		self._nodeCounter = 5
		self.G = nx.DiGraph()
		self.G.add_node(0)

		self.pos = nx.circular_layout(self.G)

		self.selectedEdge = None
		self.selectedNode = None
		self.sourceNode = self.G.nodes()[0]

	# Node operations

	def addNode(self, x, y):
		self._nodeCounter += 1
		n = self._nodeCounter
		self.G.add_node(n)
		self.pos[n] = [x, y]

		self._relabel()

	def deleteNode(self, n):
		del self.pos[n]

		self.G.remove_node(n)

		if n == self.sourceNode:
			self.sourceNode = self.G.nodes()[0]

		self._relabel()


	def moveNode(self, n, x, y):
		self.pos[n] = [x , y]

	def selectNode(self, n):
		self.selectedNode = n

	def deselectNode(self):
		self.selectedNode = None

	def setSource(self, n):
		self.sourceNode = n


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

	def getKwargs(self):
		return {
			'linewidths' : [3.0 if n == self.selectedNode else 1.0 for n in self.G.nodes()],
			'node_color' : ["lightblue" if n == self.sourceNode else "lightgreen" for n in self.G.nodes()],
			'width'		 : [2.0 if e == self.selectedEdge else 1.0 for e in self.G.edges()]
		}


	def _relabel(self):
		mapping = {n : i for i, n in enumerate(self.G)}
		self.pos = {mapping[n] : self.pos[n] for n in self.G}
		self.sourceNode = mapping[self.sourceNode]
		nx.relabel_nodes(self.G,mapping,False)
