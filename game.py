import random
from copy import deepcopy
from Tkinter import *
from functools import partial

root = Tk()
root.option_add('*font', ('verdana', 12, 'bold'))
root.title("Saper")

class game:


	flag         = PhotoImage(file='data/flag.png')
	not_clicked  = PhotoImage(file='data/not_clicked.png')
	clicked_bomb = PhotoImage(file='data/clicked_bomb.png')
	flagged_bomb = PhotoImage(file='data/flagged_bomb.png')

	around_image = []
	for i in range(0, 9):
		around_image.append(PhotoImage(file='data/' + str(i) + '.png'))

	def __init__(self, master, size, bombs_map, mode):
		self.master = master
		self.mode = mode
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

	def update_time(self):
		print 'here'
		if self.status == 'playing':
			print self.playing_time
			self.playing_time += 1
			self.time['text'] = self.playing_time
			self.master.after(1000, self.update_time)

	def bar(self):
		self.bottomFrame = Frame(self.master)
		self.bottomFrame.pack(side = BOTTOM)
		f = ('verdana', 15, 'bold')
		self.bombs_to_find = Label(self.master, text=str(self.flags), bg='black', fg='red', width=2, height=1, font=f)
		self.bombs_to_find.pack(side = LEFT, pady=4, padx=8)
		self.playing_time = -1
		self.time = Label(self.master, text='0', bg='black', fg='red', width=2, height=1, font=f)
		self.time.pack(side = RIGHT, pady=4, padx=8)

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
		h = 30*self.dimensions[0]
		w = 30*self.dimensions[1]
		game_frame = Frame(self.bottomFrame, height = h, width = w)
		#game_frame.grid(column = 0, row = 1)
		game_frame.pack(side = BOTTOM)
		self.places = [
		[Label(game_frame, image=game.not_clicked, width=30, height=30) 
		for i in range(self.dimensions[1])] 
		for j in range(self.dimensions[0])
		]
		for y in range(self.dimensions[0]):
			for x in range(self.dimensions[1]):
				left_click = partial(self.update_grid, y, x, 1)
				right_click = partial(self.update_grid, y, x, 2)
				self.places[y][x].bind("<Button-1>", left_click)
				self.places[y][x].bind("<Button-3>", right_click)
				self.places[y][x].grid(row=y, column=x)

	def show_grid(self, h, w):
		value = self.grid[h][w]
		if value == 0:
			self.places[h][w]['image'] = game.not_clicked
		elif value == 1:
			self.places[h][w]['image'] = game.flag
			self.places[h][w].unbind("<Button-1>")
		elif value == 2:
			self.places[h][w]['image'] = game.clicked_bomb
		elif value >= 10:
			self.places[h][w]['image'] = game.around_image[value - 10]
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

	def update_grid(self, h, w, move, event):
		if self.status == 'playing':
			if move == 1:
				if self.bombs_map[h][w] == 0 and self.grid[h][w] == 0:
					self.found += 1
					if self.found == 1:
						self.update_time()
					if self.found == self.to_find:
						self.status = 'win'
					around_this = self.bombs_around(h, w)
					self.grid[h][w] = 10 + around_this[0]
					self.show_grid(h, w)
					if around_this[0] == 0:
						for i in around_this[1]:
							self.update_grid(i[0], i[1], 1, event)
				elif self.grid[h][w] > 10:
					print self.flags_around(h, w)[0] == self.grid[h][w] - 10
					if self.flags_around(h, w)[0] == self.grid[h][w] - 10:
						print h, w
						for i in self.flags_around(h, w)[1]:
							print i
							self.update_grid(i[0], i[1], 1, event)

				elif self.bombs_map[h][w] == 1:
					self.status = 'lose'
					self.grid[h][w] = 2
					self.show_grid(h, w)
					#self.suicide()
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
		self.master.destroy()


cos1 = Frame(root, bd=10)
second = game(cos1, 2, [], 'single')
cos1.grid(row=0, column=0, padx=10, pady=5)
root.mainloop()