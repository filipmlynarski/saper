from Tkinter import *
import time

root = Tk()

class Timer():
	def __init__(self):
		self.label = Label(text="")
		self.label.pack()
		self.update_clock()
	def update_clock(self):
		now = time.strftime("%H:%M:%S")
		self.label.configure(text=now)
		self.after(1000, self.update_clock)
tajm = Timer()
root.mainloop()