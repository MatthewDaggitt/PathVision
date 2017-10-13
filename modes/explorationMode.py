import math
import random
import pickle
import threading
import tkinter
import time

import networkx as nx

from settings import *

#from frames.exploration.generalControls import GeneralControls

class ExplorationMode(tkinter.Frame):

	def __init__(self, parent, app):
		tkinter.Frame.__init__(self)