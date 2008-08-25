from Tkinter import *
from ScrolledText import ScrolledText
import sys
import os

class ScrolledTextPanel(ScrolledText):
    def __init__(self):
        ScrolledText.__init__(self, state=DISABLED)
    
    def write(self, text):
        self.config(state=NORMAL)
        self.insert(END, text)
        self.config(state=DISABLED)
        self.see(END)
        self.master.update()
        
class ChatWindow(Frame):
    def __init__(self):
        Frame.__init__(self, None)

        self.master.title("Chat Window")
        self.pack()

        self.text = ScrolledTextPanel()
        self.text.pack()

        self.update()
    
    def write(self, text):
        return self.text.write(text)
