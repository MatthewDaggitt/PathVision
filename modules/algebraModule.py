import tkinter
import settings

from theory.algebra import DisplayAlgebra
from theory.algebraExamples import examples

################
## Controller ##
################

class AlgebraController():

	def __init__(self, mode, parent):
		self._model = AlgebraModel()
		self._view  = AlgebraView(self, parent, examples)
		self._mode  = mode

	############
	## Actions

	def setAlgebra(self, algebra):
		self._model.setAlgebra(algebra)
		self._view.setAlgebra(algebra)

	def setWithPaths(self, withPaths):
		self._model.setWithPaths(withPaths)
		self._view.setWithPaths(withPaths)

	def setAbbreviatePaths(self, abbreviatePaths):
		self._model.setAbbreviatePaths(abbreviatePaths)
		self._view.setAbbreviatePaths(abbreviatePaths)

	# Saving and loading
	
	def loadAlgebraData(self, algebraName, withPaths):
		self.setWithPaths(withPaths)

		for name, algebra in self._model.availableAlgebras.items():
			if name == algebraName:
				self.setAlgebra(algebra)
				return

		raise Exception("Tried to load algebra " + name + " but no corresponding algebra found")

	def saveAlgebraData(self):
		return {
			"algebra" 	: self._model.baseAlgebra.name,
			"withPaths" : self._model.withPaths
		}

	############
	## Getters

	def getBaseAlgebra(self):
		return self._model.baseAlgebra

	def getComputationAlgebra(self):
		return self._model.computationAlgebra

	def getWithPaths(self):
		return self._model.withPaths

	def getAbbreviatePaths(self):
		return self._model.abbreviatePaths

	#############
	## Internal

	def _changeAlgebra(self, algebra):
		if self._model.baseAlgebra != algebra:
			self.setAlgebra(algebra)
			self._mode.graphController.resetEdgeWeights(algebra.defaultEdge)
			self._mode.problemTopologyChanged()

	def _changeWithPaths(self, withPaths):
		self.setWithPaths(withPaths)
		self._mode.problemTopologyChanged()

	def _changeAbbreviatePaths(self, abbreviatePaths):
		self.setAbbreviatePaths(abbreviatePaths)
		self._mode.problemLabellingChanged()

###########
## Model ##
###########

class AlgebraModel():

	def __init__(self):
		self.availableAlgebras 	= {a.name:a for a in examples}
		self.withPaths 			= False
		self.abbreviatePaths 	= False
		self.baseAlgebra        = None
		self.computationAlgebra = None

		self.setAlgebra(examples[0])
	
	def setAlgebra(self, algebra):
		self.baseAlgebra = algebra
		self.setWithPaths(self.withPaths)

	def setWithPaths(self, withPaths):
		self.withPaths = withPaths
		if withPaths:
			self.computationAlgebra = DisplayAlgebra.trackPaths(self.baseAlgebra)
		else:
			self.computationAlgebra = self.baseAlgebra

	def setAbbreviatePaths(self, abbreviatePaths):
		self.abbreviatePaths = abbreviatePaths

##########
## View ##
##########

class AlgebraView(tkinter.Frame):

	def __init__(self, controller, parent, availableAlgebras):
		tkinter.Frame.__init__(self, parent, borderwidth=settings.BORDER_WIDTH, relief=tkinter.GROOVE)

		self.controller = controller
		self.algebras = {a.name:a for a in availableAlgebras}

		## Widgets

		self.headerL = tkinter.Label(self, text="Algebra", font="TkHeadingFont")

		self.algebraV = tkinter.StringVar()
		self.algebraL = tkinter.Label(self, text="Algebra:")
		self.algebraCB = tkinter.ttk.Combobox(self,textvariable=self.algebraV,values=list(self.algebras.keys()),state="readonly",width=10)
		self.algebraCB.current(0)
		self.algebraV.tid = self.algebraV.trace("w", self._onAlgebraWrite)

		self.withPathsV = tkinter.IntVar()
		self.withPathsL = tkinter.Label(self, text="Track paths:")
		self.withPathsChB = tkinter.Checkbutton(self, variable=self.withPathsV)
		self.withPathsV.tid = self.withPathsV.trace("w", self._onWithPathsWrite)

		self.abbreviatePathsV = tkinter.IntVar()
		self.abbreviatePathsL = tkinter.Label(self, text="Abbreviate paths:")
		self.abbreviatePathsChB = tkinter.Checkbutton(self, variable=self.abbreviatePathsV)
		self.abbreviatePathsV.tid = self.abbreviatePathsV.trace("w", self._onAbbreviatePathsWrite)

		self.headerL.grid(row=0,column=0,sticky="W")
		self.algebraL.grid(row=1,column=0,sticky="W")
		self.algebraCB.grid(row=1,column=1,sticky="EW",padx=(7,5))
		self.withPathsL.grid(row=2,column=0,sticky="W")
		self.withPathsChB.grid(row=2,column=1,sticky="W")
		self.abbreviatePathsL.grid(row=3,column=0,sticky="W")
		self.abbreviatePathsChB.grid(row=3,column=1,sticky="W")

	###############
	## User input

	def _onAlgebraWrite(self, *args):
		a = self.algebras[self.algebraV.get()]
		self.controller._changeAlgebra(a)

	def _onWithPathsWrite(self, *args):
		self.controller._changeWithPaths(bool(self.withPathsV.get()))

	def _onAbbreviatePathsWrite(self, *args):
		self.controller._changeAbbreviatePaths(bool(self.abbreviatePathsV.get()))

	##############
	## Setters

	def setAlgebra(self, A):
		self.algebraV.trace_vdelete("w", self.algebraV.tid)
		self.algebraV.set(A.name)
		self.algebraV.tid = self.algebraV.trace("w", self._onAlgebraWrite)

	def setWithPaths(self, v):
		self.withPathsV.trace_vdelete("w", self.withPathsV.tid)
		self.withPathsV.set(v)
		self.withPathsV.tid = self.withPathsV.trace("w", self._onWithPathsWrite)

		self.abbreviatePathsChB.configure(state=tkinter.NORMAL if v else tkinter.DISABLED)

	def setAbbreviatePaths(self, v):
		self.abbreviatePathsV.trace_vdelete("w", self.abbreviatePathsV.tid)
		self.abbreviatePathsV.set(v)
		self.abbreviatePathsV.tid = self.abbreviatePathsV.trace("w", self._onAbbreviatePathsWrite)