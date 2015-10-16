import tkinter as tk
import os

import main_gui

os.chdir('..')

if __name__ == '__main__':
    root = tk.Tk()
    my_application = main_gui.SeparateWindowFile(root)
    my_application.pack(fill='both', expand=True)
    my_application.mainloop()