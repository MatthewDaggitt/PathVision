import tkinter

from theory.displayAlgebra import examples

class Controls(tkinter.Frame):

	def __init__(self, parent):
		tkinter.Frame.__init__(self, parent)
		self.parent = parent
		
		padding = 10

		self._algebraControls = AlgebraControls(self)
		self._algebraControls.grid(row=0, column=0, sticky="EW", pady=padding)

		self._edgeControls = EdgeControls(self)
		self._edgeControls.grid(row=1, column=0, sticky="EW", pady=padding)

		self._informationControls = InformationControls(self)
		self._informationControls.grid(row=2, column=0, sticky="", pady=padding)

		self._saveControls = SaveControls(self)
		self._saveControls.grid(row=3, column=0, sticky="EW", pady=padding)


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


	# Up

	def setAlgebra(self, A):
		self.parent.setAlgebra(A, True)

	def setWithPaths(self, v):
		self.parent.setWithPaths(v)

	def setSelectedEdgeValue(self, v):
		self.parent.setSelectedEdgeValue(v)

	def load(self):
		self.parent.load()

	def save(self):
		self.parent.save()




######################
## Algebra controls ##
######################


class AlgebraControls(tkinter.ttk.LabelFrame):

	def __init__(self, parent):
		tkinter.ttk.LabelFrame.__init__(self, parent, text="Algebra", borderwidth=5)

		self.parent = parent

		self.algebraV = tkinter.StringVar()
		self.algebraCB = tkinter.ttk.Combobox(
			self, 
			textvariable=self.algebraV, 
			values=[a.name for a in examples]
		)
		self.algebraCB.grid(row=0,column=0)
		self.algebraCB.current(0)
		self.algebraV.tid = self.algebraV.trace("w", self.setAlgebra)


		self.withPathsV = tkinter.IntVar()
		self.withPathsChB = tkinter.Checkbutton(self, text="With paths", variable=self.withPathsV)
		self.withPathsChB.grid(row=1,column=0)
		self.withPathsV.tid = self.withPathsV.trace("w", self.setWithPaths)

	def setAlgebra(self, a, b, c):
		v = self.algebraV.get()
		for A in examples:
			if A.name == v:
				self.parent.setAlgebra(A)

	def setWithPaths(self, a, b, c):
		self.parent.setWithPaths(bool(self.withPathsV.get()))

	def algebraChanged(self, A):
		self.algebraV.trace_vdelete("w", self.algebraV.tid)
		self.algebraV.set(A.name)
		self.algebraV.tid = self.algebraV.trace("w", self.setAlgebra)

	def withPathsChanged(self, v):
		self.withPathsV.trace_vdelete("w", self.withPathsV.tid)
		self.withPathsV.set(v)
		self.withPathsV.tid = self.withPathsV.trace("w", self.setWithPaths)




###################
## Edge controls ##
###################

class EdgeControls(tkinter.ttk.LabelFrame):

	def __init__(self, parent):
		tkinter.ttk.LabelFrame.__init__(self, parent, text="Edge", borderwidth=5)
		self.parent = parent
		self.edgeEntry = None

	def algebraChanged(self, A):
		if self.edgeEntry:
			self.edgeEntry.grid_forget()
		self.edgeEntry = EdgeEntry(self, self, A)
		self.edgeEntry.grid(row=0,column=0, sticky="NESW")
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
			self.parent.setSelectedEdgeValue(v)
		
class EdgeEntry(tkinter.ttk.LabelFrame):

	def __init__(self, parent, edgeControls, A):
		tkinter.ttk.LabelFrame.__init__(self, parent, borderwidth=0)

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

class SaveControls(tkinter.ttk.Frame):

	def __init__(self, parent):
		tkinter.ttk.Frame.__init__(self, parent)
		self.parent = parent

		self.loadB = tkinter.Button(self, text="Load graph", command=self.load)
		self.loadB.grid(row=0, column=0)

		self.saveB = tkinter.Button(self, text="Save graph", command=self.save)
		self.saveB.grid(row=0, column=1)

	def load(self):
		self.parent.load()

	def save(self):
		self.parent.save()




##########################
## Information controls ##
##########################

class InformationControls(tkinter.ttk.LabelFrame):

	def __init__(self, parent):
		tkinter.ttk.LabelFrame.__init__(self, parent, text="Controls", borderwidth=0)


		controlStr = "Add node: left click on empty space\n\n"
		controlStr += "Remove node: right click on node\n\n"
		controlStr += "Add edge: left click on source followed by the destination\n\n"
		controlStr += "Remove edge: right click on edge\n\n"
		controlStr += "Change edge value: left click on edge and type\n\n"
		controlStr += "Change destination: double left click on new destination node"


		self.text = tkinter.Text(self, width=30, bg="#ddd", wrap=tkinter.WORD)
		self.text.grid(row=0, column=0)
		self.text.insert(tkinter.INSERT, controlStr)
		self.text.configure(state=tkinter.DISABLED)