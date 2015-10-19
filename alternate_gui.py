import io
import sys

import tkinter as tk
import scipy.io as sc_io
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk

from PIL import Image, ImageTk

import graphing_api
from multiprocessing import Process

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import time

__Version__ = "0.4.0"
# Edit this whenever you make a change, help us keep track.
#           for a.b.c
#           we change a when we finish a complete feature
#           we change b when we add a new feature
#           we change c when whenever we do a small fix


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.selected_file = None
        self.selected_trial = None
        self.highlighted = None
        self.new_window = None
        self.file = None
        self.master.title('Tkinter GUI Rewrite V' + __Version__)
        self.grid()
        self.active_files = []
        self.opened_files = {}
        self.listbox_data = {}

        # graphing api
        self.number_trials = 0

        self.stimuli_time = []
        self.stimuli_code = []
        self.firing = []
        self.trialled_firing = []

        self.dictionary = {}
        self.mat = {}

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
        self.file_menu.add_command(label='Settings...', command=None)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', command=self.quit)

        self.menu.add_cascade(label='File', menu=self.file_menu)

        # View Cascade
        self.view_menu = tk.Menu(self.menu, tearoff=False)
        self.view_menu.add_command(label='Placeholder', command=None)

        self.menu.add_cascade(label='View', menu=self.view_menu)

        # Help Cascade
        def display_about():
            text = "Created by:\n" \
                   "Ben Witney\n" \
                   "Martin Tran\n" \
                   "Jeffrey Vo\n" \
                   "Jay Requizo\n" \
                   "Aaron Jia\n" \
                   "\n" \
                   "In Co-operation With:\n" \
                   "John Monash Science School" \
                   "\n" \
                   "\n" \
                   "Version: "
            messagebox.showinfo(message=text + __Version__, title='About', icon='info')

        self.help_menu = tk.Menu(self.menu, tearoff=False)
        self.help_menu.add_command(label='About', command=display_about)

        self.menu.add_cascade(label='Help', menu=self.help_menu)

        #####################################################
        # Scrollbar/File Viewer
        #####################################################

        self.file_viewer = tk.Scrollbar(self)
        self.trials = tk.Scrollbar(self)

        self.trial_listbox = tk.Listbox(self, yscrollcommand=self.trials.set, width=6, activestyle='none',
                                        selectmode='single', exportselection=False, highlightthickness=0)
        self.list_of_open_files = tk.Listbox(self, yscrollcommand=self.file_viewer.set, activestyle='none',
                                             width=24, selectmode='single', exportselection=False, highlightthickness=0)

        self.trial_listbox.bind('<Double-1>', self.base_gui_plot_trial)
        self.list_of_open_files.bind('<Double-1>', self.listbox_element_selected)
        self.list_of_open_files.bind('<<ListboxSelect>>', self.set_active)

        #####################################################
        # Scrollbar Toolbar
        #####################################################

        self.scrollbar_toolbar = tk.Frame(self)
        if sys.platform == ("win32" or "cygwin"):
            self.icon = 'icons\\'

        elif sys.platform == "darwin":
            self.icon = 'icons/'

        self.i_size = (14, 14)

        self.browse_image = Image.open(self.icon+'open.ico')
        self.browse_image = self.browse_image.resize(self.i_size, Image.ANTIALIAS)

        self.delete_image = Image.open(self.icon+'delete.png')
        self.delete_image = self.delete_image.resize(self.i_size, Image.ANTIALIAS)

        self.up_image = Image.open(self.icon+'up.png')
        self.up_image = self.up_image.resize(self.i_size, Image.ANTIALIAS)

        self.down_image = Image.open(self.icon+'down.png')
        self.down_image = self.down_image.resize(self.i_size, Image.ANTIALIAS)

        self.window_open_image = Image.open(self.icon+'window_add.png')
        self.window_open_image = self.window_open_image.resize(self.i_size, Image.ANTIALIAS)

        self.tk_browse_image = ImageTk.PhotoImage(self.browse_image)
        self.tk_delete_image = ImageTk.PhotoImage(self.delete_image)
        self.tk_up_image = ImageTk.PhotoImage(self.up_image)
        self.tk_down_image = ImageTk.PhotoImage(self.down_image)
        self.tk_window_open = ImageTk.PhotoImage(self.window_open_image)

        self.delete_file_button = tk.Button(self.scrollbar_toolbar, image=self.tk_delete_image,
                                            command=self.unload_selected, relief='flat', padx=2, pady=2,
                                            overrelief='groove', anchor='center')

        self.up_button = tk.Button(self.scrollbar_toolbar, image=self.tk_up_image,
                                   command=self.move_element_up, relief='flat', padx=2, pady=2,
                                   overrelief='groove', anchor='center')

        self.down_button = tk.Button(self.scrollbar_toolbar, image=self.tk_down_image,
                                     command=self.move_element_down, relief='flat', padx=2, pady=2,
                                     overrelief='groove', anchor='center')

        self.window_open_button = tk.Button(self.scrollbar_toolbar, image=self.tk_window_open,
                                            command=self.new_file_window, relief='flat', padx=2, pady=2,
                                            overrelief='groove', anchor='center')

        self.browse_file_button = tk.Button(self.scrollbar_toolbar, image=self.tk_browse_image,
                                            command=self.browse_file, relief='flat', padx=2, pady=2,
                                            overrelief='groove', anchor='center')

        ttk.Separator(self.scrollbar_toolbar, orient='vertical').pack(side='left', fill='y', padx=2)
        self.browse_file_button.pack(side='left')
        self.delete_file_button.pack(side='left')
        ttk.Separator(self.scrollbar_toolbar, orient='vertical').pack(side='left', fill='y', padx=2)
        self.up_button.pack(side='left')
        self.down_button.pack(side='left')
        self.window_open_button.pack(side='left')
        ttk.Separator(self.scrollbar_toolbar, orient='vertical').pack(side='right', fill='y', padx=1)

        #####################################################
        # Text Widget
        #####################################################

        self.trial_text = tk.Label(self, text='Number of Trials: ', width=40, anchor='w', relief='groove')
        self.file_text = tk.Label(self, text='Selected File: ', width=40, anchor='w', relief='groove')
        self.display_trial_text = tk.Label(self, text='Graphed Trial: ', width=40, anchor='w', relief='groove')

        #####################################################
        # Base Image Viewer
        #####################################################

        self.figure = Figure(figsize=(9, 6), dpi=100)
        # self.a = self.figure.add_subplot(111)
        self.image_panel = FigureCanvasTkAgg(self.figure, self)

        #####################################################
        # Widget Element Configuration
        #####################################################

        # Grid instantiations

        self.scrollbar_toolbar.grid(row=0,             column=0, sticky='ew')
        self.list_of_open_files.grid(row=1, rowspan=2, column=0, sticky='ns', padx=1, pady=1)
        self.file_viewer.grid(row=1,        rowspan=2, column=1, sticky='ns', padx=1, pady=1)
        self.trial_listbox.grid(row=1,      rowspan=2, column=2, sticky='ns', padx=1, pady=1)
        self.trials.grid(row=1,             rowspan=2, column=3, sticky='ns', padx=1, pady=1)
        self.file_text.grid(row=0,                     column=4, sticky='nsw', padx=2, pady=1)
        self.trial_text.grid(row=0,                    column=5, sticky='nsew', padx=2, pady=1)
        self.display_trial_text.grid(row=0,                    column=6, sticky='nsew', padx=2, pady=1)
        self.image_panel.get_tk_widget().grid(row=1,     columnspan=3, column=4, sticky='nsew')

        # Widget sticky and weighting

        self.rowconfigure(1, weight=2)
        self.columnconfigure(6, weight=1)

        # Widget configurations)

        self.file_viewer.config(command=self.list_of_open_files.yview)
        self.trials.config(command=self.trial_listbox.yview)

    # Finished : Working
    def browse_file(self):
        files = filedialog.askopenfilenames(filetypes=(('MatLab Files', '*.mat'),))

        # Add files to a list of opened files and update the scrollbar
        for selected_file in files:
            if selected_file not in self.active_files:
                name, extension = selected_file.split('.')
                if extension == 'mat':
                    self.active_files.append(selected_file)

                    filename = selected_file.split('/')
                    filename = filename[-1]

                    self.list_of_open_files.insert('end', filename)
                    self.listbox_data[filename] = selected_file

    #  Finished : Working
    def move_element_up(self):
        try:
            selected = self.list_of_open_files.curselection()[0]
            if selected != 0:
                file = self.list_of_open_files.get(selected)
                self.list_of_open_files.delete(selected)
                self.list_of_open_files.insert(selected-1, file)
                self.list_of_open_files.selection_clear(selected-1)
                self.list_of_open_files.selection_set(selected-1)
                self.active_files.insert(selected-1, self.active_files[selected])
        except IndexError:
            pass

    #  Finished : Working
    def move_element_down(self):
        try:
            selected = self.list_of_open_files.curselection()[0]
            if selected != self.list_of_open_files.size():
                file = self.list_of_open_files.get(selected)
                self.list_of_open_files.delete(selected)
                self.list_of_open_files.insert(selected+1, file)
                self.list_of_open_files.selection_clear(0, self.list_of_open_files.size())
                self.list_of_open_files.selection_set(selected+1)
                self.active_files.insert(selected+1, self.active_files[selected])
        except IndexError:
            pass

    # Finished : Working
    def listbox_element_selected(self, event):
        self.selected_file = self.list_of_open_files.get(self.list_of_open_files.curselection())
        self.file = self.listbox_data[self.selected_file]
        self.file_text.configure(text='Selected File: ' + str(self.selected_file))

        trashcan = []
        for keys in self.opened_files.keys():
            trashcan.append(keys)

        for rubbish in trashcan:
            del self.opened_files[rubbish]
        if self.selected_file is not None:
            self.quick_load_file(self.selected_file)

    # Finished : Working
    def quick_load_file(self, file):
        temp = graphing_api.GraphingApplication()
        temp.open_file(self.listbox_data[file])
        self.trial_text.configure(text='Number of Trials: ' + str(temp.number_trials))
        self.trial_listbox.delete(0, self.trial_listbox.size())
        for x in range(temp.number_trials):
            self.trial_listbox.insert('end', str(x+1))
        del temp

    # Finished : Working
    def base_gui_plot_trial(self, event):
        widget = event.widget
        self.selected_trial = widget.get(widget.curselection())
        self.display_trial_text.configure(text='Graphed Trial: ' + str(self.selected_trial))

        self.image_panel.get_tk_widget().delete('all')
        self.image_panel.get_tk_widget().grid_remove()

        self.tk.call(self.image_panel.get_tk_widget(), 'delete', 1, 1)
        del self.figure
        del self.image_panel

        self.figure = Figure(figsize=(9, 6), dpi=100)
        self.image_panel = FigureCanvasTkAgg(self.figure, self)
        self.a = self.figure.add_subplot(111)

        if self.selected_trial is not None:

            try:
                self.mat[str(self.file) + " " + str(self.selected_trial)] = sc_io.loadmat(self.file, appendmat=True)
            except Exception as e:
                try:
                    self.mat[str(self.file) + " " + str(self.selected_trial)] = sc_io.loadmat(self.file, appendmat=True)
                except FileNotFoundError:
                    print("File not found: ", e)

            temp_var = sc_io.whosmat(self.file)[0][0]

            for x in self.mat[str(self.file) + " " + str(self.selected_trial)]['StimTrig'][0][0][4]:
                self.stimuli_time.append(x[0])
            for x in self.mat[str(self.file) + " " + str(self.selected_trial)]['StimTrig'][0][0][5]:
                if x[0] != 62:
                    self.stimuli_code.append(x[0])
                else:
                    self.stimuli_code.append(0)
                    self.number_trials += 1
            for x in self.mat[str(self.file) + " " + str(self.selected_trial)][temp_var][0][0][4]:
                self.firing.append(x[0])
            counter = 1
            for i, x in enumerate(self.stimuli_code):
                if x == 0:
                    self.dictionary[counter] = i
                    counter += 1

            temp_list = []
            temp_key = 1
            for x in self.firing:
                try:
                    if x <= self.stimuli_time[self.dictionary[temp_key]]:
                        temp_list.append(x)
                    else:
                        self.trialled_firing.append(temp_list)
                        temp_list = []
                        temp_key += 1
                except KeyError:
                    break
            index = self.selected_trial
            if index == "1":
                self.a.cla()
                for x in self.trialled_firing[int(index)-1]:
                    self.a.plot([x, x], [0, 10], "r-")

                self.a.plot(self.stimuli_time[0:self.dictionary[1]+1],
                            self.stimuli_code[0:self.dictionary[1]+1], 'ko', ms=6)

                for i, x in enumerate(self.stimuli_code[0:self.dictionary[1]+1]):
                    self.a.annotate(s=str(x), xy=(self.stimuli_time[i], x), xytext=(self.stimuli_time[i], 10.2), color='0.2', size=13, weight="bold")

                self.a.axis(xmin=0, xmax=self.stimuli_time[self.dictionary[1]])
                self.a.set_xlabel("Time (s)")
                self.a.set_ylabel("Amplitude of Stimuli")
            else:
                self.a.cla()

                for x in self.trialled_firing[int(index)-1]:
                    self.a.plot([x, x], [0, 10], "r-")

                self.a.plot(self.stimuli_time[self.dictionary[int(index)-1]:self.dictionary[int(index)]+1],
                            self.stimuli_code[self.dictionary[int(index)-1]:self.dictionary[int(index)]+1],
                            'ko', ms=6)

                for i, x in enumerate(self.stimuli_code[self.dictionary[int(index)-1]:self.dictionary[int(index)]+1]):
                    self.a.annotate(s=str(x), xy=(self.stimuli_time[i+self.dictionary[int(index)-1]], x),
                                    xytext=(self.stimuli_time[i+self.dictionary[int(index)-1]], 10.2),
                                    color='0.2', size=13, weight="bold")

                self.a.axis(xmin=self.stimuli_time[self.dictionary[int(index)-1]],
                            xmax=self.stimuli_time[self.dictionary[int(index)]])
                self.a.set_xlabel("Time (s)")
                self.a.set_ylabel("Amplitude of Stimuli")

            self.image_panel.get_tk_widget().grid(row=1,     columnspan=3, column=4, sticky='nsew')

    # Finished : Working
    def unload_selected(self):
        if self.list_of_open_files.curselection() is not None:
            items = self.list_of_open_files.curselection()
            if self.list_of_open_files.get(items) == self.highlighted:
                self.highlighted = None

            self.active_files.remove(self.listbox_data[self.list_of_open_files.get(items)])

            pos = 0
            for i in items:
                idx = int(i) - pos
                self.list_of_open_files.delete(idx, idx)
                pos += 1

            self.list_of_open_files.selection_clear(0, self.list_of_open_files.size())
            if self.list_of_open_files.size() > 0:
                self.list_of_open_files.selection_set(items[0])
            self.trial_listbox.delete(0, self.trial_listbox.size())
            self.trial_text.configure(text='Number of Trials:')
            self.file_text.configure(text='Selected File:')
            self.display_trial_text.configure(text='Graphed Trial: ')

            self.image_panel.get_tk_widget().delete('all')
            self.image_panel.get_tk_widget().grid_remove()

            self.tk.call(self.image_panel.get_tk_widget(), 'delete', 1, 1)
            del self.figure
            del self.image_panel

            self.figure = Figure(figsize=(9, 6), dpi=100)
            self.image_panel = FigureCanvasTkAgg(self.figure, self)
            self.a = self.figure.add_subplot(111)
            self.image_panel.get_tk_widget().grid(row=1,     columnspan=3, column=4, sticky='nsew')

    def set_active(self, event):
        if self.list_of_open_files.size() > 0:
            self.highlighted = self.list_of_open_files.get(self.list_of_open_files.curselection())

    # Unfinished
    def new_file_window(self):
        if self.highlighted not in self.opened_files.keys() and self.highlighted is not None:
            self.opened_files[self.highlighted] = NewWindow(self.listbox_data[self.highlighted], self.highlighted, type='0')
            self.opened_files[self.highlighted].start()
        elif self.highlighted in self.opened_files.keys():
            if not self.opened_files[self.highlighted].is_alive():
                self.opened_files[self.highlighted] = NewWindow(self.listbox_data[self.highlighted], self.highlighted, type='0')
                self.opened_files[self.highlighted].start()


class SeparateWindowFile(tk.Frame):
    def __init__(self, master=None, num_trials=0, file=None, file_name=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.file = file
        self.file_name = file_name
        self.master.title('Trial Viewer ({})'.format(self.file_name))

        # graphing api
        self.number_trials = 0
        self.selected_trial = None

        self.stimuli_time = []
        self.stimuli_code = []
        self.firing = []
        self.trialled_firing = []

        self.dictionary = {}
        self.mat = {}

        # Base Image Viewer
        self.figure = Figure(figsize=(9, 6), dpi=100)
        self.a = self.figure.add_subplot(111)
        self.image_panel = FigureCanvasTkAgg(self.figure, self)

        # Toolbar
        self.menu = tk.Menu(self.master)

        try:
            self.master.config(menu=self.menu)
        except AttributeError:
            # master is a top-level window (Python 1.4/Tkinter 1.63)
            self.master.tk.call(master, "config", "-menu", self.menu)

        # File Cascade
        self.file_menu = tk.Menu(self.menu, tearoff=False)
        self.file_menu.add_command(label='Settings...', command=None)
        self.menu.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', command=self.quit)

        # Help Cascade
        self.help_menu = tk.Menu(self.menu, tearoff=False)
        self.help_menu.add_command(label='About', command=None)

        self.menu.add_cascade(label='Help', menu=self.help_menu)

        # Textbox
        self.trial_text = tk.Label(self, text='Trial: ', width=40, anchor='w', relief='groove')

        # Trial Viewer
        self.trials = tk.Scrollbar(self)
        self.trial_listbox = tk.Listbox(self, yscrollcommand=self.trials.set, width=6, activestyle='none',
                                        selectmode='single', exportselection=False, highlightthickness=0)

        for x in range(1, num_trials):
            self.trial_listbox.insert('end', str(x))

        self.trial_listbox.bind('<Double-1>', self.trial_selected)
        self.trials.config(command=self.trial_listbox.yview)

        # Toolbar
        self.scrollbar_toolbar = tk.Frame(self)
        if sys.platform == ("win32" or "cygwin"):
            self.icon = 'icons\\'

        elif sys.platform == "darwin":
            self.icon = 'icons/'

        self.analyse = Image.open(self.icon+'analyse.png')
        self.analyse = self.analyse.resize((14, 14), Image.ANTIALIAS)
        self.tk_analyse = ImageTk.PhotoImage(self.analyse)
        self.analyse_button = tk.Button(self.scrollbar_toolbar, image=self.tk_analyse,
                                        command=None, relief='flat', padx=2, pady=2,
                                        overrelief='groove', anchor='center')

        ttk.Separator(self.scrollbar_toolbar, orient='vertical').pack(side='left', fill='y', padx=2)
        self.analyse_button.pack(side='left')

        # Weight setup
        self.rowconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # Grid Setup
        self.scrollbar_toolbar.grid(row=0, column=0, sticky='ew', pady=1)
        self.trial_text.grid(row=0, column=2, sticky='ew', padx=1, pady=1)
        self.trial_listbox.grid(row=1, column=0, sticky='ns', padx=1, pady=1)
        self.trials.grid(row=1, column=1, sticky='ns', padx=1, pady=1)
        self.image_panel.get_tk_widget().grid(row=1, column=2, sticky='nsew', padx=0, pady=0)

    def trial_selected(self, event):
        widget = event.widget
        self.selected_trial = widget.get(widget.curselection())
        self.trial_text.configure(text='Trial: ' + str(self.selected_trial))

        self.image_panel.get_tk_widget().delete('all')
        self.image_panel.get_tk_widget().grid_remove()

        self.tk.call(self.image_panel.get_tk_widget(), 'delete', 1, 1)
        del self.figure
        del self.image_panel

        self.figure = Figure(figsize=(9, 6), dpi=100)
        self.image_panel = FigureCanvasTkAgg(self.figure, self)
        self.a = self.figure.add_subplot(111)

        if self.selected_trial is not None:
            if str(str(self.file) + " " + str(self.selected_trial)) not in self.mat.keys():
                try:
                    self.mat[str(self.file) + " " + str(self.selected_trial)] = sc_io.loadmat(self.file, appendmat=True)
                except Exception as e:
                    try:
                        self.mat[str(self.file) + " " + str(self.selected_trial)] = sc_io.loadmat(self.file, appendmat=True)
                    except FileNotFoundError:
                        print("File not found: ", e)

                temp_var = sc_io.whosmat(self.file)[0][0]

                for x in self.mat[str(self.file) + " " + str(self.selected_trial)]['StimTrig'][0][0][4]:
                    self.stimuli_time.append(x[0])
                for x in self.mat[str(self.file) + " " + str(self.selected_trial)]['StimTrig'][0][0][5]:
                    if x[0] != 62:
                        self.stimuli_code.append(x[0])
                    else:
                        self.stimuli_code.append(0)
                        self.number_trials += 1
                for x in self.mat[str(self.file) + " " + str(self.selected_trial)][temp_var][0][0][4]:
                    self.firing.append(x[0])
                counter = 1
                for i, x in enumerate(self.stimuli_code):
                    if x == 0:
                        self.dictionary[counter] = i
                        counter += 1

                temp_list = []
                temp_key = 1
                for x in self.firing:
                    try:
                        if x <= self.stimuli_time[self.dictionary[temp_key]]:
                            temp_list.append(x)
                        else:
                            self.trialled_firing.append(temp_list)
                            temp_list = []
                            temp_key += 1
                    except KeyError:
                        break
            index = self.selected_trial
            if index == "1":
                self.a.cla()
                for x in self.trialled_firing[int(index)-1]:
                    self.a.plot([x, x], [0, 10], "r-")

                self.a.plot(self.stimuli_time[0:self.dictionary[1]+1],
                            self.stimuli_code[0:self.dictionary[1]+1], 'ko', ms=6)

                for i, x in enumerate(self.stimuli_code[0:self.dictionary[1]+1]):
                    self.a.annotate(s=str(x), xy=(self.stimuli_time[i], x), xytext=(self.stimuli_time[i], 10.2), color='0.2', size=13, weight="bold")

                self.a.axis(xmin=0, xmax=self.stimuli_time[self.dictionary[1]])
                self.a.set_xlabel("Time (s)")
                self.a.set_ylabel("Amplitude of Stimuli")
            else:
                self.a.cla()

                for x in self.trialled_firing[int(index)-1]:
                    self.a.plot([x, x], [0, 10], "r-")

                self.a.plot(self.stimuli_time[self.dictionary[int(index)-1]:self.dictionary[int(index)]+1],
                            self.stimuli_code[self.dictionary[int(index)-1]:self.dictionary[int(index)]+1],
                            'ko', ms=6)

                for i, x in enumerate(self.stimuli_code[self.dictionary[int(index)-1]:self.dictionary[int(index)]+1]):
                    self.a.annotate(s=str(x), xy=(self.stimuli_time[i+self.dictionary[int(index)-1]], x),
                                    xytext=(self.stimuli_time[i+self.dictionary[int(index)-1]], 10.2),
                                    color='0.2', size=13, weight="bold")

                self.a.axis(xmin=self.stimuli_time[self.dictionary[int(index)-1]],
                            xmax=self.stimuli_time[self.dictionary[int(index)]])
                self.a.set_xlabel("Time (s)")
                self.a.set_ylabel("Amplitude of Stimuli")

        self.image_panel.get_tk_widget().grid(row=1, column=2, sticky='nsew', padx=0, pady=0)
        # self.after(500, self.do_after)

    def do_after(self):
        self.image_panel.get_tk_widget().delete('all')


class NewWindow(Process):
    def __init__(self, file, file_name, process_type):
        Process.__init__(self)
        self.mat_lab = graphing_api.GraphingApplication()
        self.mat_lab.open_file(file)
        self.number_of_trials = self.mat_lab.number_trials

        self.file = file
        self.file_name = file_name
        self.type = process_type

    def run(self):
        if self.type == '0':
            self.root = tk.Tk()
            self.my_application = SeparateWindowFile(self.root, self.number_of_trials, self.file, self.file_name)
            self.my_application.pack(fill='both', expand=True)
            self.my_application.mainloop()
        elif self.type == '1':
            self.root = tk.Tk()
            self.my_application = SeparateWindowFile(self.root, self.number_of_trials, self.file, self.file_name)
            self.my_application.pack(fill='both', expand=True)
            self.my_application.mainloop()