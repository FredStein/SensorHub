import Tkinter as tk
from Tkinter import IntVar, Label, Frame, Button, Radiobutton, LabelFrame, Spinbox, Menu, Listbox, Canvas
from ttk import Labelframe, Combobox, Treeview, Scrollbar
from PIL import Image, ImageTk      # Needs Pillow
from Tkconstants import LEFT, E, EW, NE, W, S, NSEW, GROOVE, RIGHT, NW, DISABLED, CENTER, RAISED, SUNKEN, BOTH, LAST, NORMAL, END
import threading
import Queue
from collections import OrderedDict

xLoc = ('A','M','F')
yLoc = ('P','S')
numNodes = len(xLoc)* len(yLoc)

nodes = {}
"""nodes: dict of nodes. Key: IPv4 address , Value: instance of sNode
"""
queues = {}
"""queues: dict of queues. Key: IPv4 address , Value: instance of queue
"""
