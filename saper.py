import os
import time
import socket
import random
import tkMessageBox
from Tkinter import *
from functools import partial
from multiprocessing import Process

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 8887)
sock.connect(server_address)

root = Tk()
root.option_add('*font', ('verdana', 12, 'bold'))
root.title("Saper")

bomb         = PhotoImage(file='data/bomb.png')
flag         = PhotoImage(file='data/flag.png')
not_clicked  = PhotoImage(file='data/not_clicked.png')
clicked_bomb = PhotoImage(file='data/clicked_bomb.png')
flagged_bomb = PhotoImage(file='data/flagged_bomb.png')
around = {}
for i in range(0, 9):
	around[str(i)] = PhotoImage(file='data/' + str(i) + '.png')
if not os.path.isfile('log_info'):
	open('log_info', 'w')
if not os.path.isfile('parameters'):
	file = open('parameters', 'w')
	file.write('size 0\n')
	file.close()
if not os.path.isfile('stats'):
	file = open('stats', 'w')
	file.close()
parameters={}

def update_stats(size, result='0', t='0'):
	file = open('stats', 'a+')
	file.write(str(size) + ' ' + str(result) + ' ' + str(t) + '\n')
	file.close()

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

def time_lable():
	global sec, stop
	if not stop:
		sec += 1
		Time_table['text'] = sec
		Time_table.after(1000, time_lable)
	else:
		sec = -1

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
def done():
	checked = 0
	for h in current_grid:
		for w in h:
			if w > 9:
				checked += 1
	return checked == to_find
def bombs_around(x, y):
	to_check = [[i, j] for i in range(x-1, x+2) for j in range(y-1, y+2) if 0 <= i < len(current_grid) and 0 <= j < len(current_grid[0])]
	ret = 0
	for i in to_check:
		if bomb_grid[i[0]][i[1]] == 1:
			ret += 1
	return [ret, [i for i in to_check if i != [x, y] and current_grid[i[0]][i[1]] < 10]]
def flags_around(x, y):
	to_check = [[i, j] for i in range(x-1, x+2) for j in range(y-1, y+2) if 0 <= i < len(current_grid) and 0 <= j < len(current_grid[0])]
	ret, ret2 = 0, []
	for i in to_check:
		if current_grid[i[0]][i[1]] == 1:
			ret += 1
		elif current_grid[i[0]][i[1]] == 0:
			ret2.append(i)
	return [ret, ret2]

def modify_grid(x, y, event='', flag=False):
	global stop
	if not stop:
		if sec == -1:
			time_lable()
		global bombs_found, stats
		end = False
		if current_grid[x][y] > 10:
			f_around = flags_around(x, y)
			if f_around[0] == current_grid[x][y] - 10:
				for to_click in f_around[1]:
					modify_grid(to_click[0], to_click[1])
		elif not flag:
			if bomb_grid[x][y] == 1:
				end = True
				current_grid[x][y] = 3
				stop = True
				Restart['text'] = u'\u2639'
				if not sec < 1:
					update_stats(parameters['size'])
					Bombs = Label(stats, text=str(bombs - bombs_found), fg='red', bg='black', width=5, height=1)
					Bombs.grid(column=0, row=0)
				show_grid(x, y)
			else:
				around = bombs_around(x, y)
				if current_grid[x][y] == 1:
					bombs_found -= 1
				current_grid[x][y] = around[0] + 10
				if around[0] == 0:
					for i in around[1]:
						modify_grid(i[0], i[1], event, False)
					if not end:
						show_grid(x, y)
				elif not end:
					show_grid(x, y)
		else:
			if current_grid[x][y] == 0:
				bombs_found += 1
				current_grid[x][y] = 1
			else:
				bombs_found -= 1
				current_grid[x][y] = 0
			Bombs = Label(stats, text=str(bombs - bombs_found), fg='red', bg='black', width=5, height=1)
			Bombs.grid(column=0, row=0)
			show_grid(x, y)

def show_grid(do_x, do_y):
	h_i, w_i = do_x, do_y
	w = current_grid[h_i][w_i]
	if w == 0:
		burton = Label(game, image=not_clicked, width=30, height=30)
		left_click  = partial(modify_grid, h_i, w_i)
		right_click = partial(modify_grid, h_i, w_i, True)
		burton.bind("<Button-1>", left_click)
		burton.bind("<Button-3>", right_click)
		burton.grid(column=w_i, row=h_i)
	elif w == 1:
		burton = Label(game, image=flag, width=30, height=30)
		#left_click  = partial(modify_grid, h_i, w_i)
		right_click = partial(modify_grid, h_i, w_i, True)
		#burton.bind("<Button-1>", left_click)
		burton.bind("<Button-3>", right_click)
		burton.grid(column=w_i, row=h_i)
	elif w == 10:
		Label(game, image=around[str(w-10)], width=30, height=30).grid(column=w_i, row=h_i)
	elif w > 10:
		burton = Label(game, image=around[str(w-10)], width=30, height=30)
		left_click  = partial(modify_grid, h_i, w_i)
		right_click = partial(modify_grid, h_i, w_i)
		burton.bind("<Button-1>", left_click)
		burton.bind("<Button-3>", right_click)
		burton.grid(column=w_i, row=h_i)
	elif w == 3:
		Label(game, image=clicked_bomb, width=30, height=30).grid(column=w_i, row=h_i)
	if done():
		Restart['text'] = u'\u263b'
		if sec != -1:
			update_stats(parameters['size'], '1', sec)
		global stop
		stop = True

def create_game():
	clear()
	Button(root, text=u'\u2190', command=starting_menu).grid(column=0, row=0)
	global game, bombs_found, stats, to_find, p, Time_table, sec, stop, Restart
	to_find = (w/30) * (h/30) - bombs
	Frame(width=40).grid(column=0, row=0)
	stats = Frame(root, width=w, height=100)
	stats.grid(column=1, row=0, padx=100)
	game = Frame(root, width=w, height=h)
	game.grid(column=1, row=1)
	bombs_found = 0
	Bombs = Label(stats, text=str(bombs - bombs_found), fg='red', bg='black', width=5, height=1)
	Bombs.grid(column=0, row=0)
	Label(stats, width=5).grid(column=1, row=0)
	Restart = Button(stats, text=u'\u263a', width=1, height=1, command=create_single_game)
	Restart.grid(column=2, row=0)
	Label(stats, width=5).grid(column=3, row=0)
	Time_table = Label(stats, text='0', fg='red', bg='black', width=5, height=1)
	Time_table.grid(column=4, row=0)
	sec = -1
	stop = False
	game_bar()

def create_single_game():
	global bomb_grid, current_grid, w, h, bombs
	if parameters['size'] == '0':
		w, h, bombs = 10*30, 10*30, 10
	elif parameters['size'] == '1':
		w, h, bombs = 16*30, 16*30, 40
	elif parameters['size'] == '2':
		w, h, bombs = 30*30, 16*30, 99
	bomb_grid = []
	for high in range(h/30):
		bomb_grid.append([])
		for wdth in range(w/30):
			bomb_grid[-1].append(0)
	bombs_locations = random.sample(xrange((w/30) * (h/30)), bombs)
	for i in bombs_locations:
		bomb_grid[i/(w/30)][i%(w/30)] = 1
	current_grid = []
	for high in range(h/30):
		current_grid.append([])
		for wdth in range(w/30):
			current_grid[-1].append(0)
	create_game()
	for h_idx in range(h/30):
		for w_idx in range(w/30):
			show_grid(h_idx, w_idx)
	
def comunicate(x):
	sock.sendall(x)
	data = sock.recv(1024)
	return eval(data)

def single_mode():
	create_single_game()

def sign_in():
	log = Login_entry.get()
	pas = Password_entry.get()
	if len(log) > 5 and len(pas) > 5:
		status = comunicate(str({'action': 'sign_in', 'login': log, 'password': pas}))
		if status['status'] == True:
			file = open('log_info', 'w')
			file.write(log + '\n' + pas)
			file.close()
			Login_entry['bg'] = 'green'
		else:
			Login_entry['bg'] = 'red'

def sign_up():
	log = new_Login_entry.get()
	pas = new_Password_entry.get()
	if len(log) > 2 and len(pas) > 2:
		result = comunicate(str({'action': 'sign_up', 'login': log, 'password': pas}))
		if result['status'] == True:
			file = open('log_info', 'w')
			file.write(log + '\n' + pas)
			file.close()
			new_Login_entry['bg'] = 'green'
		else:
			new_Login_entry['bg'] = 'red'

def login_page():
	global Login_entry, Password_entry, new_Login_entry, new_Password_entry
	Frame(root, width=100).grid(row=0, column=2)
	Frame(root, height=10).grid(column=0, row=3)

	Label(root, text='Sign in', width=10, anchor=W).grid(row=1, column=1)
	Label(root, text='Sign up').grid(row=1, column=3)

	Login = Frame(root)
	Login.grid(column=1, row=2)
	Password = Frame(root)
	Password.grid(column=1, row=4)

	Label(Login,    text='login: '   ,width=9, anchor=W).grid(column=0, row=0)
	Label(Password, text='password: ',width=9, anchor=W).grid(column=0, row=0)

	Login_entry = Entry(Login, width=15)
	Login_entry.grid(column=1, row=0)
	Password_entry = Entry(Password, width=15, show='*')
	Password_entry.grid(column=1, row=0)

	new_Login = Frame(root)
	new_Login.grid(row=2, column=3)
	new_Password = Frame(root)
	new_Password.grid(row=4, column=3)

	Label(new_Login,     text='login: '   ,width=9, anchor=W).grid(column=0, row=0)
	Label(new_Password,  text='password: ',width=9, anchor=W).grid(column=0, row=0)

	Button(root, text='Login', command=sign_in).grid(column=1, row=5)
	Button(root, text='Create Account', command=sign_up).grid(column=3, row=5)

	new_Login_entry = Entry(new_Login, width=15)
	new_Login_entry.grid(column=1, row=0)
	new_Password_entry = Entry(new_Password, width=15)
	new_Password_entry.grid(column=1, row=0)

def multi_mode():
	clear()
	game_bar()
	Button(root, text=u'\u2190', command=starting_menu).grid(column=4, row=0)
	Frame(root, width=40, height=40).grid(column=0, row=0)
	if len(open('log_info').read().splitlines()) == 2:
		print 'login saved'
	else:
		login_page()


def starting_menu():
	clear()
	Label(root, height=8).grid(column=0, row=0)
	Label(root, width=30).grid(column=0, row=1)
	single = Button(root, text='Singleplayer', bg='green', command=single_mode, width=20, height=3).grid(column=1, row=1)
	Label(root, width=10).grid(column=2, row=1)
	multi = Button(root, text='Multiplayer', bg='red', command=multi_mode, width=20, height=3).grid(column=3, row=1)

update_parameters()
starting_menu()

root.mainloop()
