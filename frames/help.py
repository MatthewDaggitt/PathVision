import tkinter

class HelpText(tkinter.Text):

	def __init__(self, parent):
		tkinter.Text.__init__(self, parent, bg="#ddd", wrap=tkinter.WORD)

		controlStr = "Controls\n\n"
		controlStr += "Add node: left click on empty space\n\n"
		controlStr += "Remove node: right click on node\n\n"
		controlStr += "Add edge: left click on destination followed by the source\n\n"
		controlStr += "Remove edge: right click on edge\n\n"
		controlStr += "Change edge value: left click on edge and type\n\n"
		controlStr += "Change destination: double left click on new destination node"

		self.insert(tkinter.INSERT, controlStr)
		self.configure(state=tkinter.DISABLED)