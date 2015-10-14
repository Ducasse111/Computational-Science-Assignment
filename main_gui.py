import io
import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageTk

import graphing_api as graphing_api


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.selected_file = None
        self.selected_trial = None
        self.raw_image = None
        self.cur_image = None
        self.image = None
        self.master.title('Tkinter GUI Rewrite')
        self.grid()
        self.active_files = []
        self.matlab_opened_files = {}
        self.listbox_data = {}
        self.refresh_rate = 100
        self.still_resizing = False

        self.bind('<Configure>', self.on_resize)

        '''------------------
        Widget Instantiations
        ------------------'''

        #####################################################
        # Drop-down Menu
        #####################################################

        self.menu = tk.Menu(self.master)

        try:
            self.master.config(menu=self.menu)
        except AttributeError:
            # master is a top-level window (Python 1.4/Tkinter 1.63)
            self.master.tk.call(master, "config", "-menu", self.menu)

        # File Cascade
        self.file_menu = tk.Menu(self.menu, tearoff=False)
        self.file_menu.add_command(label='Browse', command=self.browse_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', command=self.quit)

        self.menu.add_cascade(label='File', menu=self.file_menu)

        # View Cascade
        self.view_menu = tk.Menu(self.menu, tearoff=False)
        self.view_menu.add_command(label='Placeholder', command=None)

        self.menu.add_cascade(label='View', menu=self.view_menu)

        # Help Cascade
        self.help_menu = tk.Menu(self.menu, tearoff=False)
        self.help_menu.add_command(label='About', command=None)

        self.menu.add_cascade(label='Help', menu=self.help_menu)

        #####################################################
        # Scrollbar/File Viewer
        #####################################################

        self.file_viewer = tk.Scrollbar(self)
        self.trials = tk.Scrollbar(self)

        self.trial_listbox = tk.Listbox(self, yscrollcommand=self.trials.set, width=5, selectmode='single')
        self.list_of_open_files = tk.Listbox(self, yscrollcommand=self.file_viewer.set, width=20, selectmode='single')

        self.trial_listbox.bind('<Double-Button-1>', self.base_gui_plot_trial)
        self.list_of_open_files.bind('<Double-Button-1>', self.listbox_element_selected)

        #####################################################
        # Text Widget
        #####################################################

        self.trial_text = tk.Label(self, text='Number of Trials: ')

        #####################################################
        # Base Image Viewer
        #####################################################

        self.image_panel = tk.Canvas(self, height=480, width=720, bg='white')

        #####################################################
        # Widget Element Configuration
        #####################################################

        # Grid instantiations

        self.list_of_open_files.grid(row=0, rowspan=2, column=0, sticky='ns')
        self.file_viewer.grid(row=0,        rowspan=2, column=1, sticky='ns')
        self.trial_listbox.grid(row=0,      rowspan=2, column=2, sticky='ns')
        self.trials.grid(row=0,             rowspan=2, column=3, sticky='ns')
        self.trial_text.grid(row=0,                    column=4, sticky='we')
        self.image_panel.grid(row=1,                   column=4, sticky='nsew')

        # Widget sticky and weighting

        # self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.columnconfigure(4, weight=1)

        # Widget configurations
        self.file_viewer.config(command=self.list_of_open_files.yview)
        self.trials.config(command=self.trial_listbox.yview)

    # Finished : Working
    def browse_file(self):
        files = filedialog.askopenfilenames()

        # Add files to a list of opened files and update the scrollbar
        for selected_file in files:
            if selected_file not in self.active_files:
                self.active_files.append(selected_file)

                filename = selected_file.split('/')
                filename = filename[-1]

                self.list_of_open_files.insert('end', filename)
                self.listbox_data[filename] = selected_file
        return

    # Finished : Working
    def listbox_element_selected(self, event):
        widget = event.widget
        self.selected_file = widget.get(widget.curselection())
        bin = [x for x in self.matlab_opened_files.keys()]
        for rubbish in bin:
            del self.matlab_opened_files[rubbish]
        self.matlab_opened_files[self.selected_file] = graphing_api.GraphingApplication()
        if self.selected_file is not None:
            self.quick_load_file(self.matlab_opened_files[self.selected_file])

    # Finished : Working
    def quick_load_file(self, graphing_object):
        graphing_object.open_file(self.listbox_data[self.selected_file])
        self.trial_text.configure(text='Number of trials: ' + str(graphing_object.number_trials))
        self.trial_listbox.delete(0, self.trial_listbox.size())
        for x in range(graphing_object.number_trials):
            self.trial_listbox.insert('end', str(x+1))

    # Unfinished
    def base_gui_plot_trial(self, event):
        widget = event.widget
        self.selected_trial = widget.get(widget.curselection())
        self.raw_image = Image.open(io.BytesIO(self.matlab_opened_files[self.selected_file].get_graph(self.selected_trial)))
        self.cur_image = self.raw_image.resize((self.image_panel.winfo_width(), self.image_panel.winfo_height()), Image.ANTIALIAS)

        self.image = ImageTk.PhotoImage(self.cur_image)
        self.image_panel.image = self.image
        self.image_panel.create_image(0, 0, anchor='nw', image=self.image)

    def refresh(self):
        if self.raw_image is not None:
            width, height = self.cur_image.size
            if width != self.image_panel.winfo_width() or height != self.image_panel.winfo_height():
                self.cur_image = self.raw_image.resize((self.image_panel.winfo_width(), self.image_panel.winfo_height()), Image.ANTIALIAS)
                self.image = ImageTk.PhotoImage(self.raw_image)

                self.image_panel.image = self.image
                self.image_panel.itemconfigure(self.image_panel, image=self.image)

                self.after(100, self.refresh)
                self.bind('<Configure>', None)
            else:
                self.bind('<Configure>', self.on_resize)

    # Unfinished
    def on_resize(self, event):
        self.still_resizing = True

    # Unfinished
    def new_image_window(self, image_data_as_bytes):
        pass

    # Unfinished
    def new_file_window(self, file):
        pass

    @staticmethod
    def edit_text(textbox, text):
        textbox.configure(state='normal')
        textbox.insert("1.0", text)
        textbox.configure(state='disabled')