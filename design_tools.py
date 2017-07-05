import socket
from game import game
from Tkinter import *
from functools import partial

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_address = ('158.69.201.134', 8887)
server_address = ('localhost', 8888)
sock.connect(server_address)

nick = ''

def clear(x):
	for widget in x.winfo_children():
		widget.destroy()

def comunicate(x):
	sock.sendall(str(x))
	BUFF_SIZE = 1024
	data = ""
	while True:
		part = sock.recv(BUFF_SIZE)
		data += part
		if len(part) < BUFF_SIZE:
			break
	try:
		return eval(data)
	except:
		return {}


class sign_in:

	def __init__(self, master, after, to_clear = []):
		for widget in master.winfo_children():
			widget.destroy()
		self.master = master
		self.username = StringVar()
		self.password = StringVar()
		self.after = after
		self.to_clear = to_clear

		Label(self.master, text = 'username').grid(column = 0, row = 0, sticky = 'w')
		self.uEntry = Entry(self.master, textvariable = self.username, width = 10)
		self.uEntry.grid(column = 1, row = 0, padx = 4, pady = 4)

		Label(self.master, text = 'password').grid(column = 0, row = 1, sticky = 'w')
		self.pEntry = Entry(self.master, textvariable = self.password, width = 10)
		self.pEntry.grid(column = 1, row = 1, padx = 4, pady = 4)

		Button(self.master, command = self.login, text = 'Login').grid(column = 0, row = 2, columnspan = 2)

	def validate(self):
		response = comunicate({
			'action': 'sign_in',
			'username': self.username.get(),
			'password': self.password.get()
			})
		return [response['status'], response['nick']]

	def login(self):
		result = self.validate()
		if result[0]:
			global nick
			nick = result[1]
			print nick
			file = open('log_info', 'w')
			file.write(self.username.get()+'\n'+self.password.get())
			file.close()
			self.after(self.master, self.to_clear)
		else:
			self.uEntry['bg'] = 'red'
			self.pEntry['bg'] = 'red'


class sign_up:

	def __init__(self, master, after, to_clear = []):
		for widget in master.winfo_children():
			widget.destroy()
		self.master = master
		self.username = StringVar()
		self.password = StringVar()
		self.nick = StringVar()
		self.after = after
		self.to_clear = to_clear

		Label(self.master, text = 'username').grid(column = 0, row = 0, sticky = 'w')
		self.uEntry = Entry(self.master, textvariable = self.username, width = 10)
		self.uEntry.grid(column = 1, row = 0, padx = 4, pady = 4)

		Label(self.master, text = 'password').grid(column = 0, row = 1, sticky = 'w')
		self.pEntry = Entry(self.master, textvariable = self.password, width = 10)
		self.pEntry.grid(column = 1, row = 1, padx = 4, pady = 4)

		Label(self.master, text = 'nick').grid(column = 0, row = 2, sticky = 'w')
		self.nEntry = Entry(self.master, textvariable = self.nick, width = 10)
		self.nEntry.grid(column = 1, row = 2, padx = 4, pady = 4)

		Button(self.master, command = self.register, text = 'Register').grid(column = 0, row = 3, columnspan = 2)

	def validate(self):
		response = comunicate({
			'action': 'sign_up',
			'username': self.username.get(),
			'password': self.password.get(),
			'nick': self.nick.get()
			})
		return response['status']

	def register(self):
		if self.validate():
			file = open('log_info', 'w')
			file.write(self.username.get()+'\n'+self.password.get())
			file.close()
			self.after(self.master, self.to_clear)
			global nick
			nick = self.nick.get()
			print nick
		else:
			self.uEntry['bg'] = 'red'
			self.pEntry['bg'] = 'red'
			self.nEntry['bg'] = 'red'


class show_online:

	def __init__(self, master):
		for widget in master.winfo_children():
			widget.destroy()
		self.master = master
		self.friends = []
		self.friendsList = Listbox(self.master)
		self.friendsList.pack()
		self.list_friends()
		self.update_friends()

	def update_friends(self):
		current_friends = comunicate({
			'action': 'online_users',
			'nick': nick
			})
		if self.friends != current_friends['online_users']:
			self.friends = current_friends['online_users']
			self.list_friends()
		self.to_kill = self.master.after(1000, self.update_friends)
	
	def list_friends(self):
		self.friendsList.delete(0, self.friendsList.size())
		for friend in self.friends:
			if friend != nick:
				self.friendsList.insert(END, friend)

	def suicide(self):
		self.master.after_cancel(self.to_kill)
		self.friendsList.destroy()


class show_rooms:

	def __init__(self, master, main_master):
		for widget in master.winfo_children():
			widget.destroy()
		self.main_master = main_master
		self.master = master
		self.rooms = []
		self.roomsList = Listbox(self.master)
		self.roomsList.pack()
		self.list_rooms()
		self.update_rooms()

	def update_rooms(self):
		current_rooms = comunicate({
			'action': 'show_rooms'
			})
		if self.rooms != current_rooms:
			self.rooms = current_rooms
			self.list_rooms()
		self.to_kill = self.master.after(1000, self.update_rooms)
	
	def join_room(self, event):
		self.host = self.roomsList.get(self.roomsList.curselection()[0]).split('/ ')[1]
		respond = comunicate({
			'action': 'join_room',
			'host': self.host,
			'login': nick
		})
		if respond['status']:
			clear(self.master)
			show_room(self.main_master, host = self.host)

	def list_rooms(self):
		self.roomsList.delete(0, self.roomsList.size())
		sizes = ['small', 'medium', 'big']
		for room in self.rooms:
			self.roomsList.insert(END, sizes[int(room['size'])] + ' / ' + room['host'])

			p = partial(self.join_room)
			self.roomsList.bind('<<ListboxSelect>>', p)

	def suicide(self):
		self.master.after_cancel(self.to_kill)
		self.roomsList.destroy()


class show_room:

	def __init__(self, master,  new=False, size=False, host='', first=True):
		self.first = first
		for widget in master.winfo_children():
			widget.destroy()
		self.game_status = False
		self.new = new
		self.host = host
		self.master = master
		if self.new:
			p = partial(comunicate, {
				'action': 'start_game',
				'host': nick
				})
			Button(self.master, text='Start', command=p).grid(column=2, row=1)
			self.size = size
			comunicate({
				'action': 'create_room',
				'nick': nick,
				'size': str(self.size)
				})
		self.bombs = []
		self.room_info = self.info()
		self.size = int(self.room_info['size'])
		self.exit_room_button = Button(self.master, text='exit room', command=self.exit_room)
		self.exit_room_button.grid(column=2, row=0)
		self.sizes = [
			[10, 10],
			[16, 16],
			[16, 30]
		]
		self.show_boards(True, True)

	def info(self):
		ret = comunicate({
				'action': 'show_room',
				'me': nick,
				'host': self.host
				})
		if 'users' in ret and nick in ret['users']:
			ret['users'].remove(nick)
		return ret

	def show_boards(self, first=False, boards=False):
		updated_info = self.info()
		if not updated_info['status']:
			self.exit_room()
			return
		if boards and (self.room_info != updated_info or first):
			self.users_index = {}
			self.room_info = updated_info
			self.size = int(self.room_info['size'])
			self.boards = []
			users_added = 0
			for i in range(4):
				self.boards.append({
					'Frame': Frame(
						self.master, 
						width = self.sizes[self.size][1]*20, 
						height = self.sizes[self.size][0]*20, 
						bg='gray'
						)
					})
				if i == 0:
					if self.game_status:
						self.boards[-1]['board'] = game(self.boards[-1]['Frame'], self.size, self.bombs, 'multi', True, nick, comunicate, self.host)
					else:
						self.boards[-1]['board'] = game(self.boards[-1]['Frame'], self.size, self.bombs, 'multi', False, nick)
				else:
					self.boards[-1]['board'] = game(self.boards[-1]['Frame'], self.size, self.bombs, 'multi', False)
					if i == 1 and self.new == False:
						self.users_index[self.room_info['host']] = len(self.boards) - 1
						self.boards[-1]['board'].nickLabel['text'] = self.room_info['host']				
					elif users_added < len(self.room_info['users']):
						self.users_index[self.room_info['users'][users_added]] = len(self.boards) - 1
						self.boards[-1]['board'].nickLabel['text'] = self.room_info['users'][users_added]
						users_added += 1

				self.boards[-1]['Frame'].grid(column = i%2, row = i/2, padx=2, pady=2)
		elif not boards and (self.room_info != updated_info or first):
			self.users_index = {}
			self.room_info = updated_info
			self.size = int(self.room_info['size'])
			users_added = 0
			for i in range(1, 4):
				if i == 1 and self.new == False:
					self.users_index[self.room_info['host']] = len(self.boards) - 1
					self.boards[i]['board'].nickLabel['text'] = self.room_info['host']				
				elif users_added < len(self.room_info['users']):
					self.users_index[self.room_info['users'][users_added]] = len(self.boards) - 1
					self.boards[i]['board'].nickLabel['text'] = self.room_info['users'][users_added]
					users_added += 1
				else:
					self.boards[i]['board'].nickLabel['text'] = ''

		if not self.game_status:
			if comunicate({'action': 'game_status', 'host': self.host})['game_status']:
				self.game_status = True
				self.bombs = comunicate({
					'action': 'show_game',
					'me': nick,
					'host': self.host
					})['bombs_map']
				self.show_boards(True, True)
				self.current_game = []
				self.update_board(True)
			else:
				self.to_kill = self.master.after(1000, self.show_boards)
	
	def update_board(self, first = False):
		save = comunicate({'action': 'show_game', 'me': nick, 'host': self.host})
		
		if first:
			self.current_game = save
			for i in save:
				if i != nick and i != 'bombs_map' and i != 'died':
					move = save[i][0]
					self.boards[self.users_index[i]]['board'].update_grid(move[0], move[1], move[2])
				elif i == nick:
					move = save[i][0]
					self.boards[0]['board'].update_grid(move[0], move[1], move[2])

		if not 'bombs_map' in save and not self.info()['status']:
			self.exit_room()
			return

		elif not 'bombs_map' in save and self.info()['status']:
			self.show_boards(True, True)
			return

		elif self.bombs != save['bombs_map']:
			self.game_status = False
			self.current_game = []
			self.show_boards(True)
			return

		if self.current_game != save:
			for i in save:
				if i != nick and i != 'bombs_map' and i != 'died':
					for move in save[i][len(self.current_game[i]):]:
						self.boards[self.users_index[i]]['board'].update_grid(move[0], move[1], move[2])
			self.current_game = save

		self.to_kill = self.master.after(500, self.update_board)

	def exit_room(self):
		self.master.after_cancel(self.to_kill)
		comunicate({
			'action': 'exit_room',
			'nick': nick
			})
		main_menu(self.master)

class main_menu:

	def __init__(self, master, to_clear = []):

		for widget in master.winfo_children():
			widget.destroy()
		for widget in to_clear:
			widget.destroy()

		self.master = master
		Label(self.master, text = 'Rooms', fg = 'blue').grid(column = 1, row = 0)
		Label(self.master, text = 'Online Users', fg = 'green').grid(column = 2, row = 0)
		
		roomsFrame = Frame(self.master)
		rooms_class = show_rooms(roomsFrame, self.master)
		roomsFrame.grid(column = 1, row = 1)

		friendsFrame = Frame(self.master)
		friends_class = show_online(friendsFrame)
		friendsFrame.grid(column = 2, row = 1)

		self.CheckVars = [IntVar() for i in range(3)]
		self.C, self.sizes = [], ['small', 'medium', 'big']
		self.checkFrame = Frame(self.master)
		self.checkFrame.grid(column=0, row=1, sticky=N)
		for idx, i in enumerate(self.sizes):
			f = partial(self.deselect, idx)
			self.C.append(Checkbutton(self.checkFrame, text=i, variable = self.CheckVars[idx],
								command = f, onvalue = 1, offvalue = 0))
			self.C[idx].pack(side=LEFT)
		self.C[2].select()
		Button(self.master, text = 'Create Room', 
			command = lambda: show_room(self.master, 
				True, 
				[i for i in range(len(self.CheckVars)) if self.CheckVars[i].get() == 1][0],
				nick
				)
			).grid(column = 0, row = 0)

	def deselect(self, x):
		for i in range(3):
			if i != x:
				self.C[i].deselect()
		if not any([self.CheckVars[i].get() for i in range(3)]):
			self.C[x].select()