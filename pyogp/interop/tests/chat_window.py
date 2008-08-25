from Tkinter import *
from ScrolledText import ScrolledText
import sys
import os

class ScrolledTextPanel(ScrolledText):
    def __init__(self, *args, **kwds):
        ScrolledText.__init__(self, state=DISABLED, *args, **kwds)
    
    def write(self, text):
        print "WRITING"
        self.config(state=NORMAL)
        print "INSERTING"
        self.insert(END, text)
        print "CONFIGGING"
        self.config(state=DISABLED)
        print "SEEING"
        self.see(END)
        print "UPDATING"
        self.master.update()
        print "DONE WRITING"
        
    def flush(self):
        print "FLUSHING"
        self.master.update()
        print "DONE FLUSHING"


class ChatWindow(Frame):
    def __init__(self):
        Frame.__init__(self, None)

        self.master.title("Chat Window")
        self.pack()

        self.text = ScrolledTextPanel()
        self.text.pack()

        self.update()
    
    def write(self, *args, **kwds):
        return self.text.write(*args, **kwds)

    def flush(self, *args, **kwds):
        return self.text.flush(*args, **kwds)
