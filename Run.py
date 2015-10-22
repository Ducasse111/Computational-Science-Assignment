import tkinter as tk
import os

import GUI

os.chdir('..')

if __name__ == '__main__':
    root = tk.Tk()
    my_application = GUI.Application(root)
    my_application.pack(fill='both', expand=True)
    my_application.mainloop()