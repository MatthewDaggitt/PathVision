import tkinter

class SizeDialog(BasicDialog):

    def __init__(self, parent):

        self.top = tkinter.Toplevel(parent)

        tkinter.Label(self.top, text="Value").pack()

        self.e = tkinter.Entry(self.top)
        self.e.pack(padx=5)

        b = tkinter.Button(self.top, text="OK", command=self.ok)
        b.pack(pady=5)

    def ok(self):

        print("value is", self.e.get())

        self.top.destroy()
