'''
Created on 27Nov.,2016

@author: Fred
'''
import __init__ as st
import sqlite3
from sqlite3 import Error
from datetime import datetime as dt
import xml.etree.ElementTree as ET
from test.test_xml_etree import attrib
from test.test_binop import isint


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
        guiFrame.columnconfigure(0, weight = 1)

        btnFrame =st.Frame(guiFrame,borderwidth=5,relief = st.GROOVE)
        btnFrame.grid(row=0, column=0, sticky = st.EW)
        
        self.nodeFrame = st.Frame(guiFrame,borderwidth=5,relief = st.GROOVE)
#        self.nodeFrame.bind("<Configure>", lambda event, canvas=canvas: self.onFrameConfigure(canvas))

#         canvas = st.Canvas(guiFrame, borderwidth=0)
#         self.nodeFrame = st.Frame(canvas,borderwidth=5,relief = st.GROOVE)
#         vsb = st.Scrollbar(root, orient="vertical", command=canvas.yview)
#         canvas.configure(yscrollcommand=vsb.set)
#         vsb.pack(side="right", fill="y")
#         canvas.pack(side="left", fill="both", expand=True)
#         canvas.create_window((0,0), window=self.nodeFrame, anchor="nw")
#         self.nodeFrame.bind("<Configure>", lambda event, canvas=canvas: self.onFrameConfigure(canvas))


        self.nodeFrame.grid(row=1, column=0, sticky = st.EW)

        self.nodeButtons = {}       #dict of node buttons Key: nodeID , Value: instance of button

        for w in st.xLoc:
            for h in st.yLoc:
                b = st.Button(btnFrame, state = st.DISABLED, text = w+h, width = 4, height = 2)
                b.grid(row=st.yLoc.index(h), column=st.xLoc.index(w), sticky=st.W)
                self.nodeButtons[w+h] = b
                
    def onFrameConfigure(self,canvas):          #Reset the scroll region to encompass the inner frame
        canvas.configure(scrollregion=canvas.bbox("all"))

    def createNode(self,node):
        """Activate button to show incoming data
             Create instance of sNode object in gui element
        :param node: tuple (IPv4 address, nodeID, initial message) strings
        """
        st.nodes[node[0]] = sNode(self.nodeFrame,node)
        btxt = node[1]+'\n'+node[0]
        self.nodeButtons[node[1]].config(state = st.NORMAL)
        self.nodeButtons[node[1]].config(command = st.nodes[node[0]].show)
        self.nodeButtons[node[1]].config(text = btxt, width = len(node[0])-3)
        st.nodes[node[0]].btn = self.nodeButtons[node[1]]

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
                        self.createNode((nAddr,nodeID,msg))                                         #activate node button in gui, create instance of sNode
                    st.nodes[nAddr].appendData(msg)                                                 #extract and append timestamp and instance values
 

class sNode():
    """ Sensor Node object """
    def __init__(self,parent,node):
        """ initialise Node
        :param node: tuple (IPv4 address, nodeID, initial message) strings
        :param parent: handle of containing tk.Frame
        :TODO parent could be some (any?) other object
        """
        self.initElements = ET.fromstring(node[2])
        self.ID = node[1]
        self.ownFrame = st.Frame(parent,borderwidth=5,relief = st.GROOVE)
        self.btn = None             #Populated with button handle by CreateNode
        self.varFieldNames = {}     #dict of sensor data fields. Key: Field Name, Value: tk.Label handle
                                    #Populated by build().
        self.sensors = {}           #Was [('Accelerometer','A',3), ('Gyroscope','Gyro',3), ('Gravity','Grav',3), ('Linear Acceleration','LA',3), ('Rotation Vector', 'RV',3)]
                                    #Populated by .build from first message for each node.{Type,[v1 ... vn]} (sorted) Excludes Timestamp
        self.db = None              #sqlite3 database connection object
                                    #Populated by build() with openDB()
        self.build()
        print node[0]+ ' NodeId ' + node[1] + ' is up'

    def show(self):
        self.ownFrame.grid(row=st.yLoc.index(self.ID[1]), column=st.xLoc.index(self.ID[0]), sticky=st.W)
        self.btn.config(command = self.hide)

    def hide(self):
        self.ownFrame.grid_remove()
        self.btn.config(command = self.show)
        #insert code to hide parent frame if this is the only active node
        
    def setSensors(self):
        for sensor in self.initElements.findall("Sensor"):
                varList = []
                for entry in sorted(sensor.keys()):
                    if entry != "Type":
                        varList.append(entry)
                    self.sensors[sensor.get("Type")] = varList
        
        
    def build(self):
        self.setSensors()
        hdrTitle = st.Label(self.ownFrame, text = self.ID)
        hdrTitle.grid(row=0,column=0, sticky=st.EW, columnspan = self.sensCols())
        dbFName = self.ID+'db.sqlite3'          #FileName  is NodeID(IP address) + 'db.sqlite3'
        self.openDB(dbFName)
        
        sTitle = "Time"
        sLbl = st.Label(self.ownFrame,text = sTitle)
        sLbl.grid(row = 1, column = 0, sticky = st.EW, rowspan = 2)
        instName = sTitle
        self.varFieldNames[instName] = st.Label(self.ownFrame, width = 10, bg ='white', text ="")
        self.varFieldNames[instName].grid(row = 3, column = 0, sticky = st.EW)
        colndx = 1
        """
        :TODO:    Sort Sensors to desired order if not already
        """ 
        for sensor in self.sensors.keys():
            sTitle = sensor
            sLbl = st.Label(self.ownFrame,text = sTitle)
            sLbl.grid(row = 1, column = colndx, sticky = st.EW, columnspan = len(self.sensors.get(sensor)))
            for ctr in xrange(0,len(self.sensors.get(sTitle))):
                vLbl = st.Label(self.ownFrame,text = self.sensors.get(sTitle)[ctr])
                vLbl.grid(row = 2, column = colndx+ctr, sticky = st.EW)
                instName = sTitle + self.sensors.get(sTitle)[ctr]
                self.varFieldNames[instName] = st.Label(self.ownFrame, width = 0, bg ='white', text ='')
                self.varFieldNames[instName].grid(row = 3, column = colndx+ctr, sticky = st.EW)
            colndx += len(self.sensors.get(sTitle))

            self.createTable(self.db, sensor, self.sensors[sensor])

    def appendData(self,msg):
        xmlElements =  ET.fromstring(msg)
        ts = xmlElements.find("Timestamp").attrib.get("Time")
        fieldVal = dt.fromtimestamp(float(ts)/1000).strftime('%m %d %H:%M:%S.%f')[:-3]
        
        temp1 = self.varFieldNames['Time'].cget('text')
        
        temp2 = fieldVal + '\n' + temp1
        
        self.varFieldNames['Time'].config(text = temp2, width = len(fieldVal))
        
        for sensor in xmlElements.findall("Sensor"):
            values = [int(ts)]                                       #Initialise DB row content
            name = sensor.get("Type")
            for key in sensor.keys():
                if key != "Type":
                    fieldVal = sensor.get(key)
                    fv = '{:.3f}'.format(float(fieldVal))
                    self.varFieldNames[name+key].config(text = fv+'\n'+self.varFieldNames[name+key].cget('text'))
                    if len(fv) > self.varFieldNames[name+key].cget('width'):
                        self.varFieldNames[name+key].config(width = len(fv))
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
    