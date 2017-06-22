'''
Created on 20Feb.,2017

@author: Fred Stein
'''
import __init__ as st
from GUI import UI
import time
import socket
import xml.etree.ElementTree as ET
from _elementtree import fromstring

class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI. We spawn a new thread for the worker.
        """
        self.master = master
        
        # Set up the GUI part
        self.gui = UI(master, self.endApp)

        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        self.running = 1
        self.IOT = st.threading.Thread(target=self.IOThread)
        self.IOT.setDaemon(1)
        self.IOT.start()

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()

    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        if not self.running:
            # Cleanup in EndApp
            self.master.destroy()

        self.gui.processQueue()
        self.master.after(40, self.periodicCall)

    def IOThread(self):
        """
        This is where we handle the asynchronous I/O.
        The thread has to yield control.
        :TODO Amend to listen for well formed (known) XML from SNodeServer
        """
        port = 50000
        host = ''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST, 1)
        s.bind((host, port))

        while self.running:
            time.sleep(0.1)
            message, address = s.recvfrom(8192)
            msgStr = message.decode('utf8')
            print msgStr
            nodeID = fromstring(message).attrib.get('Name')
            if nodeID in self.gui.nodeButtons.keys():                       #Is this one of our nodes?  TODO: ID encryption to prevent node spoofing)
                if address[0] not in st.queues:                             #node ip address is unknown
                    st.queues[address[0]] = st.Queue.Queue()                #add the address and a queue for it to the queue dict
                st.queues[address[0]].put(msgStr)
            else:
                pass                                                        #not our node. Do nothing with it

    def endApp(self):
        for node in st.nodes:
            st.nodes[node].db.commit()
            st.nodes[node].db.close()                                       #:TODO success test here & exception handling
        self.running = 0
