import os
import time
import random
from Tkinter import *
from functools import partial
from multiprocessing import Process

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

if not os.path.isfile('parameters.txt'):
	file = open('parameters.txt', 'w')
	file.write('size 0\n')
	file.close()
stop = False
sec = 0
parameters={}
def update_parameters():
	for i in open('parameters.txt').read().splitlines():
		parameters[i.split(' ')[0]] = i.split(' ')[1]

def clear():
	for widget in root.winfo_children():
		widget.destroy()

def change_size():
	file = open('parameters.txt', 'w')
	file.write('size ' + v.get())
	file.close()
	update_parameters()

def time_lable():
	global sec
	print stop
	if not stop:
		sec += 1
		Time_table['text'] = sec
		# Take advantage of the after method of the Label
		Time_table.after(1000, time_lable)
	else:
		sec = 0
'''	global game_time
	while True:
		time.sleep(1)
		game_time += 1
		Button(root, text='test').grid(row=2)
		Time_table = Label(stats, text=str(game_time), fg='red', bg='black', width=5, height=1)
		Time_table.grid(column=4, row=0)
		#print str(game_time)'''
def game_bar():
	clear()
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
def modify_grid(x, y, event, flag=False, rec=False):
	print sec
	if sec == 0:
		time_lable()
	global bombs_found, stats
	end = False
	if not flag:
		if bomb_grid[x][y] == 1:
			end = True
			current_grid[x][y] = 3
			show_grid('False', 'False', end)
		elif current_grid[x][y] != 1:
			around = bombs_around(x, y)
			current_grid[x][y] = around[0] + 10
			if around[0] == 0:
				for i in around[1]:
					modify_grid(i[0], i[1], event, False, True)
				if not rec and not end:
					show_grid()
			elif not rec and not end:
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

def show_grid(do_x='False', do_y='False', end=False):
	if do_x == 'False':
		for widget in game.winfo_children():
			widget.destroy()
		for h_idx, h in enumerate(current_grid):
			for w_idx, w in enumerate(h):
				if w == 0:
					burton = Label(game, image=not_clicked, width=30, height=30)
					if not end:
						left_click  = partial(modify_grid, h_idx, w_idx)
						right_click = partial(modify_grid, h_idx, w_idx, True)
						burton.bind("<Button-1>", left_click)
						burton.bind("<Button-3>", right_click)
					burton.grid(column=w_idx, row=h_idx)
				elif w == 1:
					burton = Label(game, image=flag, width=30, height=30)
					if not end:
						right_click = partial(modify_grid, h_idx, w_idx, True)
						burton.bind("<Button-3>", right_click)
					burton.grid(column=w_idx, row=h_idx)
				elif w > 9:
					Label(game, image=around[str(w-10)], width=30, height=30).grid(column=w_idx, row=h_idx)
				elif w == 3:
					Label(game, image=clicked_bomb, width=30, height=30).grid(column=w_idx, row=h_idx)
	else:
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
			right_click = partial(modify_grid, h_i, w_i, True)
			burton.bind("<Button-3>", right_click)
			burton.grid(column=w_i, row=h_i)
		elif w > 9:
			Label(game, image=around[str(w-10)], width=30, height=30).grid(column=w_i, row=h_i)
		elif w == 3:
			Label(game, image=clicked_bomb, width=30, height=30).grid(column=w_i, row=h_i)
	if done():
		stop = True

def create_game():
	clear()
	game_bar()
	global game, bomb_grid, current_grid, bombs_found, stats, bombs, to_find, p, Time_table
	if parameters['size'] == '0':
		w, h, bombs = 10*30, 10*30, 10
	elif parameters['size'] == '1':
		w, h, bombs = 16*30, 16*30, 40
	elif parameters['size'] == '2':
		w, h, bombs = 30*30, 16*30, 99
	to_find = (w/30) * (h/30) - bombs
	Frame(width=10).grid(column=0, row=0)
	stats = Frame(root, width=w, height=100)
	stats.grid(column=1, row=0, padx=100)
	game = Frame(root, width=w, height=h)
	game.grid(column=1, row=1)
	bombs_found = 0
	Bombs = Label(stats, text=str(bombs - bombs_found), fg='red', bg='black', width=5, height=1)
	Bombs.grid(column=0, row=0)
	Label(stats, width=5).grid(column=1, row=0)
	Restart = Button(stats, text='restart', width=10, height=1, command=create_game)
	Restart.grid(column=2, row=0)
	Label(stats, width=5).grid(column=3, row=0)
	Time_table = Label(stats, text='0', fg='red', bg='black', width=5, height=1)
	Time_table.grid(column=4, row=0)
	sec = 0
	bomb_grid = []
	for high in range(h/30):
		bomb_grid.append([])
		for wdth in range(w/30):
			bomb_grid[-1].append(0)
	bombs_locations = random.sample(xrange((w/30) * (h/30)), bombs)
	for i in bombs_locations:
		bomb_grid[i/(w/30)][i%(h/30)] = 1

	current_grid = []
	for high in range(h/30):
		current_grid.append([])
		for wdth in range(w/30):
			current_grid[-1].append(0)

	show_grid()

def single_mode():
	create_game()

def multi_mode():
	clear()

def starting_menu():
	Label(root, height=8).grid(column=0, row=0)
	Label(root, width=30).grid(column=0, row=1)
	single = Button(root, text='Singleplayer', bg='green', command=single_mode, width=20, height=3).grid(column=1, row=1)
	Label(root, width=10).grid(column=2, row=1)
	multi = Button(root, text='Multiplayer', bg='red', command=multi_mode, width=20, height=3).grid(column=3, row=1)

update_parameters()
starting_menu()

root.mainloop()