import tkinter
import threading
import time

import settings
from modules.pathDisplayModule import PathDisplayController
from modules.graphModule import GraphController
from modules.choiceModule import ChoiceController
from modules.storageModule import StorageController
from modules.orderSearchModule import OrderSearchController

padding = 10

class ExplorationMode(tkinter.Frame):

	def __init__(self, parent, app):
		tkinter.Frame.__init__(self)
		self.app = app


		leftFrame = tkinter.Frame(self)
		label = tkinter.Label(leftFrame, text="Exploration mode", font=settings.TITLE_FONT)
		self.orderSearchController  = OrderSearchController(self, leftFrame)
		#self.graphSearchController = GraphSearchController(self, leftFrame)
		self.storageController 		= StorageController(leftFrame, self.getSaveData, self.loadData, "toplogy")

		label.grid(row=0,column=0, sticky="NW", pady=padding)
		self.orderSearchController._view.grid(row=1,column=0,sticky="NESW",pady=padding)
		#self.graphSearchController._view.grid(row=2, column=0, sticky="NESW",pady=padding)
		self.storageController._view.grid(row=2, column=0, sticky="NESW",pady=padding)

		self.pathDisplayController = PathDisplayController(self,self)
		self.choiceController = ChoiceController(self,self)

		leftFrame.grid(row=0, column=0, rowspan=2, sticky="NESW", padx=padding, pady=(0,padding))
		self.pathDisplayController._view.grid(row=0,column=1,sticky="NESW")
		self.choiceController._view.grid(row=0,column=2,sticky="NESW")

		self.rowconfigure(0,weight=1)
		self.columnconfigure(1,weight=1)
		self.columnconfigure(2,weight=1)

		self.graphTopologyChanged()

	def activate(self):
		pass

	def deactivate(self):
		pass

	#############
	## Actions ##
	#############

	def graphTopologyChanged(self):
		self.pathDisplayController.graphTopologyChanged()
		self.choiceController.draw()
		self.pathDisplayController.draw()

	def partialOrderChanged(self):
		pass


	def loadData(self, data):
		self.choiceController.loadData(data)
		self.graphTopologyChanged()

	def getSaveData(self):
		return self.choiceController.getSaveData()