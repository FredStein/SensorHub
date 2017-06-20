'''
Created on 18Nov.,2016

@author:  Fred

'''
import __init__ as st
from Client import ThreadedClient

if __name__ == '__main__':
    root = st.tk.Tk()
    client = ThreadedClient(root)
    root.protocol("WM_DELETE_WINDOW",client.endApp)
    root.mainloop()
    print 'Cheese?'
    