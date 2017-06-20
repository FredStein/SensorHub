'''
Created on 27Nov.,2016

@author: Fred
'''
import __init__ as st
import sqlite3
from datetime import datetime as dt
import xml.etree.ElementTree as ET


class UI(object):
    def __init__(self, root, endCommand):
        """ initialise UI
        :param root: Tk.tk instance
        :param endCommand: protocol handler for close [x] / Quit
        """
        root.title('Sensor Hub')
        root.geometry('+%d+%d' % (100, 100))
        menubar = st.Menu(root)
        filemenu = st.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label = 'File', menu = filemenu)
        filemenu.add_command(label = 'Quit', command = endCommand)
        root.config(menu = menubar)

        guiFrame = st.Frame(root,borderwidth=5,relief = st.GROOVE)
        guiFrame.pack(expand = 1, fill = st.BOTH)

        btnFrame =st.Frame(guiFrame)
        btnFrame.pack()
               
        self.nodeButtons = {}       #dict of node buttons Key: nodeID , Value: instance of button
        self.nodeWindows = {}       #dict of node windows Key: nodeID , Value: instance of frame

        for w in st.xLoc:
            for h in st.yLoc:
                b = st.Button(btnFrame, state = st.DISABLED, text = w+h, width = 4, height = 2)
                b.grid(row=st.yLoc.index(h), column=st.xLoc.index(w))
                self.nodeButtons[w+h] = b
                self.nodeWindows[w+h] = st.Frame(guiFrame,borderwidth=2,relief = st.GROOVE, bg="black")

    def createNode(self,node):
        """Activate button to signal node active and enable display of incoming data
             Create instance of sNode object
        :param node: tuple (IPv4 address, nodeID, initial message) strings
        """
        print node[1]
        btxt = node[1]+'\n'+node[0]
        self.nodeButtons[node[1]].config(state = st.NORMAL)
        st.nodes[node[0]] = sNode(self.nodeWindows[node[1]],node,self.nodeButtons[node[1]])
        print len(st.nodes)
        print st.nodes.keys()
        self.nodeButtons[node[1]].config(command = st.nodes[node[0]].show)
        self.nodeButtons[node[1]].config(text = btxt, width = len(node[0])-3)

    def processIncoming(self):
        """
        Handle all the messages currently in the sensor queues (if any).
        """
        for nAddr, localq in st.queues.items():
            while (localq.qsize()):
                try:
                    msg = localq.get(0)
                except localq.Empty:
                    pass
                except Exception as e:
                    print "Unexpected error:", e
                else:
                    if nAddr not in st.nodes:                                                       #this address does not have a node object
                        nodeID = ET.fromstring(msg).attrib.get('Name')                              #get the Node ID
                        self.createNode((nAddr,nodeID,msg))                                         #activate button for this node, create instance of sNode
                    st.nodes[nAddr].appendData(msg)                                                 #extract and append timestamp and Sensor values
 

class sNode():
    """ Sensor Node object """
    def __init__(self,parent,node,nBtn):
        """ initialise Node
        :param node: tuple (IPv4 address, nodeID, initial message) strings
        :param parent: handle of containing tk.Frame
        :TODO parent could be some (any?) other object
        """
        self.initElements = ET.fromstring(node[2])
        self.ID = node[1]
        self.ownWindow = parent
        self.btn = nBtn
        self.sensFieldValues = {}       #dict of sensor data fields. Key: Field Name, Value: tk.Label handle. Populated by build().
        self.sensFieldNames = {}        #dict of sensor data labels. Key: Field Name, Value: tk.Label handle. Populated by build(). Used to keep label width aligned with field width
        self.sensors = {}               #Populated by build() from first message for each node.{Type,[v1 ... vn]} (sorted) Excludes Timestamp
        self.db = None                  #sqlite3 database connection object. Populated by build() with openDB()
        self.display = False
        self.build()
        print node[0]+ ' NodeId ' + node[1] + ' is up'

    def build(self):
        self.setSensors()
        dbFName = self.ID+'db.sqlite3'          #FileName  is NodeID(IP address) + 'db.sqlite3'
        self.openDB(dbFName)
        
        self.headerFrame = st.Frame(self.ownWindow,bg = 'yellow')
        self.headerFrame.grid(row = 0, column = 0, sticky = st.NSEW)                                   #Do not fill X here or header stretches to cover scrollbar (?)

        self.dispPort = st.Canvas(self.ownWindow, bg = 'bisque')
        self.dispPort.grid(row = 1, column = 0, sticky = st.NSEW)


        self.dispFrame = st.Frame(self.dispPort, bg = 'green',pady = 2)
        self.dispFrameID = self.dispPort.create_window(0,0, window = self.dispFrame, anchor = st.NW)
        
        
        var_scroll = st.Scrollbar(self.ownWindow, orient = "vertical", command = self.dispPort.yview)
        var_scroll.grid(row = 1, column = 1, sticky = st.NSEW)
        
        self.dispPort.config(yscrollcommand = var_scroll.set)

        
        nodeTitle = st.Label(self.headerFrame, text = self.ID)
        nodeTitle.grid(row=0,column=0, sticky=st.EW, columnspan = self.sensCols()+1)
        
        sTitle = "Time"
        self.sensFieldNames[sTitle] = st.Label(self.headerFrame,text = sTitle, bg = 'magenta')
        self.sensFieldNames[sTitle].grid(row = 1, column = 0, sticky = st.EW, rowspan = 2)
        
        self.sensFieldValues[sTitle] = st.Label(self.dispFrame, bg ='blue', fg = 'white',text ="", anchor = st.NE)
        self.sensFieldValues[sTitle].pack(side = st.LEFT, fill = st.Y, expand = 1)
#         self.dispFrame.columnconfigure(0, weight=1)
#         self.dispFrame.rowconfigure(0, weight=1)

        colndx = 1
        """
        :TODO:    Sort Sensors to desired order if not already
        """ 
        for sensor in self.sensors.keys():
            sTitle = sensor
            sLbl = st.Label(self.headerFrame, text = sTitle, bg='orange')
            sLbl.grid(row = 1, column = colndx, sticky = st.EW, columnspan = len(self.sensors.get(sensor)))
            self.headerFrame.columnconfigure(colndx, weight = 1)
            
            for ctr in xrange(0,len(self.sensors.get(sTitle))):
                instName = sTitle + self.sensors.get(sTitle)[ctr]
                self.sensFieldNames[instName] = st.Label(self.headerFrame,text = self.sensors.get(sTitle)[ctr], bg = 'magenta')
                self.sensFieldNames[instName].grid(row = 2, column = colndx+ctr, sticky = st.NSEW)
                self.headerFrame.columnconfigure(colndx+ctr, weight = 1)
                
                self.sensFieldValues[instName] = st.Label(self.dispFrame, bg ='blue', fg = 'white', text ='', anchor = st.NE)
                self.sensFieldValues[instName].pack(side = st.LEFT, fill = st.Y, expand = 1)

#                self.dispFrame.columnconfigure(colndx+ctr, weight=1)
                
            colndx += len(self.sensors.get(sTitle))
            self.createTable(self.db, sensor, self.sensors[sensor])

        self.dispFrame.bind("<Configure>", self.OnFrameConfigure)
        self.dispPort.bind('<Configure>', self.FrameHeight)

    def FrameHeight(self, event):
        print event.height, event.width
        canvas_height = event.height
        self.dispPort.itemconfig(self.dispFrameID, height = canvas_height)

    def OnFrameConfigure(self, event):
        self.dispPort.configure(scrollregion=self.dispPort.bbox('all'))

    def appendData(self,msg):
        xmlElements =  ET.fromstring(msg)
        ts = xmlElements.find("Timestamp").attrib.get("Time")
        fieldVal = dt.fromtimestamp(float(ts)/1000).strftime('%m %d %H:%M:%S.%f')[:-3]

        temp1 = self.sensFieldValues['Time'].cget('text')
        
        temp2 = fieldVal + '\n' + temp1
        
        self.sensFieldValues['Time'].config(text = temp2, width = len(fieldVal)-3)
        self.sensFieldNames['Time'].config(width = len(fieldVal)-3)
        for sensor in xmlElements.findall("Sensor"):
            values = [int(ts)]                                       #Initialise DB row content
            name = sensor.get("Type")
            for key in sensor.keys():
                if key != "Type":
                    fieldVal = sensor.get(key)
                    if (key == "dT"):
                        fv = fieldVal
                    else:
                        fv = '{:.3f}'.format(float(fieldVal))
                    self.sensFieldValues[name+key].config(text = fv+'\n'+self.sensFieldValues[name+key].cget('text'))
                    if len(fv) > self.sensFieldValues[name+key].cget('width'):
                        self.sensFieldValues[name+key].config(width = len(fv))
                        self.sensFieldNames[name+key].config(width = len(fv))
                    values.append((key,float(fieldVal)))              #Type conversion truncating to 5? characters. Appends (Name,Value)
            self.insertRow(name,values)

    def openDB(self, dbFile):
        """ create connection. Creates db in workspace if it does not exist
        :param dbFile: Name of sqlite3 file to connect to / create. Prefixed with node ID
        :return:
        """
        try:
            self.db = sqlite3.connect(dbFile)
        except sqlite3.Error as e:
            print 'sqlite3 connect error: ', e

    def createTable(self, conn, table, fields):
        """     create table for each sensor   
        :param conn: sqlite3 Connection object
        :param table: sensor(table) name
        :param fields: sensor fields - tuple
        Format:
                TableName = SensorName
                TableFields = <index, time, 1-n sensor field(s)>
            """
        table =''.join([c for c in table if c.isalnum()])   #strips out non alpha numeric to prevent string insertion attack
        
        cmdStr = 'CREATE TABLE IF NOT EXISTS '+ table
        cmdStr += ' (id integer PRIMARY KEY,'
        cmdStr += ' time integer NOT NULL UNIQUE'
        for field in fields:
            cmdStr = cmdStr + ' ,' +''.join([c for c in field if c.isalnum()]) + ' text NOT NULL'
        cmdStr += ');'
        try:
            c = conn.cursor()
        except sqlite3.Error as e:
            print 'sqlite3 cursor creation error: ', e
        try:
            c.execute(cmdStr)
        except sqlite3.Error as e:
            print 'sqlite3 execute error: ', e
        try:
            conn.commit()
        except sqlite3.Error as e:
            print 'sqlite3 commit error: ', e
    
    def insertRow(self,sensor,values):
        """
        Insert row of sensor readings
        :param sensor: sensor name. string
        :param values: list of <time, integer; (Value name1, string; Value1, float); ...; (Value nameN, string; ValueN, float)>
        :return:
        """
        wldCrd = '?'
        sql = ' INSERT INTO ' + sensor.replace(' ', '')                 #prevent string injection
        fieldNames = '(time'
        fieldValues =  [values[0]]
        for item in values:
            if  isinstance(item, tuple):
                fieldNames = fieldNames + ',' + item[0]
                fieldValues.append(item[1])
                wldCrd = wldCrd + ',?'
        values = tuple(fieldValues)

        sql = sql + fieldNames + ') VALUES('+ wldCrd + ') '
        cur = self.db.cursor()
        try:
            cur.execute(sql, fieldValues)
        except sqlite3.Error as e:
            print 'sqlite3 execute error: ', e
    
    def sensCols(self):
        n= 0
        for item in self.sensors.keys():
            n += len(self.sensors.get(item))
        return n

    def show(self):
        print "ping"
        self.display = True
        self.ownWindow.pack(fill=st.BOTH, expand=True)
        self.btn.config(command = self.hide)

    def hide(self):
        self.display = False
        self.ownWindow.pack_forget()
        self.btn.config(command = self.show)
        #insert code to hide parent frame if this is the only active node

    def setSensors(self):
        for sensor in self.initElements.findall("Sensor"):
                varList = []
                for entry in sorted(sensor.keys()):
                    if entry != "Type":
                        varList.append(entry)
                    self.sensors[sensor.get("Type")] = varList

    
    
    