import math
import random
import threading
import tkinter
import time
import sys

import networkx as nx

from settings import *

from modes.explorationMode import ExplorationMode
from modes.simulationMode import SimulationMode

class App(tkinter.Frame):

	def __init__(self):
		tkinter.Frame.__init__(self)

		# Setup the master frame
		self.master.title("PathVision")
		self.grid(row=0,column=0,sticky="NESW",padx=OUT_PADDING,pady=OUT_PADDING)
		self.master.rowconfigure(0,weight=1)
		self.master.columnconfigure(0,weight=1)
		self.setup_themes()
		self.setup_menubar()

		self.simulationMode = SimulationMode(self, self)
		self.explorationMode = ExplorationMode(self, self)

		# Setup window events
		self.master.protocol("WM_DELETE_WINDOW", self.on_close)
		self.bind("<Configure>", self.on_resize)
		self.rowconfigure(0,weight=1)
		self.columnconfigure(0,weight=1)

		self.activate_simulation()
		self.simulationMode.storageController._load("examples/quadratic.pv")
		#self.explorationMode.storageController._load("test.alg")
		
		tkinter.mainloop()


	def setup_themes(self):
		# Choose ttk themes
		for theme in ["aqua","vista","xpnative","clam"]:
			if theme in tkinter.ttk.Style().theme_names():
				tkinter.ttk.Style().theme_use(theme)
				break

	def setup_menubar(self):
		self._menubar = tkinter.Menu(self)

		fileMenu = tkinter.Menu(self._menubar, tearoff=False)
		fileMenu.add_command(label="Quit", command=self.on_close)
		self._menubar.add_cascade(label="File", menu=fileMenu)

		modeMenu = tkinter.Menu(self._menubar, tearoff=False)
		modeMenu.add_radiobutton(label="Simulate", command=self.activate_simulation)
		modeMenu.add_radiobutton(label="Explore", command=self.activate_exploration)
		self._menubar.add_cascade(label="Mode", menu=modeMenu)

		helpMenu = tkinter.Menu(self._menubar, tearoff=False)
		self._menubar.add_cascade(label="Help", menu=helpMenu)

		self.master.config(menu=self._menubar)


	################
	## App events ##
	################

	def activate_simulation(self):
		self.explorationMode.grid_remove()
		self.simulationMode.grid(row=0, column=0, sticky="NESW")

		self.simulationMode.activate()
		self.currentMode = self.simulationMode

	def activate_exploration(self):
		self.simulationMode.grid_remove()
		self.explorationMode.grid(row=0, column=0, sticky="NESW")

		self.explorationMode.activate()
		self.currentMode = self.explorationMode
		
	###################
	## Window events ##
	###################

	def on_resize(self, e):
		# Needed because sometimes in multiple resizes
		# draw gets called before the window resize is complete...
		def worker():
			time.sleep(0.01)
			self.simulationMode.draw()

		threading.Thread(target=worker).start()

	def on_close(self):
		self.destroy()
		quit()

if __name__ == '__main__':
	App()


"""

"""

"""
def displayHelp(self):
	window = tkinter.Toplevel(self)
	window.wm_title("PathVision help")
	helpText = HelpText(window)
	helpText.pack(side="top", fill="both", expand=True, padx=5, pady=5)
"""

"""
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
		controlStr += "Change destination: double left click on new destination node\n\n"
		controlStr += "Toggle node label: middle click on node"

		self.insert(tkinter.INSERT, controlStr)
		self.configure(state=tkinter.DISABLED)
"""