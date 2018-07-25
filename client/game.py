import random
from Tkinter import *
from copy import deepcopy
from functools import partial
from thread import start_new_thread


class game:

	def __init__(self, master, size, bombs_map, mode, me=False, nick='', multi_func='', host=''):

		self.mode = mode
		file_type = 'jpg'
		if self.mode == 'single':
			self.image_size = 30
			source = 'data/images/' + file_type + '/30'
		else:
			self.multi_func = multi_func
			self.host = host
			self.image_size = 20
			source = 'data/images/' + file_type + '/20'
		self.flag = PhotoImage(file=source + '/flag.' + file_type)
		self.not_clicked = PhotoImage(file=source + '/not_clicked.' + file_type)
		self.clicked_bomb = PhotoImage(file=source + '/clicked_bomb.' + file_type)
		self.flagged_bomb = PhotoImage(file=source + '/flagged_bomb.' + file_type)
		self.around_image = []
		for i in range(0, 9):
			self.around_image.append(PhotoImage(file=source + '/' + str(i) + '.' + file_type))
		self.nick = nick
		self.me = me
		self.master = master
		self.size = size
		self.status = 'playing'
		self.create_dimensions()
		self.flags = self.bombs
		self.bar()
		self.to_find = self.dimensions[0] * self.dimensions[1] - self.bombs
		self.found = 0
		self.grid = [
				[0 for j in range(self.dimensions[1])]
				for i in range(self.dimensions[0])
			]
		if not bombs_map:
			self.random_bombs()
		else:
			self.bombs_map = bombs_map
		self.create_grid()

	def update_stats(self, size, result='0', t='0'):
		file = open('data/stats', 'a+')
		file.write(str(size) + ' ' + str(result) + ' ' + str(t) + '\n')
		file.close()

	def update_time(self):
		if self.status == 'playing':
			self.playing_time += 1
			self.time['text'] = self.playing_time
			self.after = self.master.after(1000, self.update_time)

	def remake(self):
		self.suicide()
		self.__init__(self.master, self.size, False, self.mode)

	def bar(self):
		self.bottomFrame = Frame(self.master)
		self.bottomFrame.pack(side = BOTTOM)
		f = ('verdana', 8, 'bold')
		self.bombs_to_find = Label(self.master, text=str(self.flags), bg='black', fg='red', width=3, font=f)
		self.bombs_to_find.pack(side = LEFT)
		if self.mode == 'single':
			self.remake_button = Button(self.master, text='Remake', command=self.remake)
			self.remake_button.pack(side = LEFT, padx=self.dimensions[1]/2*self.image_size-90)
		else:
			self.nickLabel = Label(self.master, text=self.nick)
			self.nickLabel.pack(side = LEFT, padx=self.dimensions[1]/2*self.image_size-90)
		self.playing_time = 0
		self.time = Label(self.master, text='0', bg='black', fg='red', width=3, font=f)
		self.time.pack(side = RIGHT)

	def random_bombs(self):
		self.bombs_map = deepcopy(self.grid)
		bombs_locations = random.sample(xrange(self.dimensions[0]*self.dimensions[1]), self.bombs)
		for i in bombs_locations:
			self.bombs_map[i/(self.dimensions[1])][i%(self.dimensions[1])] = 1

	def create_dimensions(self):
		sizes = [
			[10, 10, 10],
			[16, 16, 40],
			[16, 30, 99]
		]
		self.bombs = sizes[self.size][2]
		self.dimensions = sizes[self.size][:-1]

	def create_grid(self):
		h = self.image_size*self.dimensions[0]
		w = self.image_size*self.dimensions[1]
		game_frame = Frame(self.bottomFrame, height = h, width = w)
		game_frame.pack(side = BOTTOM)
		self.places = [
		[Label(game_frame, image=self.not_clicked, width=self.image_size, height=self.image_size) 
		for i in range(self.dimensions[1])] 
		for j in range(self.dimensions[0])
		]
		for y in range(self.dimensions[0]):
			for x in range(self.dimensions[1]):
				self.places[y][x].grid(row=y, column=x)
				left_click = partial(self.update_grid, y, x, 1)
				right_click = partial(self.update_grid, y, x, 2)
				self.places[y][x].bind("<Button-1>", left_click)
				self.places[y][x].bind("<Button-3>", right_click)
				if self.mode == 'multi' and self.me == False:
					self.places[y][x].unbind("<Button-1>")
					self.places[y][x].unbind("<Button-3>")

	def show_grid(self, h, w):
		value = self.grid[h][w]
		if value == 0:
			self.places[h][w]['image'] = self.not_clicked
			left_click = partial(self.update_grid, h, w, 1)
			right_click = partial(self.update_grid, h, w, 2)
			self.places[h][w].bind("<Button-1>", left_click)
			self.places[h][w].bind("<Button-3>", right_click)
		elif value == 1:
			self.places[h][w]['image'] = self.flag
			self.places[h][w].unbind("<Button-1>")
		elif value == 2:
			self.places[h][w]['image'] = self.clicked_bomb
		elif value >= 10:
			self.places[h][w]['image'] = self.around_image[value - 10]
			self.places[h][w].unbind("<Button-3>")

	def bombs_around(self, h, w):
		to_check = [
			[i, j]
			for i in range(h-1, h+2) 
			for j in range(w-1, w+2) 
			if 
			0 <= i < self.dimensions[0] and 
			0 <= j < self.dimensions[1] and
			not (i == h and j == w) and
			(self.grid[i][j] == 0 or
			self.grid[i][j] == 1)
		]
		amount_of_bombs = 0
		for i in to_check:
			if self.bombs_map[i[0]][i[1]] == 1:
				amount_of_bombs += 1
		return [amount_of_bombs, to_check]

	def flags_around(self, h, w):
		ret, ret_check = 0, []
		to_check = [
			[i, j]
			for i in range(h-1, h+2) 
			for j in range(w-1, w+2) 
			if 
			0 <= i < self.dimensions[0] and 
			0 <= j < self.dimensions[1] and
			not (i == h and j == w)
		]
		for i in to_check:
			if self.grid[i[0]][i[1]] == 1:
				ret += 1
			elif self.grid[i[0]][i[1]] == 0:
				ret_check.append(i)
		return [ret, ret_check]

	def update_grid(self, h, w, move, event=''):
		if self.status == 'playing':
			if not event == 'rec' and self.mode == 'multi' and self.me == True:
				start_new_thread(self.multi_func, ({
					'action': 'game_move',
					'me': self.nick,
					'host': self.host,
					'move': [h, w, move]
					}, ))

			if move == 1:
				if self.bombs_map[h][w] == 0 and self.grid[h][w] == 0:
					self.found += 1
					if self.found == 1:
						self.after = self.master.after(1000, self.update_time)
					if self.found == self.to_find:
						if self.mode == 'multi' and self.me == True:
							start_new_thread(self.multi_func, ({
								'action': 'game_move',
								'action2': True,
								'me': self.nick,
								'host': self.host,
								'move': [h, w, move]
								}, ))
						self.status = 'win'
						self.update_stats(str(self.size), '1', str(self.playing_time))
					around_this = self.bombs_around(h, w)
					self.grid[h][w] = 10 + around_this[0]
					self.show_grid(h, w)
					if around_this[0] == 0:
						for i in around_this[1]:
							self.update_grid(i[0], i[1], 1, 'rec')
				elif self.grid[h][w] > 10:
					if self.flags_around(h, w)[0] == self.grid[h][w] - 10:
						for i in self.flags_around(h, w)[1]:
							self.update_grid(i[0], i[1], 1, 'rec')

				elif self.bombs_map[h][w] == 1:
					if self.mode == 'multi' and self.me == True:
						start_new_thread(self.multi_func, ({
							'action': 'game_move',
							'action2': True,
							'me': self.nick,
							'host': self.host,
							'move': [h, w, move]
							} ,))
					self.status = 'lose'
					self.update_stats(str(self.size))
					self.grid[h][w] = 2
					self.show_grid(h, w)
					if self.mode == 'single':
						self.suicide()
						self.__init__(self.master, self.size, False, self.mode)
			elif move == 2:
				if self.grid[h][w] == 1:
					self.flags += 1
					self.bombs_to_find['text'] = str(self.flags)
					self.grid[h][w] = 0
				else:
					self.flags -= 1
					self.bombs_to_find['text'] = str(self.flags)
					self.grid[h][w] = 1
				self.show_grid(h, w)

	def suicide(self):
		for i in range(len(self.places)):
			for j in range(len(self.places[i])):
				self.places[len(self.places) - i - 1][i - j - 1].destroy()
		self.time.destroy()
		self.bombs_to_find.destroy()
		self.remake_button.destroy()
		try:
			self.master.after_cancel(self.after)
		except:
			pass