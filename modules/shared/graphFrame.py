import math
from collections import defaultdict

import tkinter
import networkx as nx
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from settings import NODE_SIZE, NODE_COLOUR, SOURCE_NODE_COLOUR, NODE_LABEL_OFFSET
from modules.shared.graphInteraction import Interaction


class GraphFrame(tkinter.Frame):

	def __init__(self, controller, parent, *args, **kwargs):
		tkinter.Frame.__init__(self, parent, *args, **kwargs, borderwidth=5, relief=tkinter.RIDGE)
			
		self.controller = controller

		self._setupCanvas()
		self._setupMouseInteractions()

		self.dragTarget = None
		self.dragged = False
		self.selectTarget = None
		self.mouseOverTarget = None

		self.behaviours = []
		self.triggers = defaultdict(set)
		self.nodePositions = {}

	def _setupCanvas(self):
		self.figure = plt.figure(facecolor="white")
		plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
		plt.axis('off')
		self.axes = self.figure.add_subplot(111)
		
		self.canvas = FigureCanvasTkAgg(self.figure, master=self)
		self.canvas.show()
		self.canvas.get_tk_widget().pack(fill=tkinter.BOTH, expand=True)

	def _setupMouseInteractions(self):
		self.press_callbackID 	= self.figure.canvas.callbacks.connect('button_press_event', self._mouseDown)
		self.release_callbackID = self.figure.canvas.callbacks.connect('button_release_event', self._mouseUp)
		self.move_callbackID 	= self.figure.canvas.callbacks.connect('motion_notify_event', self._mouseMove)

	"""
	def disableMouseInteractions(self):
		self.figure.canvas.mpl_disconnect(self.press_callbackID)
		self.figure.canvas.mpl_disconnect(self.release_callbackID)
		self.figure.canvas.mpl_disconnect(self.move_callbackID)
	"""

	#############
	## Drawing

	def registerBehaviours(self, behaviours):
		for behaviour in behaviours:
			for interaction, trigger in behaviour.triggers.items():
				self.triggers[interaction].add(trigger)
			self.behaviours.append(behaviour)

	def deregisterBehaviours(self, behaviours):
		for behaviour in behaviours:
			for interaction, trigger in behaviour.triggers.items():
				self.triggers[interaction].add(trigger)
			self.behaviours.remove(behaviour)

	def draw(self, drawData):
		# Apply the behaviours to the drawData
		for behaviour in self.behaviours:
			behaviour.processDrawData(drawData)

		# Store node positions
		self.nodePositions = drawData.nodePositions

		# Node outlines
		graph = drawData.graph
		nodeOutlines = [1.0 for n in graph.nodes()]
		for node in drawData.outlinedNodes:
			nodeOutlines[node] = 2.0

		# Node colours
		nodeColours = []
		for node in graph.nodes():
			if node in drawData.colouredNodes:
				nodeColours.append("red")
			elif node == drawData.graph.sourceNode:
				nodeColours.append(SOURCE_NODE_COLOUR)
			else:
				nodeColours.append(NODE_COLOUR)

		# Node labels
		nodeOuterLabelPositions = {}
		for n in graph.nodes():
			x, y = drawData.nodePositions[n]
			direction = self._labelOrientation(n, graph)
			nodeOuterLabelPositions[n] = (x, y + direction*NODE_LABEL_OFFSET)

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
		self.axes.text(10/width, 1 - 10/height, drawData.titleText, transform=self.axes.transAxes, verticalalignment='top', fontsize=12)
		res = nx.draw_networkx_nodes(graph, drawData.nodePositions, ax=self.axes, with_labels=False, labels=drawData.nodeInnerLabels, linewidths=nodeOutlines, node_color=nodeColours, edge_colour='black')
		nx.draw_networkx_edges(graph, drawData.nodePositions, ax=self.axes, edge_color=drawData.edgeColours, arrows=True)
		nx.draw_networkx_labels(graph, drawData.nodePositions, ax=self.axes, labels=drawData.nodeInnerLabels)
		nx.draw_networkx_labels(graph, nodeOuterLabelPositions, ax=self.axes, labels=drawData.nodeOuterLabels, font_weight="bold", font_color="r", font_size=10)
		nx.draw_networkx_edge_labels(graph, drawData.nodePositions, ax=self.axes, edge_labels=edgeLabels, label_pos=0.35)
		if res:
			res.set_edgecolor("black") 
		self.canvas.draw()


	##################
	## Mouse events

	def _triggerEvent(self, interaction, *args):
		for action in self.triggers[interaction]:
			action(*args)

	def _mouseDown(self, event):
		if event.xdata and event.ydata:
			x, y = event.xdata, event.ydata
			nodeData = self.controller._model._findNearestNode(x,y)

			if nodeData is not None:
				node, distance = nodeData
				if event.button == 1 and distance <= NODE_SIZE:
					self.dragTarget = node
					if event.dblclick:
						self._triggerEvent(Interaction.NODE_LEFT_DOUBLE_CLICK, node)


	def _mouseUp(self, event):
		if event.xdata and event.ydata:
			x, y = event.xdata, event.ydata
			nodeData = self.controller._model._findNearestNode(x,y)
			edgeData = self.controller._model._findNearestEdge(x,y)

			if nodeData is not None:
				node, nodeDistance = nodeData
				if event.button == 1:
					if self.dragged:
						self._triggerEvent(Interaction.NODE_DRAGGED, (x,y))
						self._triggerEvent(Interaction.NODE_FINISH_DRAG, node)
						self.dragTarget = None
						self.dragged = False
						return
					elif nodeDistance <= NODE_SIZE:
						self._triggerEvent(Interaction.NODE_LEFT_CLICK, node)
						return
				if event.button == 2 and nodeDistance <= NODE_SIZE:
					self._triggerEvent(Interaction.NODE_MIDDLE_CLICK, node)
					return
				if event.button == 3 and nodeDistance <= NODE_SIZE:
					self._triggerEvent(Interaction.NODE_RIGHT_CLICK, node)
					return

			if edgeData is not None:
				edge, edgeDistance = edgeData
				if event.button == 1 and edgeDistance <= NODE_SIZE:
					self._triggerEvent(Interaction.EDGE_LEFT_CLICK, edge)
					return
				if event.button == 3 and edgeDistance <= NODE_SIZE:
					self._triggerEvent(Interaction.EDGE_RIGHT_CLICK, edge)
					return

			if event.button == 1:
				self._triggerEvent(Interaction.SPACE_LEFT_CLICK, (x,y))
			if event.button == 3:
				self._triggerEvent(Interaction.SPACE_RIGHT_CLICK, (x,y))

	def _mouseMove(self, event):
		if event.xdata and event.ydata:
			x, y = event.xdata, event.ydata
			nodeData = self.controller._model._findNearestNode(x,y)

			if nodeData is not None:
				node, distance = nodeData
				if event.button == 1 and self.dragTarget is not None:
					if not self.dragged:
						self._triggerEvent(Interaction.NODE_START_DRAG, node)
						self.dragged = True
					self._triggerEvent(Interaction.NODE_DRAGGED, (x,y))
			
				newMouseOverTarget = node if distance <= NODE_SIZE else None
				if self.mouseOverTarget != newMouseOverTarget:
					if self.mouseOverTarget is not None:
						self._triggerEvent(Interaction.NODE_MOUSE_OUT, self.mouseOverTarget)
					if newMouseOverTarget is not None:
						self._triggerEvent(Interaction.NODE_MOUSE_IN, newMouseOverTarget)
				self.mouseOverTarget = newMouseOverTarget

	def _labelOrientation(self, n, graph):
		xn, yn = self.nodePositions[n]

		neighbours = {n for n, _ in graph.in_edges(n)}.union({n for _, n in graph.out_edges(n)})

		if neighbours:
			neighbourPos = [self.nodePositions[m] for m in neighbours]
			neighbourAngles = sorted([(math.atan2(y - yn, x-xn) + 3*math.pi/2) % (math.pi*2) for x, y in neighbourPos])

			nearestUp = min([abs(a-math.pi) for a in neighbourAngles])
			nearestDown = min([a if a < math.pi else (2*math.pi - a) for a in neighbourAngles])
			
			if nearestUp < nearestDown:
				return 1
			else:
				return -1
		else:
			return 1