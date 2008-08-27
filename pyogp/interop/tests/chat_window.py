from Tkinter import *
from ScrolledText import ScrolledText
import sys
import os

class ScrolledTextPanel(ScrolledText):
    def __init__(self, *args, **kwds):
        ScrolledText.__init__(self, state=DISABLED, *args, **kwds)
    
    def write(self, text):
        print "WRITING text: " + text
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

        self.tx = Text(self, height=1, width=60, borderwidth=5, relief=RIDGE)
        self.tx.height = 1
        self.tx.width = 60
        self.tx.pack()
        self.tx.bind('<Return>', self.hit_enter)
        
        self.b1 = Button(self, text="Send")
        self.b1.pack(side=RIGHT, before=self.tx)
        self.b1.configure(command=self.hit_enter)

        self.update()

    def set_enter_hit(self, func):
        self.tx.bind('<Return>', func)
        self.b1.configure(command=func)

    def hit_enter(self):
        print "ENTER HIT---------------"
        if self.tx.get(END) == '\n':
            print 'REMOVING SPACE'
            self.tx.delete(END)

        if self.tx.get(1.0) == '\n':
            print 'REMOVING SPACE'
            self.tx.delete(1.0)

        msg = self.tx.get(1.0, END)
        self.tx.delete(1.0,END)
        return msg.replace("\n","")

    def write(self, *args, **kwds):
        return self.text.write(*args, **kwds)

    def flush(self, *args, **kwds):
        return self.text.flush(*args, **kwds)
