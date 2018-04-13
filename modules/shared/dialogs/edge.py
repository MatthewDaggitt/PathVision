import tkinter
from modules.shared.dialogs.base import BasicDialog


class EdgeDialog(BasicDialog):
    
    def __init__(self, parent, algebra, currentValue, title=None):
    	self._algebra      = algebra
    	self._currentValue = currentValue
    	super().__init__(parent,title)

    def body(self, master):

        self.l = tkinter.Label(master, text="Edge value: ")
        self.e = EdgeEntry(master, self._algebra, self.apply)
        self.e.setValue(self._currentValue)

        self.l.grid(row=0, column=0)
        self.e.grid(row=0, column=1)
        return self.e

    def apply(self):
        self.result = self.e.getValue()

    def validate(self):
    	return self.e.validate()


class EdgeEntry(tkinter.Frame):

	def __init__(self, parent, algebra, onEnterCallback):
		tkinter.Frame.__init__(self, parent, borderwidth=0)

		self.subEntries = []
		self.algebra = algebra

		if algebra.componentAlgebras:
			for i, childAlgebra in enumerate(algebra.componentAlgebras):
				child = EdgeEntry(self, childAlgebra, onEnterCallback)
				child.grid(row=0,column=i)
				self.subEntries.append(child)
		else:
			self.value = tkinter.StringVar()

			self.entry = tkinter.Entry(self, textvariable=self.value, width=5)
			self.entry.grid(row=0, column=0)
			self.entry.bind("<Return>", lambda e: onEnterCallback())

	def validate(self):
		if self.subEntries:
			valid = True
			for entry in self.subEntries:
				valid &= entry.validate()
			return valid
		else:
			v = self.value.get()
			if self.algebra.validateEdgeString(v):
				self.entry.configure(bg="#FFFFFF")
				return True
			else:
				self.entry.configure(bg="#FFAAAA")
				return False

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
				return self.algebra.parseEdgeString(v)
			else:
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