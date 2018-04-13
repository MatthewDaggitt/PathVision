import abc

from modules.shared.graphInteraction import Interaction, DrawData
from modules.shared.dialogs.edge import EdgeDialog

################
## Base class ##
################

class Behaviour():
	def _init_(self):
		pass

	@abc.abstractmethod
	def getTriggers():
		pass

	@abc.abstractmethod
	def processDrawData():
		pass

############################
## Some common behaviours ##
############################

# Highlights nodes when mouse passes over
class MouseOverBehaviour(Behaviour):

	def __init__(self, redraw):
		self.triggers = {
			Interaction.NODE_MOUSE_IN  	: self._onNodeMouseIn,
			Interaction.NODE_MOUSE_OUT 	: self._onNodeMouseOut
		}
		self._redraw = redraw

		self.mouseOverNode = None

	def processDrawData(self, drawData):
		if self.mouseOverNode is not None:
			if self.mouseOverNode in drawData.graph:
				drawData.outlinedNodes.append(self.mouseOverNode)
			else:
				self.mouseOverNode = None

	# Private methods
	def _onNodeMouseIn(self, n):
		self.mouseOverNode = n
		self._redraw()

	def _onNodeMouseOut(self, n):
		self.mouseOverNode = None
		self._redraw()


# Allows the dragging of nodes around the canvas
class NodeDraggingBehaviour(Behaviour):

	def __init__(self, redraw, moveNode):
		self.triggers = {
			Interaction.NODE_START_DRAG		: self._onNodeDragStart,
			Interaction.NODE_DRAGGED		: self._onNodeDragged,
			Interaction.NODE_FINISH_DRAG	: self._onNodeDragFinish
		}
		self._redraw = redraw
		self._moveNode = moveNode

		self.draggedNode = None

	def processDrawData(self, drawData):
		if self.draggedNode is not None:
			drawData.outlinedNodes.append(self.draggedNode)

	# Private methods
	def _onNodeDragStart(self, n):
		self.draggedNode = n

	def _onNodeDragged(self, position):
		self._moveNode(self.draggedNode, position)
		self._redraw()

	def _onNodeDragFinish(self, n):
		self.draggedNode = None


# Allows the addition and removal of nodes and edges to the graph
class EditTopologyBehaviour(Behaviour):

	def __init__(self, redraw, setSourceNode, addNode, deleteNode, addEdge, deleteEdge, getDefaultEdgeWeight):
		self.triggers = {
			Interaction.NODE_LEFT_CLICK 		: self._onNodeLeftClick,
			Interaction.NODE_LEFT_DOUBLE_CLICK 	: self._onNodeLeftDoubleClick,
			Interaction.NODE_RIGHT_CLICK 		: self._onNodeRightClick,
			Interaction.EDGE_RIGHT_CLICK 		: self._onEdgeRightClick,
			Interaction.SPACE_LEFT_CLICK 		: self._onSpaceLeftClick,
			Interaction.SPACE_RIGHT_CLICK 		: self._onSpaceRightClick
		}
		self._redraw 				= redraw
		self._setSourceNode			= setSourceNode
		self._addNode 				= addNode
		self._deleteNode 			= deleteNode
		self._addEdge 				= addEdge
		self._deleteEdge 			= deleteEdge
		self._getDefaultEdgeWeight 	= getDefaultEdgeWeight

		self.selectedNode = None
		self.selectedEdge = None

	def processDrawData(self, drawData):
		if self.selectedNode is not None:
			drawData.outlinedNodes.append(self.selectedNode)

	# Private methods
	def _onNodeLeftClick(self, n):
		if self.selectedNode is not None and n != self.selectedNode:
			self._addEdge((self.selectedNode, n), self._getDefaultEdgeWeight())
		self.selectedNode = n
		self._redraw()

	def _onNodeLeftDoubleClick(self, n):
		self._setSourceNode(n)
		self._redraw()

	def _onNodeRightClick(self, n):
		if self.selectedNode == n:
			self.selectedNode = None
		self._deleteNode(n)
		self._redraw()

	def _onEdgeRightClick(self, e):
		self.selectedEdge = None
		self.selectedNode = None
		self._deleteEdge(e)
		self._redraw()

	def _onSpaceLeftClick(self, position):
		n = self._addNode(position)
		self.selectedEdge = None
		self.selectedNode = n
		self._redraw()

	def _onSpaceRightClick(self, position):
		self.selectedEdge = None
		self.selectedNode = None
		self._redraw()

# Allows the addition and removal of node labels
class NodeLabellingBehaviour(Behaviour):

	def __init__(self, redraw):
		self.triggers = {
			Interaction.NODE_MIDDLE_CLICK : self._onNodeMiddleClick
		}
		self._redraw = redraw
		self.nonLabelledNodes = set()

	def processDrawData(self, drawData):
		for node in drawData.nodeOuterLabels:
			if node in self.nonLabelledNodes:
				drawData.nodeOuterLabels[node] = ""

	# Private methods
	def _onNodeMiddleClick(self, node):
		if node in self.nonLabelledNodes:
			self.nonLabelledNodes.remove(node)
		else:
			self.nonLabelledNodes.add(node)
		self._redraw()


# Allows the editing of edge values
class EdgeValueEditingBehaviour(Behaviour):

	def __init__(self, redraw, root, getAlgebra, getEdgeWeight, setEdgeWeight):
		self.triggers = {
			Interaction.EDGE_LEFT_CLICK : self._onEdgeLeftClick
		}
		self._root = root
		self._redraw = redraw
		self._getAlgebra = getAlgebra
		self._getEdgeWeight = getEdgeWeight
		self._setEdgeWeight = setEdgeWeight

	def processDrawData(self, drawData):
		pass

	# Private methods
	def _onEdgeLeftClick(self, edge):
		oldValue = self._getEdgeWeight(edge)

		dialog = EdgeDialog(self._root, self._getAlgebra(), oldValue)
		newValue = dialog.result
		if newValue is not None:
			self._setEdgeWeight(edge, newValue)
			self._redraw()