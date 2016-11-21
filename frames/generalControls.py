import tkinter

from theory.displayAlgebra import examples
from frames.help import HelpText
# Settings

borderwidth=3


# Frames

class GeneralControls(tkinter.Frame):

	def __init__(self, parent, app):
		tkinter.Frame.__init__(self, parent)
		self.parent = parent
		
		padding = 10

		self._algebraControls = AlgebraControls(self, app)
		self._algebraControls.grid(row=0, column=0, sticky="EW", pady=padding)

		self._edgeControls = EdgeControls(self, app)
		self._edgeControls.grid(row=1, column=0, sticky="EW", pady=padding)

		self._searchControls = SearchControls(self, app)
		self._searchControls.grid(row=2, column=0, sticky="EW", pady=padding)

		self._helpB = tkinter.Button(self, text="Help & other information", command=self.displayHelp)
		self._helpB.grid(row=3,column=0, padx=5, pady=5, sticky="EWS")

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(3, weight=1)

	# Down

	def edgeSelected(self, value):
		self._edgeControls.edgeSelected(value)

	def edgeDeselected(self):
		self._edgeControls.edgeDeselected()

	def algebraChanged(self, A):
		self._edgeControls.algebraChanged(A)
		self._algebraControls.algebraChanged(A)

	def withPathsChanged(self, v):
		self._algebraControls.withPathsChanged(v)

	def searchUpdate(self, iterations, bestSoFar):
		self._searchControls.searchUpdate(iterations, bestSoFar)

	def searchEnded(self):
		self._searchControls.searchEnded()



	def displayHelp(self):
		window = tkinter.Toplevel(self)
		window.wm_title("PathVision help")
		helpText = HelpText(window)
		helpText.pack(side="top", fill="both", expand=True, padx=5, pady=5)


######################
## Algebra controls ##
######################


class AlgebraControls(tkinter.Frame):

	def __init__(self, parent, app):
		tkinter.Frame.__init__(self, parent, borderwidth=borderwidth, relief=tkinter.GROOVE)

		self.app = app

		self.headerL = tkinter.Label(self, text="Algebra settings", font="TkHeadingFont")

		self.algebraV = tkinter.StringVar()
		self.algebraL = tkinter.Label(self, text="Algebra:")
		self.algebraCB = tkinter.ttk.Combobox(
			self, 
			textvariable=self.algebraV, 
			values=[a.name for a in examples],
			width=10
		)
		self.algebraCB.current(0)
		self.algebraV.tid = self.algebraV.trace("w", self.setAlgebra)

		self.withPathsV = tkinter.IntVar()
		self.withPathsL = tkinter.Label(self, text="Track paths:")
		self.withPathsChB = tkinter.Checkbutton(self, variable=self.withPathsV)
		self.withPathsV.tid = self.withPathsV.trace("w", self.setWithPaths)

		self.abbreviatePathsV = tkinter.IntVar()
		self.abbreviatePathsL = tkinter.Label(self, text="Abbreviate paths:")
		self.abbreviatePathsChB = tkinter.Checkbutton(self, variable=self.abbreviatePathsV)
		self.abbreviatePathsV.tid = self.abbreviatePathsV.trace("w", self.setAbbreviatePaths)


		self.headerL.grid(row=0,column=0,sticky="W")
		self.algebraL.grid(row=1,column=0,sticky="W")
		self.algebraCB.grid(row=1,column=1,sticky="EW",padx=(7,5))
		self.withPathsL.grid(row=2,column=0,sticky="W")
		self.withPathsChB.grid(row=2,column=1,sticky="W")
		self.abbreviatePathsL.grid(row=3,column=0,sticky="W")
		self.abbreviatePathsChB.grid(row=3,column=1,sticky="W")

	def setAlgebra(self, a, b, c):
		v = self.algebraV.get()
		for A in examples:
			if A.name == v:
				self.app.setAlgebra(A, True)

	def setWithPaths(self, a, b, c):
		self.app.setWithPaths(bool(self.withPathsV.get()))

	def setAbbreviatePaths(self, a, b, c):
		self.app.setAbbreviatePaths(bool(self.abbreviatePathsV.get()))


	def algebraChanged(self, A):
		self.algebraV.trace_vdelete("w", self.algebraV.tid)
		self.algebraV.set(A.name)
		self.algebraV.tid = self.algebraV.trace("w", self.setAlgebra)

	def withPathsChanged(self, v):
		self.withPathsV.trace_vdelete("w", self.withPathsV.tid)
		self.withPathsV.set(v)
		self.withPathsV.tid = self.withPathsV.trace("w", self.setWithPaths)

		self.abbreviatePathsChB.configure(state=tkinter.NORMAL if v else tkinter.DISABLED)




###################
## Edge controls ##
###################

class EdgeControls(tkinter.Frame):

	def __init__(self, parent, app):
		tkinter.Frame.__init__(self, parent, borderwidth=borderwidth, relief=tkinter.GROOVE)
		self.parent = parent
		self.app = app

		self.headerL = tkinter.Label(self, text="Edges", font="TkHeadingFont")
		
		self.edgeEntry = None
		self.edgeL = tkinter.Label(self, text="Value:")

		self.headerL.grid(row=0,column=0)
		self.edgeL.grid(row=1,column=0,sticky="W", pady=5)

	def algebraChanged(self, A):
		if self.edgeEntry:
			self.edgeEntry.grid_forget()
		self.edgeEntry = EdgeEntry(self, self, A)
		self.edgeEntry.grid(row=1,column=1, sticky="NESW", pady=5)
		self.edgeEntry.setState(state=tkinter.DISABLED)
		self.A = A

	def edgeSelected(self, v):
		self.edgeEntry.setState(tkinter.NORMAL)
		self.edgeEntry.setValue(v)
		self.edgeEntry.focus()

	def edgeDeselected(self):
		self.edgeEntry.setState(tkinter.DISABLED)
		self.edgeEntry.setValue("")

	def edgeValueChanged(self, a, b, c):
		v = self.edgeEntry.getValue()
		if self.A.validate(v):
			self.app.setSelectedEdgeValue(v)
		
class EdgeEntry(tkinter.Frame):

	def __init__(self, parent, edgeControls, A):
		tkinter.Frame.__init__(self, parent, borderwidth=0)

		self.edgeControls = edgeControls
		self.subEntries = []
		self.A = A

		if A.components:
			for i, childA in enumerate(A.components):
				child = EdgeEntry(self, self.edgeControls, childA)
				child.grid(row=0,column=i)
				self.subEntries.append(child)
		else:
			self.value = tkinter.StringVar()
			self.value.trace("w", self.edgeControls.edgeValueChanged)

			self.entry = tkinter.Entry(self, textvariable=self.value, width=5)
			self.entry.grid(row=0, column=0)

	def getValue(self):
		if self.subEntries:
			return [se.getValue() for se in self.subEntries]
		else:
			v = self.value.get()
			if self.A.validate(v):
				self.entry.configure(bg="#FFFFFF")
				return self.A.parse(v)
			else:
				self.entry.configure(bg="#FFAAAA")
				return None

	def setValue(self, v):
		if self.subEntries:
			for x, se in zip(v, self.subEntries):
				se.setValue(x)
		else:
			self.value.set(v)

	def setState(self, state):
		if self.subEntries:
			for se in self.subEntries:
				se.setState(state)
		else:
			self.entry.configure(state=state)


	def focus(self):
		if self.subEntries:
			self.subEntries[0].focus()
		else:
			self.entry.focus_set()
			self.entry.selection_range(0, tkinter.END)




###################
## Save controls ##
###################

class SaveControls(tkinter.Frame):

	def __init__(self, parent, app):
		tkinter.Frame.__init__(self, parent, borderwidth=borderwidth, relief=tkinter.GROOVE)

		self.loadB = tkinter.Button(self, text="Load graph", command=app.load)
		self.saveB = tkinter.Button(self, text="Save graph", command=app.save)

		self.loadB.grid(row=0, column=0, sticky="EW", padx=8, pady=5)
		self.saveB.grid(row=0, column=1, sticky="EW", padx=8, pady=5)



#####################
## Search controls ##
#####################

class SearchControls(tkinter.Frame):

	def __init__(self, parent, app):
		tkinter.Frame.__init__(self, parent, borderwidth=borderwidth, relief=tkinter.GROOVE)
		self.app = app

		self.headerL = tkinter.Label(self, text="Search for non-linear examples", font="TkHeadingFont")

		self.iterationsL = tkinter.Label(self, text="Iterations:", anchor="e")
		self.iterationsE = tkinter.Entry(self, width=10)
		self.iterationsE.insert(0, 1000)

		self.sizeL = tkinter.Label(self, text="Size:")
		self.sizeE = tkinter.Entry(self, width=10)
		self.sizeE.insert(0, 5)

		self.progressL = tkinter.Label(self, text="Results:")
		self.progressDL = tkinter.Label(self, justify=tkinter.LEFT)

		self.searchB = tkinter.Button(self, text="Start searching", width=15, command=self.startSearch)

		self.headerL.grid(row=0,column=0,columnspan=2,sticky="W")
		self.iterationsL.grid(row=1,column=0,sticky="W", pady=(5,2.5))
		self.iterationsE.grid(row=1,column=1,sticky="EW", pady=(5,2.5))
		self.sizeL.grid(row=2,column=0,sticky="W",pady=(2.5,2.5))
		self.sizeE.grid(row=2,column=1,sticky="EW",pady=(2.5,2.5))
		self.progressL.grid(row=3,column=0,sticky="W",pady=(2.5,2.5))
		self.progressDL.grid(row=3,column=1,sticky="EW",pady=(2.5,2.5))
		self.searchB.grid(row=4,column=0,columnspan=2,pady=(2.5,5))


	def startSearch(self):
		self.iterationsE.configure(state=tkinter.DISABLED)
		self.sizeE.configure(state=tkinter.DISABLED)
		#self.progressDL.configure(text="")
		self.searchB.configure(text="Stop searching", command=self.app.endSearch)

		iterations = int(self.iterationsE.get())
		size = int(self.sizeE.get())
		self.app.startSearch(iterations, size)

	def searchUpdate(self, iterations, bestSoFar):
		progress = str(100*iterations/int(self.iterationsE.get()))
		progressStr = str(bestSoFar) + " rounds (" + progress + "%)"
		self.progressDL.configure(text=progressStr)

	def searchEnded(self):
		self.iterationsE.configure(state=tkinter.NORMAL)
		self.sizeE.configure(state=tkinter.NORMAL)
		self.searchB.configure(text="Start searching", command=self.startSearch)