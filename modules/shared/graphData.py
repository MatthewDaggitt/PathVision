import math

import networkx as nx

class GraphData():

	def __init__(self):
		self.graph = nx.DiGraph()
		self.graph.sourceNode = None

		self.nodePositions = nx.circular_layout(self.graph)

	############
	## Operations

	# Add a new node at specified position
	def addNode(self, position):
		node = len(self.graph)

		self.graph.add_node(node)
		self.nodePositions[node] = position

		#self._relabel()
		return node

	# Delete the provided node from the graph
	def deleteNode(self, node):
		del self.nodePositions[node]

		self.graph.remove_node(node)

		if self.graph.sourceNode == node:
			self.graph.sourceNode = 0

		self._relabel()

	# Move node to position (x,y)
	def moveNode(self, node, position):
		self.nodePositions[node] = position

	# Set the source node
	def setSourceNode(self, node):
		self.graph.sourceNode = node

	# Add an edge with the given weight
	def addEdge(self, edge, weight=None):
		if weight:
			self.graph.add_edge(*edge, weight=weight)
		else:
			self.graph.add_edge(*edge)
			
	# Delete the provided edge
	def deleteEdge(self, e):
		self.graph.remove_edge(*e)

	# Get the edge's weight
	def getEdgeWeight(self, edge):
		a, b = edge
		return self.graph[a][b]['weight']
	
	# Set the edge's weight
	def setEdgeWeight(self, edge, weight):
		a, b = edge
		self.graph[a][b]['weight'] = weight

	# Reset all edges to a given weight
	def resetEdgeWeights(self, weight):
		for a, b in self.graph.edges():
			self.graph[a][b]['weight'] = weight

	# Load graph from the provided adjacency matrix
	def loadGraphFromAdjacencyMatrix(self, matrix):
		n = len(matrix)
		graph = nx.DiGraph()

		graph.sourceNode = 0
		for i in range(n):
			graph.add_node(i)

		for i in range(n):
			for j in range(n):
				weight = matrix[i][j]
				if weight:
					graph.add_edge(i, j, weight=weight)

		self.graph = graph

		self.nodePositions = {}
		for i in range(n):
			angle = -(i*2*math.pi/n + math.pi/2)
			self.nodePositions[i] = [2*math.cos(angle), 2*math.sin(angle)]

		
	#############
	## Private

	def _findNearestNode(self, x, y):
		node, distanceSq = min(
			[(n, (x2-x)**2 + (y2-y)**2) for n, (x2, y2) in self.nodePositions.items()], 
			key=lambda x: x[1]
		)
		return node, math.sqrt(distanceSq)

	def _findNearestEdge(self, x0, y0):
		edges = self.graph.edges()
		if not edges:
			return None

		edgeData = []
		for n1, n2 in edges:
			x1, y1 = self.nodePositions[n1]
			x2, y2 = self.nodePositions[n2]

			px = x2-x1
			py = y2-y1

			u =  max(0 , min(1 , ((x0-x1)*px + (y0-y1)*py) / (px*px + py*py)))

			x = x1 + u*px
			y = y1 + u*py

			dx = x - x0
			dy = y - y0

			dist = math.sqrt(dx*dx + dy*dy)
			edgeData.append(dist)

		return min(zip(edges, edgeData), key=lambda x: x[1])
		
	def _relabel(self, mapping=None):
		if not mapping:
			mapping = {n : i for i, n in enumerate(self.graph)}

		self.nodePositions = {mapping[n]:self.nodePositions[n] for n in self.graph}
		self.graph.sourceNode = mapping[self.graph.sourceNode]

		nx.relabel_nodes(self.graph, mapping, False)