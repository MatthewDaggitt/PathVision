import pickle
import tkinter

import settings

################
## Controller ##
################

class RoutingProblemStorageController():

	###########
	## Setup
		
	def __init__(self,mode,parent):
		self._view = RoutingProblemStorageView(self, parent)
		self._mode = mode

	############
	## Actions

	def save(self):
		filename = tkinter.filedialog.asksaveasfilename()
		if filename:
			self._save(filename)
			
	def _save(self, filename):
		file = open(filename, 'wb')
		data = self._mode.saveRoutingProblem()
		pickle.dump(data, file)


	def load(self):
		filename = tkinter.filedialog.askopenfilename()
		if filename:
			self._load(filename)

	def _load(self, filename):
		data = pickle.load(open(filename, 'rb'))
		self._mode.loadRoutingProblem(data)

##########
## View ##
##########

class RoutingProblemStorageView(tkinter.Frame):
	
	def __init__(self, controller, parent, *args, **kwargs):
		tkinter.Frame.__init__(self, parent, *args, **kwargs, borderwidth=settings.BORDER_WIDTH, relief=tkinter.GROOVE)
		self.controller = controller

		self.headerL = tkinter.Label(self, text="Storage", font="TkHeadingFont")

		self.loadIcon=tkinter.PhotoImage(file="images/load.gif")
		self.loadIcon = self.loadIcon.subsample(2)
		self.loadB = tkinter.Button(self, compound=tkinter.LEFT, image=self.loadIcon, text="Load routing problem", command=controller.load)
		
		self.saveIcon=tkinter.PhotoImage(file="images/save.gif")
		self.saveIcon = self.saveIcon.subsample(2)
		self.saveB = tkinter.Button(self, compound=tkinter.LEFT, image=self.saveIcon, text="Save routing problem", command=controller.save)

		self.headerL.grid(	row=0,column=0,sticky="W")
		self.loadB.grid(	row=1,column=0,sticky="",padx=5,pady=5)
		self.saveB.grid(	row=2,column=0,sticky="",padx=5,pady=5)
		self.grid_columnconfigure(0, weight=1)