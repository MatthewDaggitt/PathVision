import tkinter
import networkx as nx

import settings
from modules.shared.graphFrame import GraphFrame
from modules.shared.graphData import GraphData
from modules.shared.graphInteraction import DrawData
from modules.shared.graphBehaviours import MouseOverBehaviour, NodeDraggingBehaviour, EditTopologyBehaviour
from theory.orders import PathPartialOrder

################
## Controller ##
################

class ChoiceController():

	def __init__(self, mode, parent):
		self._mode  = mode
		self._model = ChoiceModel()
		self._view  = ChoiceView(self, parent)

		self._mouseOverB = MouseOverBehaviour(
			self.draw
		)
		self._nodeDraggingB = NodeDraggingBehaviour(
			self.draw, 
			self._model.moveNode
		)
		self._editTopologyB = EditTopologyBehaviour(
			self._mode.graphTopologyChanged,
			self._model.setSourceNode,
			self._model.addNode,
			self._model.deleteNode,
			self._model.addEdge,
			self._model.deleteEdge,
			lambda: None
		)

		self._view.registerBehaviours([
			self._mouseOverB,
			self._nodeDraggingB,
			self._editTopologyB
		])

	#############
	## Actions 

	def draw(self):
		drawData = DrawData(
			graph 			= self._model.graph,
			nodePositions	= self._model.nodePositions,
			titleText 		= "Edit mode"
		)
		self._view.draw(drawData)
		
	def loadData(self, data):
		self._model.graph = nx.node_link_graph(data['edgeList'])
		self._model.setSourceNode(data['sourceNode'])
		self._model.nodePositions = data['nodePositions']

	def getSaveData(self):
		return {
			"edgeList" 		: nx.node_link_data(self._model.graph),
			"nodePositions" : self._model.nodePositions,
			"sourceNode"	: self._model.graph.sourceNode
		}

	#############
	## Getters

	def getGraph(self):
		return self._model.graph

###########
## Model ##
###########

class ChoiceModel(GraphData):

	def __init__(self):
		GraphData.__init__(self)

		self.addNode((0,0))
		self.setSourceNode(0)
		

##########
## View ##
##########

class ChoiceView(GraphFrame):

	def __init__(self, controller, parent):
		GraphFrame.__init__(self, controller, parent)