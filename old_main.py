import tkinter as tk
import os

import alternate_gui

os.chdir('..')

if __name__ == '__main__':
    root = tk.Tk()
    my_application = alternate_gui.Application(root)
    my_application.pack(fill='both', expand=True)
    my_application.mainloop()