
import tkinter
from tkinter import ttk

class NavigationControls(tkinter.Frame):

	def __init__(self, parent, app):
		tkinter.Frame.__init__(self, parent)
		self.app = app

		self.loadB = tkinter.Button(self, text="Load graph", command=app.load)

		self.startB = tkinter.Button(self, text="<<", command=app.moveToStart)
		self.startB.configure(state=tkinter.DISABLED)

		self.backB = tkinter.Button(self, text="<", command=app.moveBack)
		self.backB.configure(state=tkinter.DISABLED)

		self.calculateB = tkinter.Button(self, width=5)
		
		self.forwardsB = tkinter.Button(self, text=">", command=app.moveForwards)
		self.forwardsB.configure(state=tkinter.DISABLED)

		self.endB = tkinter.Button(self, text=">>", command=app.moveToEnd)
		self.endB.configure(state=tkinter.DISABLED)

		self.saveB = tkinter.Button(self, text="Save graph", command=app.save)


		self.loadB.grid(row=0, column=0, padx=8, pady=5)
		self.startB.grid(row=0,column=1)
		self.backB.grid(row=0,column=2)
		self.calculateB.grid(row=0,column=3)
		self.forwardsB.grid(row=0,column=4)
		self.endB.grid(row=0,column=5)
		self.saveB.grid(row=0, column=6, padx=8, pady=5)

		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(6, weight=1)


	def startedCalculating(self):
		self.calculateB.configure(text="Stop", command=self.app.stopCalculating)


	def stoppedCalculating(self):
		self.calculateB.configure(text="Start", command=self.app.startCalculating)

		self.startB.configure(state=tkinter.DISABLED)
		self.backB.configure(state=tkinter.DISABLED)
		self.forwardsB.configure(state=tkinter.DISABLED)
		self.endB.configure(state=tkinter.DISABLED)


	def timeChanged(self, t, canProceed, canProceedToEnd):

		bState = tkinter.ACTIVE if t else tkinter.DISABLED
		fState = tkinter.ACTIVE if canProceed else tkinter.DISABLED
		eState = tkinter.ACTIVE if canProceedToEnd else tkinter.DISABLED

		title = "t = " + str(t)
		if not canProceed:
			title += " (CONVERGED)"

		self.startB.configure(state=bState)
		self.backB.configure(state=bState)
		self.forwardsB.configure(state=fState)
		self.endB.configure(state=eState)