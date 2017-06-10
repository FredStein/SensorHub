import Tkinter as tk

class ExampleView(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        l = tk.Label(self, text="your widgets go here...", anchor="c")
        l.pack(side="top", fill="both", expand=True)

if __name__=='__main__':
    root = tk.Tk()
    view = ExampleView(root)
    view.pack(side="top", fill="both", expand=True)
    root.mainloop()
    print "Cheese?"