from enum import Enum

class Interaction(Enum):
	NODE_LEFT_CLICK 		= 1,
	NODE_LEFT_DOUBLE_CLICK 	= 2,
	NODE_MIDDLE_CLICK 		= 3,
	NODE_RIGHT_CLICK 		= 4,
	NODE_START_DRAG 		= 5,
	NODE_DRAGGED 			= 6,
	NODE_FINISH_DRAG 		= 7,
	NODE_MOUSE_IN 			= 8,
	NODE_MOUSE_OUT 			= 9,

	EDGE_LEFT_CLICK 		= 10,
	EDGE_RIGHT_CLICK 		= 11,

	SPACE_RIGHT_CLICK 		= 12,
	SPACE_LEFT_CLICK 		= 13

class DrawData():

	def __init__(self, graph, nodePositions, titleText="", nodeInnerLabels=None, nodeOuterLabels=None, outlinedNodes=None, colouredNodes=None, edgeColours=None):
		self.graph 			= graph
		self.nodePositions 	= nodePositions
		self.titleText 		= titleText
		self.nodeInnerLabels= nodeInnerLabels 	if nodeInnerLabels 	else {node:str(node) for node in graph}
		self.nodeOuterLabels= nodeOuterLabels 	if nodeOuterLabels 	else {}
		self.outlinedNodes 	= outlinedNodes 	if outlinedNodes 	else []
		self.colouredNodes 	= colouredNodes 	if colouredNodes 	else []
		self.edgeColours    = edgeColours		if edgeColours		else 'k'