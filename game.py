from Tkinter import *
from functools import partial

root = Tk()


class game:


	flag         = PhotoImage(file='data/flag.png')
	not_clicked  = PhotoImage(file='data/not_clicked.png')
	clicked_bomb = PhotoImage(file='data/clicked_bomb.png')
	flagged_bomb = PhotoImage(file='data/flagged_bomb.png')

	around_image = []
	for i in range(0, 9):
		around_image.append(PhotoImage(file='data/' + str(i) + '.png'))

	def __init__(self, master, size, bombs_map, mode, grid_c ,grid_w):
		self.master = master
		self.grid_c = grid_c
		self.grid_w = grid_w
		self.mode = mode
		self.size = size
		self.bombs_map = bombs_map
		self.status = 'playing'
		self.create_dimensions()
		self.grid = [
				[0 for j in range(self.dimensions[1])]
				for i in range(self.dimensions[0])
			]
		self.create_grid()

	def create_dimensions(self):
		sizes = [
			[10, 10],
			[16, 16],
			[16, 30]
		]
		self.dimensions = sizes[self.size]

	def create_grid(self):
		h = 30*self.dimensions[0]
		w = 30*self.dimensions[1]
		game_frame = Frame(self.master, height = h, width = w)
		game_frame.grid(column = self.grid_c, row = self.grid_w)
		places = [
		[Label(game_frame, image=game.not_clicked, width=30, height=30) 
		for i in range(self.dimensions[1])] 
		for j in range(self.dimensions[0])
		]
		for y in range(self.dimensions[0]):
			for x in range(self.dimensions[1]):
				left_click = partial(self.update_grid, y, x, 1)
				right_click = partial(self.update_grid, y, x, 2)
				places[y][x].bind("<Button-1>", left_click)
				places[y][x].bind("<Button-3>", right_click)
				places[y][x].grid(row=y, column=x)

	def show_grid(self, h, w):
		if self.grid[h, w] == 0:
			'hmmm'

	def bombs_around(self, h, w):
		to_check = [
			[i, j]
			for i in range(h-1, h+2) 
			for j in range(w-1, w+2) 
			if 
			0 <= i < len(current_grid) and 
			0 <= j < len(current_grid[0]) and
			(i != h and j != w)
		]
		amount_of_bombs = 0
		for i in to_check:
			if self.bombs_map[i[0], i[1]] == 1:
				ret += 1
		return [amount_of_bombs, to_check]

	def update_grid(self, h, w, move, event):
		print move
		if move == 1:
			if bombs_map[h, w] == 0:
				around_this = bombs_around(h, w)
				self.grid[h, w] = 10 + around_this
				if around_this[0] == 0:
					for i in around_this[1]:
						update_grid(i[0], i[1], 1)
				show_grid(h, w)

			elif bombs_map[h, w] == 1:
				self.status = 'lose'

single = game(root, 2, [], 'single', 0, 0)
root.mainloop()