from Tkinter import *
import os

root = Tk()
photo = PhotoImage(file='not_clicked.png')

def create_game():
	cos = Frame(root, width=30, height=30)
	cos.grid()
	test = Label(cos, cursor='dot', image=photo, width=30, height=30)
	test.grid()

create_game()

root.mainloop()