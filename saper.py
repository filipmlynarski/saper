import os
import time
import socket
import random
import tkMessageBox
from Tkinter import *
#from design_tools import *
from game import game
from functools import partial
from multiprocessing import Process

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 8888)
sock.connect(server_address)

root = Tk()
root.option_add('*font', ('verdana', 12, 'bold'))
root.title("Saper")
root.attributes("-fullscreen", True)

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

def comunicate(x):
	sock.sendall(x)
	data = sock.recv(1024)
	return eval(data)

def invite(evt):
    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    print 'You selected item %d: "%s"' % (index, value)

def create_friends():
	global friends, friends_list
	scrollbar = Scrollbar(root)
	scrollbar.grid(column=1, row=1)
	Label(root, text='Online Users', fg='green').grid(row=0, column=1)
	friends_list = Listbox(root, yscrollcommand = scrollbar.set, name='friends', width=14)
	friends_list.bind('<<ListboxSelect>>', invite)
	new = comunicate(str({'action': 'online_users', 'login': my_login}))
	friends = new['online_users']
	for friend in friends:
		if friend != new['me']:
			print friend
			print new['me']
			friends_list.insert(END, friend)
	friends_list.grid(column=1, row=1)
	scrollbar.config(command = friends_list.yview)

def update_friends():
	global friends
	new = comunicate(str({'action': 'online_users', 'login': my_login}))
	if new['online_users'] != friends:
		friends_list.delete(first=0, last=friends_list.size())
		friends = new['online_users']
		for friend in friends:
			if friend != new['me']:
				print friend
				print new['me']
				friends_list.insert(END, friend)
	root.after(2000, update_friends)

def deselect(x):
	for i in range(3):
		if i != x:
			C[i].deselect()

def send_room():
	for i in range(len(CheckVars)):
		if CheckVars[i].get() == 1:
			comunicate(str({'action': 'create_room', 'size': str(i), 'login': my_login}))

def room_creator():
	clear()
	game_bar()
	Label(root, text='Size ').grid(column=0, row=0)
	global CheckVars, C
	CheckVars = [IntVar() for i in range(3)]
	C, sizes = [], ['small', 'medium', 'big']
	for idx, i in enumerate(sizes):
		f = partial(deselect, idx)
		C.append(Checkbutton(root, text=i, variable = CheckVars[idx],
		command = f, onvalue = 1, offvalue = 0))
		C[idx].grid(row=0, column=1 + idx, pady=5, padx=3)
	Button(root, text='Create Room', command=send_room).grid(row=1, column=1, pady=5, columnspan=2)
#def show_room():


def multi_window():
	clear()
	game_bar()
	Button(root, text='Play', command=room_creator).grid(row=0, column=0)
	rooms = comunicate(str({'action': 'show_rooms'}))
	print rooms
	for idx, i in enumerate(rooms):
		sizes = ['small', 'medium', 'big']
		Label(root, text='Host: ' + rooms['host'] + 'size: ' + sizes[rooms['size']] + rooms['users'] + '/6')
	create_friends()
	update_friends()

def sign_in():
	log = Login_entry.get()
	pas = Password_entry.get()
	if len(log) > 3 and len(pas) > 3:
		status = comunicate(str({'action': 'sign_in', 'login': log, 'password': pas}))
		if status['status'] == True:
			file = open('log_info', 'w')
			file.write(log + '\n' + pas)
			file.close()
			Login_entry['bg'] = 'green'
			multi_window()
		else:
			Login_entry['bg'] = 'red'

def sign_up():
	log = new_Login_entry.get()
	pas = new_Password_entry.get()
	nick = new_Nick_Entry.get()
	if len(log) > 2 and len(pas) > 2:
		result = comunicate(str({'action': 'sign_up', 'login': log, 'password': pas, 'nick': nick}))
		if result['status'] == True:
			file = open('log_info', 'w')
			file.write(log + '\n' + pas)
			file.close()
			new_Login_entry['bg'] = 'green'
			multi_window()
		else:
			new_Login_entry['bg'] = 'red'

def login_page():
	global Login_entry, Password_entry, new_Login_entry, new_Password_entry, new_Nick_Entry
	Frame(root, width=100).grid(row=0, column=2)
	Frame(root, height=10).grid(column=0, row=3)
	Frame(root, height=8).grid(column=0, row=5)

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
	new_Nick = Frame(root)
	new_Nick.grid(row=6, column=3)

	Label(new_Login,     text='login: '   ,width=9, anchor=W).grid(column=0, row=0)
	Label(new_Password,  text='password: ',width=9, anchor=W).grid(column=0, row=0)
	Label(new_Nick,      text='nick: '    ,width=9, anchor=W).grid(column=0, row=0)

	Button(root, text='Login', command=sign_in).grid(column=1, row=6)
	Button(root, text='Create Account', command=sign_up).grid(column=3, row=7)

	new_Login_entry = Entry(new_Login, width=15)
	new_Login_entry.grid(column=1, row=0)
	new_Password_entry = Entry(new_Password, width=15)
	new_Password_entry.grid(column=1, row=0)
	new_Nick_Entry = Entry(new_Nick, width=15)
	new_Nick_Entry.grid(column=1, row=0)

def multi_mode():
	global my_login
	my_login = open('log_info').read().splitlines()[0]
	clear()
	game_bar()
	Button(root, text=u'\u2190', command=starting_menu).grid(column=4, row=0)
	Frame(root, width=40, height=40).grid(column=0, row=0)
	saved_info = open('log_info').read().splitlines()
	if len(saved_info) == 2:
		check_login = str({'action': 'sign_in', 'login': saved_info[0], 'password': saved_info[1]})
		if comunicate(check_login)['status'] == True:
			multi_window()
		else:
			login_page()
	else:
		login_page()


def starting_menu():
	clear()
	single = Button(root, text='Singleplayer', bg='firebrick2', command=single_mode, width=20, height=3).grid(column=1, row=1, padx=250, pady=300)
	multi = Button(root, text='Multiplayer', bg='royal blue', command=multi_mode, width=20, height=3).grid(column=3, row=1)

update_parameters()
starting_menu()

root.mainloop()