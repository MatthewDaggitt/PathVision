import math

import tkinter
from tkinter import ttk

import networkx as nx

from modules.shared.graphFrame import GraphFrame
from modules.shared.graphData import GraphData
from modules.shared.graphInteraction import DrawData
from modules.shared.graphBehaviours import *

################
## Controller ##
################

class GraphController():

	def __init__(self, mode, parent):
		self._mode 	= mode
		self._model = GraphModel()
		self._view  = GraphView(self, parent)

		self._mouseOverB = MouseOverBehaviour(
			self._mode.problemLabellingChanged
		)
		self._nodeDraggingB = NodeDraggingBehaviour(
			self._mode.problemLabellingChanged, 
			self._model.moveNode
		)
		self._editTopologyB = EditTopologyBehaviour(
			self._mode.problemTopologyChanged,
			self._model.setSourceNode,
			self._model.addNode,
			self._model.deleteNode,
			self._model.addEdge,
			self._model.deleteEdge,
			lambda: self._mode.algebraController.getBaseAlgebra().defaultEdge
		)
		self._nodeLabellingB = NodeLabellingBehaviour(
			self._mode.problemLabellingChanged
		)
		self._edgeEditingB = EdgeValueEditingBehaviour(
			self._mode.problemTopologyChanged,
			self._mode.app,
			lambda: self._mode.algebraController.getBaseAlgebra(),
			self._model.getEdgeWeight,
			self._model.setEdgeWeight
		)

		self._view.registerBehaviours([
			self._mouseOverB,
			self._nodeDraggingB,
			self._editTopologyB,
			self._nodeLabellingB,
			self._edgeEditingB
		])

	####################
	## Public methods

	def loadGraphData(self, edgeList, sourceNode, nodePositions):
		self._model.graph = nx.node_link_graph(edgeList)#, nodetype=int, create_using=nx.DiGraph())
		self._model.setSourceNode(sourceNode)
		self._model.nodePositions = nodePositions
		self._model.nodeLabelling = {n:True for n in self._model.graph}

	def saveGraphData(self):
		return {
			"edgeList" 	: nx.node_link_data(self._model.graph),
			"pos" 		: self._model.nodePositions,
			"source" 	: self._model.graph.sourceNode
		}
	
	def loadGraphFromAdjacencyMatrix(self, matrix):
		self._model.loadGraphFromAdjacencyMatrix(matrix)

	def resetEdgeWeights(self, value):
		self._model.resetEdgeWeights(value)

	def draw(self, titleText, nodeOuterLabels):
		drawData = DrawData(
			graph 			= self._model.graph,
			nodePositions 	= self._model.nodePositions,
			titleText 	 	= titleText,
			nodeOuterLabels	= nodeOuterLabels
		)
		self._view.draw(drawData)

	#############
	## Getters

	def getGraph(self):
		return self._model.graph


	"""
	def _leftClickOnEdge(self, e):
		algebra = self._mode.algebraController.getBaseAlgebra()
		currentValue = self._model.graph[e[0]][e[1]]['weight']
		self._view.startEdgeInput(algebra, currentValue, self._setEdgeValue)
		self.selectedNode = None
		self.selectedEdge = e
	"""
	
	"""
	def _setEdgeValue(self, newValue):
		self._view.cancelEdgeInput()
		self._model.setEdgeWeight(self.selectedEdge, newValue)

		self.selectedEdge = None
		self._mode.problemTopologyChanged()
	"""

###########
## Model ##
###########

class GraphModel(GraphData):
	
	def __init__(self):
		GraphData.__init__(self)

##########
## View ##
##########

class GraphView(GraphFrame):

	def __init__(self, controller, parent, *args, **kwargs):
		GraphFrame.__init__(self, controller, parent, *args, **kwargs)
		
	#############
	## Actions

	def startEdgeInput(self, algebra, currentValue, inputCallback):
		self.edgeFrame = EdgeFrame(self, algebra, currentValue, inputCallback)
		self.edgeFrame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

	def cancelEdgeInput(self):
		self.edgeFrame.place_forget()


