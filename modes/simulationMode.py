import math
import random
import pickle
import tkinter
import time

import networkx as nx

import settings

from modules.graphModule import GraphController
from modules.graphSearchModule import GraphSearchController
from modules.routingProblemStorageModule import RoutingProblemStorageController
from modules.simulationModule import SimulationController
from modules.algebraModule import AlgebraController

padding = 10

class SimulationMode(tkinter.Frame):

	def __init__(self, parent, app, *args, **kwargs):
		tkinter.Frame.__init__(self, parent, *args, **kwargs)

		self.app = app

		# Left hand side
		leftFrame = tkinter.Frame(self)
		label = tkinter.Label(leftFrame, text="Simulation mode", font=settings.TITLE_FONT)
		self.algebraController    	= AlgebraController(self, leftFrame)
		self.graphSearchController 	= GraphSearchController(self, leftFrame)
		self.routingProblemStorageController = RoutingProblemStorageController(self, leftFrame)

		label.grid(row=0,column=0, sticky="NW", pady=padding)
		self.algebraController._view.grid(row=1,column=0,sticky="NESW",pady=padding)
		self.graphSearchController._view.grid(row=2, column=0, sticky="NESW",pady=padding)
		self.routingProblemStorageController._view.grid(row=3, column=0, sticky="NESW",pady=padding)

		# Right hand side
		self.graphController      	 = GraphController(self, self)
		self.simulationController 	 = SimulationController(self, self)
		
		leftFrame.grid(row=0, column=0, rowspan=2, sticky="NESW", padx=padding, pady=(0,padding))
		self.graphController._view.grid(row=0,column=1,rowspan=5, sticky="NESW")
		self.simulationController._view.grid(row=6,column=1,sticky="NESW", pady=padding)

		self.rowconfigure(0,weight=1)
		self.columnconfigure(1,weight=1)

		self.draw()

	def activate(self):
		pass
		#self.stopCalculating()
		#self.app.graphDisplay.setManager(self._graphEditor)

	def deactivate(self):
		pass

	############################
	## Physical graph changes ##
	############################

	def problemTopologyChanged(self):
		self.simulationController.endSimulation()
	
	def problemLabellingChanged(self):
		self.draw()

	#############
	## Drawing ##
	#############

	def _constructLabels(self):
		graph = self.graphController.getGraph()

		if self.simulationController.isSimulating():
			state = self.simulationController.getCurrentState()
			labelling = self.graphController.getNodeLabelling()
			withPaths = self.algebraController.getWithPaths()
			abbreviatePaths = self.algebraController.getAbbreviatePaths()

			labels = {}
			for node in graph.nodes:
				value = state[node]
				if labelling[node]:
					if value is not None and withPaths and abbreviatePaths:
						x, p = value
						if len(p) > 3:
							value = "({}, [{},{}, ..., {}])".format(x,p[0],p[1],p[2])
				else:
					value = ""
				labels[node] = str(value)
		else:
			labels = {node:"" for node in graph.nodes}
		
		return labels
	
	def _constructTitle(self):
		if not self.simulationController.isSimulating():
			return "Edit mode"

		convergenceTime = self.simulationController.getConvergenceTime()
		time = self.simulationController.getCurrentTime()
		return "Simulation mode\nTime = " + str(time) + (" (Converged)" if time == convergenceTime else "")
		
	def draw(self):
		labels = self._constructLabels()
		title = self._constructTitle()
		self.graphController.draw(title, labels)


	###################
	## Internal load ##
	###################

	def loadRoutingProblem(self, data):
		self.simulationController.endSimulation()
		self.graphController.loadGraphData(data['edgeList'], data['source'], data['pos'])
		self.algebraController.loadAlgebraData(data['algebra'], data['withPaths'])

		self.draw()

	def saveRoutingProblem(self):
		graphData = self.graphController.saveGraphData()
		algebraData = self.algebraController.saveAlgebraData()
		return {**graphData, **algebraData}