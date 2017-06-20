"""
Started 27/10/16

@author: FRS
"""
import Tkinter as tk
from Tkinter import Label, Frame, Button, Menu, Canvas, Scrollbar
from Tkconstants import LEFT, EW, NE, NSEW, GROOVE, NW, DISABLED, BOTH, NORMAL, Y
from datetime import datetime as dt
from Queue import Queue
from threading import Thread
from time import sleep
from _elementtree import fromstring

def transmit():
    global counter
        
    dataset = ('<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.001" x="-0.000" dT="27" y="-0.001"/><Timestamp Time= "1497850542376"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.000" x="0.001" dT="32" y="-0.002"/><Timestamp Time= "1497850542876"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.000" x="0.000" dT="27" y="-0.001"/><Timestamp Time= "1497850543376"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="0.001" x="0.000" dT="32" y="-0.001"/><Timestamp Time= "1497850543876"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="0.000" x="0.001" dT="29" y="-0.002"/><Timestamp Time= "1497850544376"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.000" x="-0.001" dT="31" y="-0.001"/><Timestamp Time= "1497850544876"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="0.000" x="-0.000" dT="32" y="-0.001"/><Timestamp Time= "1497850545375"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.001" x="-0.001" dT="32" y="-0.001"/><Timestamp Time= "1497850545876"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.001" x="-0.000" dT="30" y="-0.002"/><Timestamp Time= "1497850546375"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.001" x="0.000" dT="31" y="-0.001"/><Timestamp Time= "1497850546875"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.001" x="-0.001" dT="32" y="-0.000"/><Timestamp Time= "1497850547375"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.001" x="-0.000" dT="30" y="0.000"/><Timestamp Time= "1497850547875"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.000" x="0.000" dT="32" y="-0.001"/><Timestamp Time= "1497850548375"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.001" x="-0.000" dT="32" y="-0.001"/><Timestamp Time= "1497850548876"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.001" x="-0.000" dT="32" y="-0.001"/><Timestamp Time= "1497850549376"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.000" x="-0.001" dT="32" y="-0.001"/><Timestamp Time= "1497850549875"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.002" x="-0.001" dT="31" y="-0.001"/><Timestamp Time= "1497850550375"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="0.001" x="0.000" dT="31" y="-0.001"/><Timestamp Time= "1497850550876"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="0.000" x="0.000" dT="33" y="-0.002"/><Timestamp Time= "1497850551376"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.000" x="0.000" dT="31" y="-0.001"/><Timestamp Time= "1497850551876"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="0.001" x="0.001" dT="30" y="-0.002"/><Timestamp Time= "1497850552375"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.001" x="-0.003" dT="31" y="-0.000"/><Timestamp Time= "1497850552876"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.001" x="-0.001" dT="33" y="-0.001"/><Timestamp Time= "1497850553375"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="0.001" x="0.000" dT="29" y="-0.000"/><Timestamp Time= "1497850553876"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="0.001" x="-0.000" dT="32" y="-0.001"/><Timestamp Time= "1497850554375"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="0.001" x="0.001" dT="32" y="-0.001"/><Timestamp Time= "1497850554876"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.000" x="-0.001" dT="30" y="0.000"/><Timestamp Time= "1497850555376"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.001" x="-0.001" dT="30" y="0.000"/><Timestamp Time= "1497850555876"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="0.001" x="-0.000" dT="32" y="-0.001"/><Timestamp Time= "1497850556375"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="0.000" x="-0.001" dT="32" y="-0.001"/><Timestamp Time= "1497850556876"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="0.000" x="-0.002" dT="31" y="-0.001"/><Timestamp Time= "1497850557376"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="0.001" x="-0.001" dT="31" y="-0.001"/><Timestamp Time= "1497850557875"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.001" x="-0.003" dT="31" y="-0.000"/><Timestamp Time= "1497850558376"/></Node>',
            '<?xml version="1.0" encoding="utf-8"?><Node Name="Node1"><Sensor Type="Gyroscope" z="-0.000" x="-0.001" dT="32" y="-0.001"/><Timestamp Time= "1497850558876"/></Node>')

    if counter < len(dataset):
        
        return dataset[counter], "0.0.0.0"
    else:
        return False,False

class Client:
    """
    Launch the main part of the GUI and the IOthread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
     puts all the thread controls in a single place.
    """
    
    def __init__(self, master):
        """
        Start the GUI and asynchronous threads.
        Main thread of the application.
        Later used by GUI.
        Spawn a new thread for the worker.
        """
        self.master = master
                
        # Set up the GUI part
        self.gui = UI(master, self.endApp)

        # Set up the thread to do asynchronous I/O (simulated here)
        self.running = True
        self.thread1 = Thread(target=self.IOThread)
        self.thread1.setDaemon(1)
        self.thread1.start()

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()

    def periodicCall(self):
        """
        Check every 40 ms if there is something new in the queue. Timing based on node Tx cycle. Tune with field trials
        """
        if not self.running:
            # Cleanup in EndApp
            self.master.destroy()

        self.gui.processQueue()
        self.master.after(40, self.periodicCall)                                #:TODO Timing variable to config

    def IOThread(self):
        """
        Simulate asynchronous I/O.
        The thread has to yield control.
        """
        global myQueues
        global counter

        while self.running:
            sleep(1)                                                            #:TODO: Tune later
            message, address = transmit()
            if message:
                counter += 1
                msgStr = message
                nodeID = fromstring(message).attrib.get("Name")
                if nodeID in self.gui.nodeButtons.keys():                       #Is this one of our nodes?  TODO: ID encryption to prevent node spoofing
                    if address not in myQueues:                                 #node ip address is unknown
                        myQueues[address] = Queue()                             #add the address and a queue for it to the queue dict
                    myQueues[address].put(msgStr)
                else:
                    pass                                                        #not one of our nodes. Do nothing with it. TODO: Flag for node spoofing?

    def endApp(self):
        """    db elements removed. Working. Not relevant to question"""
        self.running = False

class UI(object):
    def __init__(self, root, endCommand):
        """ initialise UI
        :param root: Tk.tk instance
        :param endCommand: protocol handler for close [x] / Quit
        """        
        root.title("Sensor Hub")
        root.geometry("+%d+%d" % (100, 100))                                    #:TODO:    To config
        menubar = Menu(root)
        filemenu = Menu(menubar, tearoff = False)
        menubar.add_cascade(label = "File", menu = filemenu)
        filemenu.add_command(label = "Quit", command = endCommand)
        root.config(menu = menubar)

        guiFrame = Frame(root,borderwidth=5,relief = GROOVE)
        guiFrame.pack(expand = True, fill = BOTH)

        btnFrame = Frame(guiFrame)
        btnFrame.pack()
               
        self.nodeButtons = {}       #dict of node buttons Key: nodeID , Value: instance of button
        self.nodeWindows = {}       #dict of node windows Key: nodeID , Value: instance of frame

        #Only one node for purpose of question
        b = Button(btnFrame, state = DISABLED, text = "Node1", width = 6, height = 2)
        b.grid(row=0, column=0)
        self.nodeButtons["Node1"] = b
        self.nodeWindows["Node1"] = Frame(guiFrame,borderwidth=2,relief = GROOVE, bg="black")

    def createNode(self,node):
        """Activate button to signal node active and enable display of incoming data
             Create instance of sNode object
        :param node: tuple (IPv4 address, nodeID, initial message) strings
        """
        global nodes
        
        btxt = node[1]+"\n"+node[0]
        self.nodeButtons[node[1]].config(state = NORMAL)
        nodes[node[0]] = sNode(self.nodeWindows[node[1]],node,self.nodeButtons[node[1]])
        self.nodeButtons[node[1]].config(command = nodes[node[0]].show)
        self.nodeButtons[node[1]].config(text = btxt, width = len(node[0]))

    def processQueue(self):
        """
        Handle all the messages currently in the sensor queues (if any).
        """
        global nodes
        global myQueues
        
        for nAddr, localq in myQueues.items():
            while (localq.qsize()):
                try:
                    msg = localq.get(0)
                except localq.Empty:
                    pass
                except Exception as e:
                    print "Unexpected error:", e
                else:
                    if nAddr not in nodes:                                                          #this address does not have a node object
                        nodeID = fromstring(msg).attrib.get("Name")                              #get the Node ID
                        self.createNode((nAddr,nodeID,msg))                                         #activate button for this node, create instance of sNode
                    nodes[nAddr].appendData(msg)                                                    #extract and append timestamp and Sensor values
 
class sNode():
    """ Sensor Node object """
    def __init__(self,parent,node,nBtn):
        """ initialise Node
        :param node: tuple (IPv4 address, nodeID, initial message) strings
        :param parent: handle of containing tk.Frame
        """
        self.initElements = fromstring(node[2])
        self.ID = node[1]
        self.ownWindow = parent
        self.btn = nBtn
        self.sensFieldValues = {}       #dict of sensor data fields. Key: Field Name, Value: tk.Label handle. Populated by build().
        self.sensFieldNames = {}        #dict of sensor data labels. Key: Field Name, Value: tk.Label handle. Populated by build(). Used to keep label width aligned with field width
        self.sensors = {}               #Populated by build() from first message for each node.{Type,[v1 ... vn]} (display order -> TODO. For now alpha sort) Excludes Timestamp
        self.display = False
        self.build()
        print node[0]+ " NodeId " + node[1] + " is up"

    def build(self):
        self.setSensors()
        """    db elements removed. Working. Not relevant to question"""
        """background colours added to frames/canvas to assist visualisation of layout"""
        
        self.headerFrame = Frame(self.ownWindow,bg = "yellow")
        self.headerFrame.grid(row = 0, column = 0, sticky = NSEW)

        self.dispPort = Canvas(self.ownWindow, bg = "bisque")
        self.dispPort.grid(row = 1, column = 0, sticky = NSEW)

        self.dispFrame = Frame(self.dispPort, bg = "green",pady = 2)
        self.dispFrameID = self.dispPort.create_window(0,0, window = self.dispFrame, anchor = NW)
        
        
        var_scroll = Scrollbar(self.ownWindow, orient = "vertical", command = self.dispPort.yview)
        var_scroll.grid(row = 1, column = 1, sticky = NSEW)
        
        self.dispPort.config(yscrollcommand = var_scroll.set)

        nodeTitle = Label(self.headerFrame, text = self.ID)
        nodeTitle.grid(row=0,column=0, sticky=EW, columnspan = self.sensCols()+1)
        
        sTitle = "Time"
        self.sensFieldNames[sTitle] = Label(self.headerFrame,text = sTitle, bg = "magenta")
        self.sensFieldNames[sTitle].grid(row = 1, column = 0, sticky = EW, rowspan = 2)
        self.headerFrame.columnconfigure(0, weight = 1)

        self.sensFieldValues[sTitle] = Label(self.dispFrame, bg ="blue", fg = "white",text ="", anchor = NE)
        self.sensFieldValues[sTitle].grid(row = 0, column = 0, sticky = EW)
        self.dispFrame.columnconfigure(0, weight = 1)

        colndx = 1
        """
        :TODO    Arrange Sensors in desired order as order in XML indeterminate
        """ 
        for sensor in self.sensors.keys():
            sTitle = sensor
            sLbl = Label(self.headerFrame, text = sTitle, bg="orange")
            sLbl.grid(row = 1, column = colndx, sticky = EW, columnspan = len(self.sensors.get(sensor)))
            self.headerFrame.columnconfigure(colndx, weight = 1)

            for ctr in xrange(0,len(self.sensors.get(sTitle))):
                instName = sTitle + self.sensors.get(sTitle)[ctr]
                self.sensFieldNames[instName] = Label(self.headerFrame,text = self.sensors.get(sTitle)[ctr], bg = "magenta")
                self.sensFieldNames[instName].grid(row = 2, column = colndx+ctr, sticky = EW)
                self.headerFrame.columnconfigure(colndx+ctr, weight = 1)
                
                self.sensFieldValues[instName] = Label(self.dispFrame, bg ="blue", fg = "white", text ="", anchor = NE)
                self.sensFieldValues[instName].grid(row = 0, column = colndx+ctr, sticky = EW)
                self.dispFrame.columnconfigure(colndx+ctr, weight = 1)

            colndx += len(self.sensors.get(sTitle))
            """    db code removed. Working. Not relevant to question"""

        self.dispFrame.bind("<Configure>", self.OnFrameConfigure)
        self.dispPort.bind("<Configure>", self.FrameHeight)

    def FrameHeight(self, event):
        print event.height, event.width
        canvas_height = event.height
        self.dispPort.itemconfig(self.dispFrameID, height = canvas_height)

    def OnFrameConfigure(self, event):
        self.dispPort.configure(scrollregion=self.dispPort.bbox("all"))

    def appendData(self,msg):
        xmlElements =  fromstring(msg)
        ts = xmlElements.find("Timestamp").attrib.get("Time")
        fieldVal = dt.fromtimestamp(float(ts)/1000).strftime("%m %d %H:%M:%S.%f")[:-3]
        
        temp = fieldVal + "\n" + self.sensFieldValues["Time"].cget("text")
        
        self.sensFieldValues["Time"].config(text = temp, width = len(fieldVal)-3)       #Size headers and columns to fit data. TODO: move to build. Timestamp width constant. 
        self.sensFieldNames["Time"].config(width = len(fieldVal)-3)
        for sensor in xmlElements.findall("Sensor"):
            """    db code removed. Working. Not relevant to question"""
            name = sensor.get("Type")
            for key in sensor.keys():
                if key != "Type":
                    fieldVal = sensor.get(key)
                    if (key == "dT"):                                                   #Always integer
                        fv = fieldVal
                    else:
                        fv = "{:.3f}".format(float(fieldVal))
                    self.sensFieldValues[name+key].config(text = fv+"\n"+self.sensFieldValues[name+key].cget("text"))
                    if len(fv) > self.sensFieldValues[name+key].cget("width"):          #Size headers and columns to fit data
                        self.sensFieldValues[name+key].config(width = len(fv))
                        self.sensFieldNames[name+key].config(width = len(fv))
            """    db code removed. Working. Not relevant to question"""
    
    def sensCols(self):
        n= 0
        for item in self.sensors.keys():
            n += len(self.sensors.get(item))
        return n

    def show(self):
        self.display = True
        self.ownWindow.pack(fill = BOTH, expand=True)
        self.btn.config(command = self.hide)

    def hide(self):
        self.display = False
        self.ownWindow.pack_forget()
        self.btn.config(command = self.show)

    def setSensors(self):
        for sensor in self.initElements.findall("Sensor"):
                varList = []
                for entry in sorted(sensor.keys()):
                    if entry != "Type":
                        varList.append(entry)
                    self.sensors[sensor.get("Type")] = varList
    
    def endApp(self):
        """    db code removed. Working. Not relevant to question"""
        self.master.destroy()

if __name__ == "__main__":
    global nodes
    global myQueues
    global counter
    
    nodes = {}
    myQueues = {}
    counter = 0
    
    root = tk.Tk()
    client = Client(root)
    root.protocol("WM_DELETE_WINDOW",client.endApp)
    root.mainloop()
    print "Cheese?"                                                                   #Clean exit
    
    
    
    