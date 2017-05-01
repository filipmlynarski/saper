from Tkinter import *

root = Tk()
root.title('Timer')

sec = 0

def tick():
    global sec
    sec += 1
    time['text'] = sec
    # Take advantage of the after method of the Label
    time.after(1000, tick)

time = Label(root, fg='green')
time.pack()
tick()

root.mainloop()