import tkinter
from itertools import groupby
from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
import networkx as nx

import settings
from modules.shared.graphFrame import GraphFrame
from modules.shared.graphInteraction import DrawData

################
## Controller ##
################

class PathDisplayController():

	def __init__(self, mode, parent):
		self._mode  = mode
		self._model = PathDisplayModel()
		self._view  = PathDisplayView(self, parent)

		"""
		self._mouseOverB = MouseOverBehaviour(
			self._mode.problemLabellingChanged
		)
		self._nodeLabellingB = NodeLabellingBehaviour(
			self._mode.problemLabellingChanged
		)

		self._view.registerBehaviours([
			self._mouseOverB,
			self._nodeDraggingB,
			self._editTopologyB,
			self._nodeLabellingB
		])
		"""

	def graphTopologyChanged(self):
		self._model.graphChanged(self._mode.choiceController.getGraph())

	def pathOrderingChanged(self,order):
		self._model.pathOrderingChanged(order)
		self.draw()

	def draw(self):
		nodes = self._model.disputeGraph.nodes()
		edges = self._model.disputeGraph.edges()
		orderEdges = self._model.additionalEdges
		n = len(self._model.graph.nodes())

		nodeLabels = {path:(0 if path == () else path[0]) for path in nodes}
		cmap = plt.get_cmap("gist_rainbow")
		edgeColours = [to_hex(cmap(e[0][0]/float(n-1))) if e in orderEdges else 'k' for e in edges]

		drawData = DrawData(
			graph 			= self._model.disputeGraph,
			nodePositions	= self._model.nodePositions,
			titleText 		= "Partial order",
			nodeInnerLabels	= nodeLabels,
			edgeColours     = edgeColours
		)
		self._view.draw(drawData)

	#############
	## Getters ##
	#############

	def getPaths(self):
		return self._model.paths

###########
## Model ##
###########

class PathDisplayModel():

	def __init__(self):
		pass

	def graphChanged(self, graph):

		# Create all paths
		paths = set()
		for n in graph.nodes():
			nPaths = nx.all_simple_paths(graph, source=n, target=graph.sourceNode)
			paths = paths.union({tuple(p) for p in nPaths if p[0] != p[-1]})
		paths.add((graph.sourceNode,))

		# Sort paths by length
		pathsByLength = defaultdict(list)
		for path in paths:
			pathsByLength[len(path)-1].append(path)
		for length in pathsByLength:
			pathsByLength[length].sort(key=lambda p: p[::-1])

		# Add all paths to graph
		disputeGraph = nx.DiGraph()
		for p in paths:
			disputeGraph.add_node(p)
		disputeGraph.sourceNode = ()

		# Enforce increasingness
		for p in paths:
			if len(p) != 1:
				disputeGraph.add_edge(p,p[1:])
		
		graphWidth = max([len(paths) for paths in pathsByLength.values()])
		nodePositions = {}
		border = 0.05
		if paths:
			graphDepth = max(pathsByLength.keys())+1

			for h, pathsAtDepth in pathsByLength.items():
				localWidth = len(pathsAtDepth)

				y = h - (graphDepth-1)*0.5

				if localWidth == 1:
					xs = [0.0]
				else:
					xs = [w - (localWidth-1)*0.5 for w in range(localWidth)]

				for path, x in zip(pathsAtDepth, xs):
					nodePositions[path] = (x,y)

		self.graph           = graph
		self.paths 		     = paths
		self.disputeGraph    = disputeGraph
		self.nodePositions   = nodePositions
		self.edgeColours   	 = 'k'
		self.additionalEdges = set()

	def pathOrderingChanged(self, order):
		while self.additionalEdges:
			self.disputeGraph.remove_edge(*self.additionalEdges.pop())


		for node in self.graph.nodes():
			sortedPaths = order.getSourceOrdering(node)
			for i in range(len(sortedPaths)-1):
				edge = (sortedPaths[i+1],sortedPaths[i])
				self.disputeGraph.add_edge(*edge)
				self.additionalEdges.add(edge)

	def _findNearestNode(self, x, y):
		return None

	def _findNearestEdge(self, x, y):
		return None

##########
## View ##
##########

class PathDisplayView(GraphFrame):

	def __init__(self, controller, parent):
		GraphFrame.__init__(self, controller, parent)
