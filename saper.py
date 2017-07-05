import os
import time
import socket
import random
import tkMessageBox
from Tkinter import *
from design_tools import *
from game import game
from functools import partial
from multiprocessing import Process

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_address = ('158.69.201.134', 8887)
server_address = ('localhost', 8888)
sock.connect(server_address)

root = Tk()
root.option_add('*font', ('verdana', 12, 'bold'))
root.title("Saper")
#root.attributes("-fullscreen", True)

parameters={}

def update_parameters():
	for i in open('parameters').read().splitlines():
		parameters[i.split(' ')[0]] = i.split(' ')[1]

def clear():
	for widget in root.winfo_children():
		widget.destroy()

def change_size():
	file = open('parameters', 'w')
	file.write('size ' + v.get())
	file.close()
	update_parameters()

def show_stats():
	stats = [[0, 0, 0, 'Small'],[0, 0, 0, 'Medium'],[0, 0, 0, 'Large']]
	for i in open('stats').read().splitlines():
		i = i.split(' ')
		if i[1] == '1':
			stats[int(i[0])][0] += 1
			if stats[int(i[0])][1] > int(i[2]) or stats[int(i[0])][1] == 0:
				stats[int(i[0])][1] = i[2]
		stats[int(i[0])][2] += 1
	message = ''
	for idx, i in enumerate(stats):
		if idx != 0:
			message += '\n\n'
		message += i[3] + ':\n'
		message += 'attempts: ' + str(i[2])
		if i[2] > 0:
			message += '\npercantage of winnings: ' + str(int(float(i[0])/i[2]*100))+'%'
		else:
			message += '\npercantage of winnings: 0%'
		message += '\nbest time: ' + str(int(i[1])/60) + 'm' + str(int(i[1])%60) + 's'
	tkMessageBox.showinfo('Info', message)

def game_bar():
	menubar = Menu(root)
	filemenu = Menu(menubar, tearoff=0)
	filemenu.add_command(label="New Game", command=single_mode)
	filemenu.add_separator()
	global v
	v=StringVar()
	filemenu.add_radiobutton(label="Small", variable=v, value='0',command=change_size)
	filemenu.add_radiobutton(label="Medium", variable=v, value='1',command=change_size)
	filemenu.add_radiobutton(label="Large", variable=v, value='2', command=change_size)
	menubar.add_cascade(label="Game", menu=filemenu)

	Stats = Menu(menubar, tearoff=0)
	Stats.add_command(label="Show Stats", command=show_stats)
	menubar.add_cascade(label="Stats", menu=Stats)

	root.config(menu=menubar)
	filemenu.invoke(int(parameters['size']) + 2)

def single_mode():
	clear()
	update_parameters()
	game_bar()
	cos = Frame(root)
	game(cos, int(parameters['size']), [], 'single')
	cos.grid()
	#create_single_game()

def multi_mode():
	clear()
	lFrame = Frame(root)
	sFrame = Frame(root)

	sign_in(lFrame, main_menu, [sFrame])
	sign_up(sFrame, main_menu, [lFrame])

	lFrame.grid(column = 0, row = 0, sticky = 'n')
	sFrame.grid(column = 1, row = 0, padx=20)


def starting_menu():
	clear()
	single = Button(root, text='Singleplayer', bg='firebrick2', command=single_mode, width=20, height=3).grid(column=1, row=1, padx=250, pady=300)
	multi = Button(root, text='Multiplayer', bg='royal blue', command=multi_mode, width=20, height=3).grid(column=3, row=1)

update_parameters()
starting_menu()

root.mainloop()