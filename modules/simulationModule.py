import tkinter

import theory.bellmanFord as bellmanFord

################
## Controller ##
################

class SimulationController():

	def __init__(self, mode, parent):
		self._model = SimulationModel()
		self._view  = SimulationView(self, parent)
		self._mode  = mode

		self._model.enterInactiveState()
		self._view.enterInactiveState()

	################
	## Commands

	def endSimulation(self):
		self._view.enterInactiveState()
		self._model.enterInactiveState()

		self._mode.draw()

	def startSimulation(self):
		algebra   = self._mode.algebraController.getComputationAlgebra()
		withPaths = self._mode.algebraController.getWithPaths()
		graph     = self._mode.graphController.getGraph()

		self._model.enterSimulationState(algebra, withPaths, graph)
		self._simulationTimeChanged()
		
	def moveToStart(self):
		self._model.moveToStart()
		self._simulationTimeChanged()

	def moveBack(self):
		self._model.moveBack()
		self._simulationTimeChanged()

	def moveForwards(self):
		self._model.moveForwards()
		self._simulationTimeChanged()
		
	def moveToEnd(self):
		self._model.moveToEnd()
		self._simulationTimeChanged()

	############
	## Getters

	def getCurrentTime(self):
		return self._model.currentTime

	def getCurrentState(self):
		return self._model.getCurrentState()
	
	def isSimulating(self):
		return self._model.isSimulating

	def hasConverged(self):
		return self._model.hasConverged()

	def getConvergenceTime(self):
		return self._model.getConvergenceTime()

	#############
	## Internal

	def _simulationTimeChanged(self):
		self._view.enterSimulationState(
			self._model.canMoveToStart(),
			self._model.canMoveBack(),
			self._model.canMoveForward(),
			self._model.canMoveToEnd()
		)
		self._mode.draw()


###########
## Model ##
###########

class SimulationModel():
	
	def __init__(self):
		pass


	############
	## Actions

	def enterInactiveState(self):
		self.isSimulating = False
		self.computation = None
		self.currentTime = None

	def enterSimulationState(self, algebra, withPaths, graph):
		self.isSimulating = True
		self.algebra = algebra
		self.identityMatrix = bellmanFord.createIdentityMatrix(algebra, len(graph))
		self.adjacencyMatrix = bellmanFord.createAdjacencyMatrix(algebra, graph)
		self.graph = graph

		state1 = self.identityMatrix
		state2 = bellmanFord.iterate(self.algebra, state1, self.identityMatrix, self.adjacencyMatrix)

		self.computation = [state1, state2]	
		self.currentTime = 0

		self.simulate(len(graph)**2)
	
	def simulate(self, steps):
		i = 0
		while not self.hasConverged() and i < steps:
			currentState = self.computation[-1]
			newState = bellmanFord.iterate(self.algebra, currentState, self.identityMatrix, self.adjacencyMatrix)
			self.computation.append(newState)
			i += 1

	def moveToStart(self):
		self.currentTime = 0

	def moveBack(self):
		self.currentTime -= 1

	def moveForwards(self):
		if self.currentTime > len(self.computation) - 2:
			self.simulate(1)
		self.currentTime += 1

	def moveToEnd(self):
		self.currentTime = len(self.computation)-2

	############
	## Getters

	def hasConverged(self):
		return len(self.computation) >= 2 and self.computation[-1] == self.computation[-2]

	def canMoveToStart(self):
		return self.currentTime > 0

	def canMoveBack(self):
		return self.currentTime > 0

	def canMoveForward(self):
		return (not self.hasConverged()) or (self.currentTime < len(self.computation) - 2)

	def canMoveToEnd(self):
		return self.hasConverged() and self.currentTime < len(self.computation) - 2

	def getCurrentState(self):
		state = self.computation[self.currentTime]
		source = self.graph.sourceNode
		return {n:state[n][source] for n in range(len(self.graph))}

	def getConvergenceTime(self):
		if self.hasConverged():
			return len(self.computation)-2
		else:
			return None


##########
## View ##
##########

class SimulationView(tkinter.Frame):
	
	def __init__(self, controller, parent, *args, **kwargs):
		tkinter.Frame.__init__(self, parent, *args, **kwargs)
		self.controller = controller

		self.startB 	= tkinter.Button(self, text="<<",command=controller.moveToStart)
		self.backB 		= tkinter.Button(self, text="<", command=controller.moveBack)
		self.commandB	= tkinter.Button(self, width=5)
		self.forwardsB 	= tkinter.Button(self, text=">", command=controller.moveForwards)
		self.endB 		= tkinter.Button(self, text=">>",command=controller.moveToEnd)
		
		self.startB.grid(row=0,column=1)
		self.backB.grid(row=0,column=2)
		self.commandB.grid(row=0,column=3)
		self.forwardsB.grid(row=0,column=4)
		self.endB.grid(row=0,column=5)

		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(6, weight=1)


	#######################
	## Configure buttons ##
	#######################

	def enterInactiveState(self):
		self.startB.configure(state=tkinter.DISABLED)
		self.backB.configure(state=tkinter.DISABLED)
		self.forwardsB.configure(state=tkinter.DISABLED)
		self.endB.configure(state=tkinter.DISABLED)

		self.commandB.configure(text="Start", command=self.controller.startSimulation)

	def enterSimulationState(self, start, back, forward, end):
		self.startB.configure(state=tkinter.ACTIVE if start else tkinter.DISABLED)
		self.backB.configure(state=tkinter.ACTIVE if back else tkinter.DISABLED)
		self.forwardsB.configure(state=tkinter.ACTIVE if forward else tkinter.DISABLED)
		self.endB.configure(state=tkinter.ACTIVE if end else tkinter.DISABLED)

		self.commandB.configure(text="Stop", command=self.controller.endSimulation)