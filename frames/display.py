import math

import tkinter
from tkinter import ttk

import networkx as nx

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


from settings import *

class Display(tkinter.Frame):

	def __init__(self, parent, app):
		tkinter.Frame.__init__(self, parent, app)
		self.app = app


		## Visual set up

		self.figure = plt.figure(facecolor="white")
		self.axes = self.figure.add_subplot(111)
		plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
		plt.axis('off')
		
		self.canvas = FigureCanvasTkAgg(self.figure, master=self)
		self.canvas.show()
		self.canvas.get_tk_widget().pack(fill=tkinter.BOTH, expand=True)


		## Callbacks

		self.figure.canvas.callbacks.connect('button_press_event', self._mouseDown)
		self.figure.canvas.callbacks.connect('button_release_event', self._mouseUp)
		self.figure.canvas.callbacks.connect('motion_notify_event', self._mouseMove)
		

		## State

		self.dragTarget = None;
		self.dragged = False;
		self.selectTarget = None;

	#############
	## Getters ##
	#############

	def _findNearestNode(self, x, y, nodePositions):
		#print(x, y, self.canvas.get_tk_widget().winfo_width(), self.canvas.get_tk_widget().winfo_height())
		return min([((math.sqrt((x2-x)**2 + (y2-y)**2)), n) for n, (x2, y2) in nodePositions.items()])

	def _findNearestEdge(self, x0, y0):
		edges = []
		for n1, n2 in self.app.AG.G.edges():
			x1, y1 = self.app.AG.pos[n1]
			x2, y2 = self.app.AG.pos[n2]

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
			d, n = self._findNearestNode(x, y, self.app.AG.pos)

			if event.button == 1 and d <= NODE_SIZE_N:
				self.dragTarget = n
				if event.dblclick:
					self.app.setSourceNode(n)


	def _mouseUp(self, event):
		if event.xdata and event.ydata:

			x, y = event.xdata, event.ydata
			nDistance, n = self._findNearestNode(x, y, self.app.AG.pos)
			eDistance, e = self._findNearestEdge(x, y)

			sn = self.app.getSelectedNode()
			se = self.app.getSelectedEdge()

			if event.button == 3:
				if nDistance <= NODE_SIZE_N:
					if len(self.app.AG.G.nodes()) > 1:
						self.app.deleteNode(n)
				elif eDistance <= NODE_SIZE_N:
					self.app.deleteEdge(e)

			if event.button == 2:
				if nDistance <= NODE_SIZE_N:
					self.app.toggleNodeLabel(n)

			if event.button == 1:
				if self.dragged:
					self.app.moveNode(self.dragTarget, event.xdata, event.ydata)
					self.dragTarget = None
					self.dragged = False;
					return

				if nDistance <= NODE_SIZE_N or eDistance <= NODE_SIZE_N:

					if nDistance <= NODE_SIZE_N:
						if sn is not None and n != sn:
							self.app.addEdge((sn, n))
							self.app.deselectNode()
						else:
							self.app.selectNode(n)
						return

					if sn is not None:
						self.app.deselectNode()
					if se is not None:
						self.app.deselectEdge()
					self.app.selectEdge(e)
					return



				if se is not None:
					self.app.deselectEdge()
					return

				if sn is not None: 
					self.app.deselectNode()
					return

				if nDistance >= NODE_SIZE_N*2:
					self.app.addNode(x,y)
					

				



	def _mouseMove(self, event):
		if event.xdata and event.ydata and event.button == 1 and self.dragTarget is not None:
			self.app.moveNode(self.dragTarget, event.xdata, event.ydata)
			self.dragged = True;
			
			

	#############
	## Actions ##
	#############

	def startedCalculating(self):
		pass

	def stoppedCalculating(self):
		self.figure.suptitle("")

	def timeChanged(self, t, canProceed):
		self.figure.suptitle("t = " + str(t) + ("" if canProceed else " (CONVERGED)"))



	#############
	## Drawing ##
	#############

	def draw(self, G, nodeLabels, nodePositions, nodeColours, nodeOutlineWidths, edgeWidths):
		offsets =  {n : self._calculateLabelOrientation(n, G, nodePositions)*LABEL_OFFSET for n in G}
		offsetPos = {n : [x, y + offsets[n]] for n , (x, y) in nodePositions.items()}
		edgeLabels = nx.get_edge_attributes(G, 'weight')

		self.axes.cla()
		plt.axis('off')

		height = self.canvas.get_tk_widget().winfo_height()
		width = self.canvas.get_tk_widget().winfo_width()
		self.axes.set_xlim(-width/200, width/200)
		self.axes.set_ylim(-height/200, height/200)

		nx.draw_networkx(G, nodePositions, ax=self.axes, linewidths=nodeOutlineWidths, node_color=nodeColours, width=edgeWidths)
		nx.draw_networkx_labels(G, offsetPos, ax=self.axes, labels=nodeLabels, font_weight="bold", font_color="r")
		nx.draw_networkx_edge_labels(G, nodePositions, ax=self.axes, edge_labels=edgeLabels, label_pos=0.35)

		self.canvas.draw()
 


	def _calculateLabelOrientation(self, n, G, nodePositions):
		xn, yn = nodePositions[n]

		neighbours = [n for n, _ in G.in_edges()] + [n for _, n in G.out_edges()]

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