import math

import tkinter
from tkinter import ttk

import networkx as nx

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from settings import NODE_SIZE, NODE_COLOUR, SOURCE_NODE_COLOUR, NODE_LABEL_OFFSET


################
## Controller ##
################

class GraphController():

	def __init__(self, mode, parent):
		self._model = GraphModel()
		self._view  = GraphView(self, parent)
		self._mode 	= mode

		self.selectedNode = None
		self.mouseOverNode = None
		self.dragging = False

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

	def setSourceNode(self, node):
		self._model.setSourceNode(node)

	def resetEdgeWeights(self, value):
		self._model.resetEdgeWeights(value)

	def draw(self, titleText, nodeLabels):
		outlinedNodes = []
		if self.selectedNode is not None:
			outlinedNodes.append(self.selectedNode)
		if self.mouseOverNode is not None:
			outlinedNodes.append(self.mouseOverNode)

		self._view.draw(
			titleText 	 	= titleText, 
			graph 			= self._model.graph, 
			nodePositions 	= self._model.nodePositions, 
			nodeLabels 		= nodeLabels, 
			outlinedNodes 	= outlinedNodes, 
			colouredNodes 	= []
		)

	#############
	## Getters

	def getGraph(self):
		return self._model.graph

	def getNodeLabelling(self):
		return self._model.nodeLabelling

	##############
	## Internal

	def _leftClickOnNode(self, n):
		if self.selectedNode is not None and n != self.selectedNode:
			algebra = self._mode.algebraController.getBaseAlgebra()
			self._model.addEdge((self.selectedNode, n), algebra.defaultEdge)
			self.selectedNode = n
			self._mode.problemLabellingChanged()
		else:
			self.selectedNode = n
			self._mode.problemTopologyChanged()

	def _leftDoubleClickOnNode(self, n):
		self._model.setSourceNode(n)
		self._mode.problemLabellingChanged()

	def _leftClickOnEdge(self, e):
		algebra = self._mode.algebraController.getBaseAlgebra()
		currentValue = self._model.graph[e[0]][e[1]]['weight']
		self._view.startEdgeInput(algebra, currentValue, self._setEdgeValue)
		self.selectedNode = None
		self.selectedEdge = e

	def _leftClickOnSpace(self, position):
		n = self._model.addNode(position)
		self.mouseOverNode = n
		self._mode.problemTopologyChanged()
		self.selectedEdge = None
		self.selectedNode = n

	def _rightClickOnSpace(self, position):
		self.selectedEdge = None
		self.selectedNode = None
		self._mode.problemLabellingChanged()
		
	def _middleClickOnNode(self, n):
		self._model.toggleNodeLabel(n)
		self._mode.problemLabellingChanged()

	def _rightClickOnNode(self, n):
		if len(self._model.graph) > 1:
			if n == self.mouseOverNode:
				self.mouseOverNode = None
			if n == self.selectedNode:
				self.selectedNode = None
			self._model.deleteNode(n)
			self._mode.problemTopologyChanged()

	def _rightClickOnEdge(self, e):
		self.selectedEdge = None
		self.selectedNode = None
		self._model.deleteEdge(e)
		self._mode.problemTopologyChanged()

	def _nodeDraggedTo(self, node, position):
		self._model.moveNode(node, position)
		self.mouseOverNode = node
		self.dragging = True
		self._mode.app.config(cursor="fleur")
		self._mode.problemLabellingChanged()

	def _nodeDragFinished(self,n):
		self.dragging = False
		self._mode.app.config(cursor="")

	def _setEdgeValue(self, newValue):
		self._view.cancelEdgeInput()
		self._model.setEdgeWeight(self.selectedEdge, newValue)

		self.selectedEdge = None
		self._mode.problemTopologyChanged()

	def _mouseInOverNode(self, n):
		self.mouseOverNode = n
		self._mode.problemLabellingChanged()

	def _mouseOutOverNode(self, n):
		if not self.dragging:
			self.mouseOverNode = None
			self._mode.problemLabellingChanged()


###########
## Model ##
###########

class GraphModel():

	def __init__(self):
		self.graph = nx.DiGraph()
		#self.graph.add_node(0)
		self.graph.sourceNode = None

		self.nodePositions = nx.circular_layout(self.graph)
		self.nodeLabelling = {n:True for n in self.graph}


	############
	## Operations

	# Add a new node at specified position
	def addNode(self, position):
		node = len(self.graph)

		self.graph.add_node(node)
		self.nodePositions[node] = position
		self.nodeLabelling[node] = True

		#self._relabel()
		return node

	# Delete the provided node from the graph
	def deleteNode(self, node):
		del self.nodePositions[node]
		del self.nodeLabelling[node]

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

	# Toggle whether the node is labelled
	def toggleNodeLabel(self, node):
		self.nodeLabelling[node] = not self.nodeLabelling[node]

	# Add an edge with the given weight
	def addEdge(self, edge, weight):
		self.graph.add_edge(*edge, weight=weight)

	# Delete the provided edge
	def deleteEdge(self, e):
		self.graph.remove_edge(*e)

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
		self.nodePositions = nx.circular_layout(graph)
		self.nodeLabelling = {n:True for n in graph}

	#############
	## Private

	def _findNearestNode(self, x, y):
		return min([((math.sqrt((x2-x)**2 + (y2-y)**2)), n) for n, (x2, y2) in self.nodePositions.items()])

	def _findNearestEdge(self, x0, y0):
		edges = []
		for n1, n2 in self.graph.edges():
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

			edges.append((dist, (n1, n2)))

		if edges:
			return min(edges)
		else:
			return float('inf'), None

	def _relabel(self, mapping=None):
		if not mapping:
			mapping = {n : i for i, n in enumerate(self.graph)}

		self.nodePositions = {mapping[n]:self.nodePositions[n] for n in self.graph}
		self.nodeLabelling = {mapping[n]:self.nodeLabelling[n] for n in self.graph}
		self.graph.sourceNode = mapping[self.graph.sourceNode]

		nx.relabel_nodes(self.graph, mapping, False)


##########
## View ##
##########

class GraphView(tkinter.Frame):

	def __init__(self, controller, parent, *args, **kwargs):
		tkinter.Frame.__init__(self, parent, *args, **kwargs, borderwidth=5, relief=tkinter.RIDGE)
			
		self.controller = controller

		self.setupCanvas()
		
		self.dragTarget = None
		self.dragged = False
		self.selectTarget = None
		self.mouseOverTarget = None

	def setupCanvas(self):
		self.figure = plt.figure(facecolor="white")
		plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
		plt.axis('off')
		self.axes = self.figure.add_subplot(111)
		
		self.canvas = FigureCanvasTkAgg(self.figure, master=self)
		self.canvas.show()
		self.canvas.get_tk_widget().pack(fill=tkinter.BOTH, expand=True)

		self.figure.canvas.callbacks.connect('button_press_event', self._mouseDown)
		self.figure.canvas.callbacks.connect('button_release_event', self._mouseUp)
		self.figure.canvas.callbacks.connect('motion_notify_event', self._mouseMove)


	#############
	## Actions

	def startEdgeInput(self, algebra, currentValue, inputCallback):
		self.edgeFrame = EdgeFrame(self, algebra, currentValue, inputCallback)
		self.edgeFrame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

	def cancelEdgeInput(self):
		self.edgeFrame.place_forget()

	##################
	## Mouse events

	def _mouseDown(self, event):
		if event.xdata and event.ydata:

			x, y = event.xdata, event.ydata
			d, n = self.controller._model._findNearestNode(x,y)

			if event.button == 1 and d <= NODE_SIZE:
				self.dragTarget = n
				if event.dblclick:
					self.controller._leftDoubleClickOnNode(n)


	def _mouseUp(self, event):
		if event.xdata and event.ydata:
			x, y = event.xdata, event.ydata
			nDistance, n = self.controller._model._findNearestNode(x,y)
			eDistance, e = self.controller._model._findNearestEdge(x,y)

			if event.button == 3:
				if nDistance <= NODE_SIZE:
					self.controller._rightClickOnNode(n)
				elif eDistance <= NODE_SIZE:
					self.controller._rightClickOnEdge(e)
				else:
					self.controller._rightClickOnSpace((x,y))

			if event.button == 2:
				if nDistance <= NODE_SIZE:
					self.controller._middleClickOnNode(n)

			if event.button == 1:
				if self.dragged:
					self.controller._nodeDraggedTo(self.dragTarget, (x,y))
					self.controller._nodeDragFinished(self.dragTarget)
					self.dragTarget = None
					self.dragged = False
				elif nDistance <= NODE_SIZE:
					self.controller._leftClickOnNode(n)
				elif eDistance <= NODE_SIZE:
					self.controller._leftClickOnEdge(e)
				else:
					self.controller._leftClickOnSpace((x,y))

	def _mouseMove(self, event):
		if event.xdata and event.ydata:
			x, y = event.xdata, event.ydata
			d, n = self.controller._model._findNearestNode(x,y)

			if event.button == 1 and self.dragTarget is not None:
				self.controller._nodeDraggedTo(self.dragTarget, (x,y))
				self.dragged = True;
			
			newMouseOverTarget = n if d <= NODE_SIZE else None
			if self.mouseOverTarget != newMouseOverTarget:
				if self.mouseOverTarget is not None:
					self.controller._mouseOutOverNode(self.mouseOverTarget)
				if newMouseOverTarget is not None:
					self.controller._mouseInOverNode(newMouseOverTarget)
			self.mouseOverTarget = newMouseOverTarget

	#############
	## Drawing

	def draw(self, titleText, graph, nodePositions, nodeLabels, outlinedNodes, colouredNodes):

		# Node outlines
		nodeOutlines = [1.0 for n in graph.nodes()]
		for node in outlinedNodes:
			nodeOutlines[node] = 2.0
		#nodeOutlines[graph.sourceNode] = 3.0

		# Node colours
		nodeColours = [NODE_COLOUR for n in graph.nodes()]
		for node in colouredNodes:
			nodeColours[node] = "red"
		if graph.sourceNode is not None:
			nodeColours[graph.sourceNode] = SOURCE_NODE_COLOUR

		# Node internal numbering
		nodeNumbers = nodeNumbers = {n : n for n in graph}
		nodeNumberPositions = nodePositions

		# Node labels
		nodeLabelPositions = {}
		for n in graph.nodes():
			x, y = nodePositions[n]
			direction = self._labelOrientation(n, graph, nodePositions)
			nodeLabelPositions[n] = (x, y + direction*NODE_LABEL_OFFSET)

		# Edge labels
		edgeLabels = nx.get_edge_attributes(graph, 'weight')

		# Configure canvas
		self.axes.cla()
		plt.axis('off')
		height = self.canvas.get_tk_widget().winfo_height()
		width = self.canvas.get_tk_widget().winfo_width()
		self.axes.set_xlim(-width/200, width/200)
		self.axes.set_ylim(-height/200, height/200)

		# Draw graph
		self.axes.text(10/width, 1 - 10/height, titleText, transform=self.axes.transAxes, verticalalignment='top', fontsize=12)
		res = nx.draw_networkx_nodes(graph, nodePositions, ax=self.axes, linewidths=nodeOutlines, node_color=nodeColours, edge_colour='black')
		nx.draw_networkx_edges(graph, nodePositions, ax=self.axes, arrows=True)
		nx.draw_networkx_labels(graph, nodeNumberPositions, ax=self.axes, labels=nodeNumbers)
		nx.draw_networkx_labels(graph, nodeLabelPositions, ax=self.axes, labels=nodeLabels, font_weight="bold", font_color="r", font_size=10)
		nx.draw_networkx_edge_labels(graph, nodePositions, ax=self.axes, edge_labels=edgeLabels, label_pos=0.35)
		if res:
			res.set_edgecolor("black") 
		self.canvas.draw()

		"""
		if not self.app.AG.labelled[n]:
			nodeLabels = {n : self._createNodeLabel(n) if self.states else "" for n in self.app.AG.G.nodes()}
		"""


	def _labelOrientation(self, n, graph, nodePositions):
		xn, yn = nodePositions[n]

		neighbours = {n for n, _ in graph.in_edges(n)}.union({n for _, n in graph.out_edges(n)})

		if neighbours:
			neighbourPos = [nodePositions[m] for m in neighbours]
			neighbourAngles = sorted([(math.atan2(y - yn, x-xn) + 3*math.pi/2) % (math.pi*2) for x, y in neighbourPos])

			nearestUp = min([abs(a-math.pi) for a in neighbourAngles])
			nearestDown = min([a if a < math.pi else (2*math.pi - a) for a in neighbourAngles])
			
			if nearestUp < nearestDown:
				return 1
			else:
				return -1
		else:
			return 1


class EdgeFrame(tkinter.Frame):

	def __init__(self, parent, algebra, currentValue, acceptCallback):
		tkinter.Frame.__init__(self, parent, borderwidth=3, relief=tkinter.GROOVE)

		self.edgeEntry = EdgeEntry(self, algebra, self.onEdit, self.onAccept)
		self.edgeEntry.grid(row=0, column=0, padx=(10,5), pady=10)

		self.acceptButton = tkinter.Button(self, text="Submit", command=self.onAccept)
		self.acceptButton.grid(row=0, column=1, padx=(5,10), pady=10)
		self.acceptCallback = acceptCallback

		self.edgeEntry.setValue(currentValue)
		self.edgeEntry.focus()

	def onEdit(self,x,y,z):
		value = self.edgeEntry.getValue()

		if value is None:
			self.acceptButton.configure(state=tkinter.DISABLED)
		else:
			self.acceptButton.configure(state=tkinter.ACTIVE)

	def onAccept(self):
		value = self.edgeEntry.getValue()

		if value is not None:
			self.acceptCallback(self.edgeEntry.getValue())

class EdgeEntry(tkinter.Frame):

	def __init__(self, parent, algebra, onEditCallback, onEnterCallback):
		tkinter.Frame.__init__(self, parent, borderwidth=0)

		self.subEntries = []
		self.algebra = algebra

		if algebra.componentAlgebras:
			for i, childAlgebra in enumerate(algebra.componentAlgebras):
				child = EdgeEntry(self, childAlgebra, onEditCallback, onEnterCallback)
				child.grid(row=0,column=i)
				self.subEntries.append(child)
		else:
			self.value = tkinter.StringVar()
			self.value.trace("w", onEditCallback)

			self.entry = tkinter.Entry(self, textvariable=self.value, width=5)
			self.entry.grid(row=0, column=0)
			self.entry.bind("<Return>", lambda e: onEnterCallback())

	def getValue(self):
		if self.subEntries:
			value = []
			for entry in self.subEntries:
				subvalue = entry.getValue()
				if subvalue is None:
					return None
				else:
					value.append(subvalue)
			return value
		else:
			v = self.value.get()
			if self.algebra.validateEdgeString(v):
				self.entry.configure(bg="#FFFFFF")
				return self.algebra.parseEdgeString(v)
			else:
				self.entry.configure(bg="#FFAAAA")
				return None

	def setValue(self, value):
		if self.subEntries:
			for x, entry in zip(value, self.subEntries):
				entry.setValue(x)
		else:
			self.value.set(value)

	def focus(self):
		if self.subEntries:
			self.subEntries[0].focus()
		else:
			self.entry.focus_set()
			self.entry.selection_range(0, tkinter.END)

	"""
	def verify(x, y, z, self):
		if self.algebra
	"""

"""
	def setState(self, state):
		if self.subEntries:
			for se in self.subEntries:
				se.setState(state)
		else:
			self.entry.configure(state=state)


	
"""