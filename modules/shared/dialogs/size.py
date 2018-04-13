import tkinter
from modules.shared.dialogs.base import BasicDialog

class SizeDialog(BasicDialog):
    
    def body(self, master):

        self.l = tkinter.Label(master, text="Graph size: ")
        self.e = tkinter.Entry(master, width=5)

        self.l.grid(row=0, column=0)
        self.e.grid(row=0, column=1)
        return self.e

    def apply(self):
        size = int(self.e.get())
        self.result = size

    def validate(self):
    	try:
    		int(self.e.get())
    		return True
    	except Exception:
    		return False