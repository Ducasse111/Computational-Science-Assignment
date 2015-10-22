import tkinter as tk
import os
import alternate_gui

os.chdir('..')

file_string = 'C:/Users/Jona/PycharmProjects/Computational Science Assignment/Computational-Science-Assignment/Data_Input/654508_rec02.mat'

if __name__ == '__main__':
    root = tk.Tk()
    # my_application = alternate_gui.NewWindow(process_type='1', file=file_string, trial=1)
    # my_application = alternate_gui.NewWindow(process_type='0')
    # my_application = alternate_gui.SeparateWindowFile(root)
    # my_application.start()
    my_application = alternate_gui.Application(root)
    # my_application = alternate_gui.AnalysisWindow(master=root, trial='1',
    #                                             file=file_string)
    my_application.pack(fill='both', expand=True)
    my_application.mainloop()