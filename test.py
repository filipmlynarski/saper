import time
from Tkinter import *
from multiprocessing import Process

root = Tk()

def test(x):
	cos = 0
	while True:
		cos += 2
		print cos
		glob['text'] = str(cos)
		time.sleep(1)

p = Process(target = test, args = ('usuless', ))
print '?'
glob = Label(root, text='0')
glob.pack()
p.start()
root.mainloop()
print '?'
p.join()