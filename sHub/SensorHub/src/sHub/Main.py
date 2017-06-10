'''
Created on 18Nov.,2016

@author:  Fred
@TODO:    1:    sNode.sensors should be populated by .build from first message for each node.
                Distance removed for now: , ('Distance','Ht',1) as it does not appear in XML string
                & logic does not handle a missing expected sensor.
                Could change logic but if populated from xml question should not arise
                (Unless sensor drops out?)
'''
import __init__ as st
from Client import ThreadedClient

if __name__ == '__main__':
    root = st.tk.Tk()
    client = ThreadedClient(root)
    root.protocol("WM_DELETE_WINDOW",client.endApp)
    root.mainloop()
    print 'Cheese?'
    