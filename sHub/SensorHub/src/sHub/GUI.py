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
        root.geometry('+%d+%d' % (100, 100))                                    #:TODO:    To config
        menubar = st.Menu(root)
        filemenu = st.Menu(menubar, tearoff = False)
        menubar.add_cascade(label = 'File', menu = filemenu)
        filemenu.add_command(label = 'Quit', command = endCommand)
        root.config(menu = menubar)

        guiFrame = st.Frame(root,borderwidth=5,relief = st.GROOVE)
        guiFrame.pack(expand = True, fill = st.BOTH)

        btnFrame =st.Frame(guiFrame)
        btnFrame.pack()
               
        self.nodeButtons = {}       #dict of node buttons Key: nodeID , Value: instance of button
        self.nodeWindows = {}       #dict of node windows Key: nodeID , Value: instance of frame

        for w in st.xLoc:
            for h in st.yLoc:
                b = st.Button(btnFrame, state = st.DISABLED, text = w+h, width = 4, height = 2)
                b.grid(row=st.yLoc.index(h), column=st.xLoc.index(w))
                self.nodeButtons[w+h] = b
                self.nodeWindows[w+h] = st.Frame(guiFrame,borderwidth=2,relief = st.GROOVE, bg="beige")

    def createNode(self,node):
        """Activate button to signal node active and enable display of incoming data
             Create instance of sNode object
        :param node: tuple (IPv4 address, nodeID, initial message) strings
        """
        btxt = node[1]+'\n'+node[0]
        self.nodeButtons[node[1]].config(state = st.NORMAL)
        st.nodes[node[0]] = sNode(self.nodeWindows[node[1]],node,self.nodeButtons[node[1]])
        self.nodeButtons[node[1]].config(command = st.nodes[node[0]].show)
        self.nodeButtons[node[1]].config(text = btxt, width = len(node[0])-3)

    def processQueue(self):
        """
        Handle all the messages currently in the sensor queue (if any).
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
        
        self.headerFrame = st.Frame(self.ownWindow)
        self.headerFrame.grid(row = 0, column = 0, sticky = st.W)                                   #Do not fill X here or header stretches to cover scrollbar (?)
        self.ownWindow.columnconfigure(0, weight = 1)
        self.dp = st.Frame(self.ownWindow)
        self.dp.grid(row = 1, column = 0, sticky = st.NSEW)
        self.ownWindow.rowconfigure(1, weight = 1)
        self.dFrame = dataFrame(self.dp, self.sensFieldValues)
        
        nodeTitle = st.Label(self.headerFrame, text = self.ID)
        nodeTitle.grid(row=0,column=0, sticky=st.EW, columnspan = self.sensCols()+1)
        
        sTitle = "Time"
        self.sensFieldNames[sTitle] = st.Label(self.headerFrame,text = sTitle)
        self.sensFieldNames[sTitle].grid(row = 1, column = 0, sticky = st.EW, rowspan = 2)
        self.headerFrame.columnconfigure(0, weight = 1)

        ts = self.initElements.find("Timestamp").attrib.get(sTitle)
        fieldVal = dt.fromtimestamp(float(ts)/1000).strftime("%m %d %H:%M:%S.%f")[:-3]
        
        self.sensFieldNames[sTitle].config(width = len(fieldVal)-4)         #Size header to fit timestamp
        self.dFrame.populate(sTitle, 0)
        colndx = 1
        """
        :TODO:    Sort Sensors to desired order if not already
        """ 
        for sensor in self.sensors.keys():
            sLbl = st.Label(self.headerFrame, text = sensor)
            sLbl.grid(row = 1, column = colndx, sticky = st.EW, columnspan = len(self.sensors.get(sensor)))
            self.headerFrame.columnconfigure(colndx, weight = 1)
            
            for ctr in xrange(0,len(self.sensors.get(sensor))):
                instName = sensor + self.sensors.get(sensor)[ctr]
                self.sensFieldNames[instName] = st.Label(self.headerFrame,text = self.sensors.get(sensor)[ctr], width = 0)
                self.sensFieldNames[instName].grid(row = 2, column = colndx+ctr, sticky = st.EW)
                self.headerFrame.columnconfigure(colndx+ctr, weight = 1)
                self.dFrame.populate(instName, colndx+ctr)
                
            colndx += len(self.sensors.get(sensor))
            self.createTable(self.db, sensor, self.sensors[sensor])

    def appendData(self,msg):
        xmlElements =  ET.fromstring(msg)
        ts = xmlElements.find("Timestamp").attrib.get("Time")
        fieldVal = dt.fromtimestamp(float(ts)/1000).strftime('%m %d %H:%M:%S.%f')[:-3]
        temp = fieldVal + '\n' + self.sensFieldValues['Time'].cget('text')
        self.sensFieldValues['Time'].config(text = temp)
        
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
        self.display = True
        self.ownWindow.pack(fill=st.BOTH, expand=True)
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


class dataFrame(st.Frame):
    def __init__(self, root, sfv):
        self.sensFieldValues = sfv
        st.Frame.__init__(self, root)
        self.canvas = st.Canvas(root, width = 0)
        self.frame = st.Frame(self.canvas)
        self.vsb = st.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vsb.pack(side="right", fill="y")
        self.canvas.create_window((0,0), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.canvas.bind("<Configure>", self.FrameHeight)

    def populate(self, colKey, col):
        '''Put in data'''
        self.sensFieldValues[colKey] = st.Label(self.frame, text="", bd = 2, bg = 'blue', fg = 'white', justify = st.RIGHT)
        self.sensFieldValues[colKey].grid(row=0, column=col, sticky = st.NSEW)
        self.frame.columnconfigure(col, weight = 1)

    def FrameHeight(self, event):
        frame_height = event.height
        frame_width = event.width
        self.canvas.itemconfig(self.frame, height = frame_height, width = frame_width)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    