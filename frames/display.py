import math

import tkinter
from tkinter import ttk

import networkx as nx

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


from settings import *

class Display(tkinter.ttk.Frame):

	def __init__(self, parent):
		tkinter.ttk.Frame.__init__(self, parent)
		self.parent = parent

		## Visual set up

		self.figure = plt.figure(facecolor="white", figsize=(15,10))
		self.axes = self.figure.add_subplot(111)
		plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
		plt.axis('off')
		
		self.canvas = FigureCanvasTkAgg(self.figure, master=self)
		self.canvas.show()
		self.canvas.get_tk_widget().grid(row=0,column=0,sticky="NEW")

		self.navigation = tkinter.ttk.Frame(self)
		self.navigation.grid(row=1,column=0, pady=(10,0))

		self.startB = tkinter.Button(self.navigation, text="<<", command=self.parent.moveToStart)
		self.startB.grid(row=0,column=0)
		self.startB.configure(state=tkinter.DISABLED)

		self.backB = tkinter.Button(self.navigation, text="<", command=self.parent.moveBack)
		self.backB.grid(row=0,column=1)
		self.backB.configure(state=tkinter.DISABLED)

		self.calculateB = tkinter.Button(self.navigation, width=5)
		self.calculateB.grid(row=0,column=2)

		self.forwardsB = tkinter.Button(self.navigation, text=">", command=self.parent.moveForwards)
		self.forwardsB.grid(row=0,column=3)
		self.forwardsB.configure(state=tkinter.DISABLED)

		self.endB = tkinter.Button(self.navigation, text=">>", command=self.parent.moveToEnd)
		self.endB.grid(row=0,column=4)
		self.endB.configure(state=tkinter.DISABLED)

		## Callbacks

		self.figure.canvas.callbacks.connect('button_press_event', self._mouseDown)
		self.figure.canvas.callbacks.connect('button_release_event', self._mouseUp)
		self.figure.canvas.callbacks.connect('motion_notify_event', self._mouseMove)
		

		## State

		self.nodeCounter = 5;
		self.dragTarget = None;
		self.dragged = False;
		self.selectTarget = None;


	#############
	## Getters ##
	#############

	def _findNearestNode(self, x, y):
		return min([((math.sqrt((x2-x)**2 + (y2-y)**2)), n) for n, (x2, y2) in self.parent.AG.pos.items()])

	def _findNearestEdge(self, x0, y0):
		edges = []
		for n1, n2 in self.parent.AG.G.edges():
			x1, y1 = self.parent.AG.pos[n1]
			x2, y2 = self.parent.AG.pos[n2]

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

	############
	## Events ##
	############

	def _mouseDown(self, event):
		if event.xdata and event.ydata:

			x, y = event.xdata, event.ydata
			d, n = self._findNearestNode(x, y)

			if event.button == 1 and d <= NODE_SIZE_N:
				self.dragTarget = n
				if event.dblclick:
					self.parent.setSource(n)
			self.draw()


	def _mouseUp(self, event):
		if event.xdata and event.ydata:

			x, y = event.xdata, event.ydata
			nDistance, n = self._findNearestNode(x, y)
			eDistance, e = self._findNearestEdge(x, y)

			if event.button == 3:
				if nDistance <= NODE_SIZE_N:
					if len(self.parent.AG.G.nodes()) > 1:
						self.parent.deleteNode(n)
				elif eDistance <= NODE_SIZE_N:
					self.parent.deleteEdge(e)
			elif event.button == 1:
				if nDistance <= NODE_SIZE_N and not self.dragged:
					if self.parent.AG.selectedEdge is not None:
						self.parent.deselectEdge()
					if self.parent.AG.selectedNode is not None and n != self.parent.AG.selectedNode:
						self.parent.addEdge((self.parent.AG.selectedNode, n))
						self.parent.deselectNode()
					else:
						self.parent.selectNode(n)
				elif eDistance <= NODE_SIZE_N and not self.dragged:
					if self.parent.AG.selectedNode is not None:
						self.parent.deselectNode()
					if self.parent.AG.selectedEdge is not None:
						self.parent.deselectEdge()
					self.parent.selectEdge(e)
				elif self.parent.AG.selectedNode is not None:
					self.parent.deselectNode()
				elif self.parent.AG.selectedEdge is not None:
					self.parent.deselectEdge()
				elif nDistance >= NODE_SIZE_N*2:
					self.parent.addNode(x,y)

			self.dragTarget = None
			self.dragged = False;

			self.draw()

	def _mouseMove(self, event):
		if event.xdata and event.ydata and self.dragTarget is not None:
			self.parent.moveNode(self.dragTarget, event.xdata, event.ydata)
			self.dragged = True;
			self.draw()
	

	#############
	## Actions ##
	#############


	def startedCalculating(self):
		self.calculateB.configure(text="Stop", command=self.parent.stopCalculating)
		self.timeChanged(0, True)

	def stoppedCalculating(self):
		self.calculateB.configure(text="Start", command=self.parent.startCalculating)

		self.startB.configure(state=tkinter.DISABLED)
		self.backB.configure(state=tkinter.DISABLED)
		self.forwardsB.configure(state=tkinter.DISABLED)
		self.endB.configure(state=tkinter.DISABLED)

		self.figure.suptitle("")
		self.draw()


	def timeChanged(self, t, canProceed):

		bState = tkinter.ACTIVE if t else tkinter.DISABLED
		fState = tkinter.ACTIVE if canProceed else tkinter.DISABLED

		self.startB.configure(state=bState)
		self.backB.configure(state=bState)
		self.forwardsB.configure(state=fState)
		self.endB.configure(state=fState)

		self.figure.suptitle("t = " + str(t))
		self.draw()

	# Drawing

	def draw(self):
		self.axes.cla()
		plt.axis('off')

		edgeLabels = nx.get_edge_attributes(self.parent.AG.G, 'weight')
		nx.draw_networkx(self.parent.AG.G, self.parent.AG.pos, ax=self.axes, **self.parent.AG.getKwargs())
		nx.draw_networkx_edge_labels(self.parent.AG.G, self.parent.AG.pos, ax=self.axes, edge_labels=edgeLabels, label_pos=0.35)

		if self.parent.states:
			state = self.parent.states[self.parent.time]
			nodeLabels = {n : state[n][self.parent.AG.sourceNode] for n in self.parent.AG.G.nodes()}
			offsetPos = {n : [x, y + self._calculateLabelOrientation(n)*LABEL_OFFSET] for n , (x, y) in self.parent.AG.pos.items()}
			nx.draw_networkx_labels(self.parent.AG.G, offsetPos, ax=self.axes, labels=nodeLabels, font_weight="bold", font_color="r")

		self.axes.set_xlim([-2,2])
		self.axes.set_ylim([-2,2])
		self.canvas.draw()

	def _calculateLabelOrientation(self, n):
		xn,yn = self.parent.AG.pos[n]

		neighbours = [n for n, _ in self.parent.AG.G.in_edges()] + [n for _, n in self.parent.AG.G.out_edges()]

		if neighbours:
			neighbourPos = [self.parent.AG.pos[m] for m in neighbours]
			neighbourAngles = sorted([(math.atan2(y - yn, x-xn) + 3*math.pi/2) % (math.pi*2) for x, y in neighbourPos])

			nearestUp = min([abs(a-math.pi) for a in neighbourAngles])
			nearestDown = min([a if a < math.pi else (2*math.pi - a) for a in neighbourAngles])
			
			if nearestUp < nearestDown:
				return 1
			else:
				return -1
		else:
			return 1


			
