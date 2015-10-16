import io
import sys

import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk

from PIL import Image, ImageTk

import graphing_api

__Version__ = "0.1.1"
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
        self.raw_image = None
        self.cur_image = None
        self.image = None
        self.master.title('Tkinter GUI Rewrite V' + __Version__)
        self.grid()
        self.active_files = []
        self.opened_files = {}
        self.listbox_data = {}
        self.refresh_rate = 100
        self.being_rescaled = False

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

        self.trial_listbox.bind('<Double-Button-1>', self.base_gui_plot_trial)
        self.list_of_open_files.bind('<Double-Button-1>', self.listbox_element_selected)

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

        self.tk_browse_image = ImageTk.PhotoImage(self.browse_image)
        self.tk_delete_image = ImageTk.PhotoImage(self.delete_image)
        self.tk_up_image = ImageTk.PhotoImage(self.up_image)
        self.tk_down_image = ImageTk.PhotoImage(self.down_image)

        self.delete_file_button = tk.Button(self.scrollbar_toolbar, image=self.tk_delete_image,
                                            command=self.unload_selected, relief='flat', padx=2, pady=2,
                                            overrelief='groove', anchor='center')

        self.up_button = tk.Button(self.scrollbar_toolbar, image=self.tk_up_image,
                                   command=self.move_element_up, relief='flat', padx=2, pady=2,
                                   overrelief='groove', anchor='center')

        self.down_button = tk.Button(self.scrollbar_toolbar, image=self.tk_down_image,
                                     command=self.move_element_down, relief='flat', padx=2, pady=2,
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
        ttk.Separator(self.scrollbar_toolbar, orient='vertical').pack(side='right', fill='y', padx=1)

        #####################################################
        # Text Widget
        #####################################################

        self.trial_text = tk.Label(self, text='Number of Trials: ', width=40, anchor='w', relief='groove')
        self.file_text = tk.Label(self, text='Selected File: ', width=40, anchor='w', relief='groove')

        #####################################################
        # Base Image Viewer
        #####################################################

        self.image_panel = tk.Canvas(self, height=480, width=720, bg='white')

        #####################################################
        # Widget Element Configuration
        #####################################################

        # Grid instantiations

        self.scrollbar_toolbar.grid(row=0,             column=0, sticky='ew')
        self.list_of_open_files.grid(row=1, rowspan=1, column=0, sticky='ns', padx=1, pady=1)
        self.file_viewer.grid(row=1,        rowspan=1, column=1, sticky='ns', padx=1, pady=1)
        self.trial_listbox.grid(row=1,      rowspan=1, column=2, sticky='ns', padx=1, pady=1)
        self.trials.grid(row=1,             rowspan=1, column=3, sticky='ns', padx=1, pady=1)
        self.file_text.grid(row=0,                     column=4, sticky='nsw', padx=2, pady=1)
        self.trial_text.grid(row=0,                    column=5, sticky='nsew', padx=2, pady=1)
        self.image_panel.grid(row=1,     columnspan=2, column=4, sticky='nsew')

        # Widget sticky and weighting

        self.rowconfigure(1, weight=2)
        self.columnconfigure(5, weight=1)

        # Widget configurations)

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
        self.image_panel.image = None
        self.image_panel.create_image(0, 0, anchor='nw', image=None)

        widget = event.widget
        self.selected_file = widget.get(widget.curselection())
        self.file_text.configure(text='Selected File: ' + str(self.selected_file))

        trashcan = []
        for keys in self.opened_files.keys():
            trashcan.append(keys)

        for rubbish in trashcan:
            del self.opened_files[rubbish]

        # self.opened_files[self.selected_file] = graphing_api.GraphingApplication()
        # if self.selected_file is not None:
        #     self.quick_load_file(self.opened_files[self.selected_file])

        return self.selected_file

    # Finished : Working
    def quick_load_file(self, graphing_object):
        graphing_object.open_file(self.listbox_data[self.selected_file])
        self.trial_text.configure(text='Number of trials: ' + str(graphing_object.number_trials))
        self.trial_listbox.delete(0, self.trial_listbox.size())
        for x in range(graphing_object.number_trials):
            self.trial_listbox.insert('end', str(x+1))

    # Finished : Working
    def base_gui_plot_trial(self, event):
        widget = event.widget
        self.selected_trial = widget.get(widget.curselection())
        self.raw_image = Image.open(io.BytesIO(self.opened_files[
                                               self.selected_file].get_graph(self.selected_trial)))

        self.cur_image = self.raw_image.resize((self.image_panel.winfo_width(),
                                                self.image_panel.winfo_height()), Image.ANTIALIAS)

        self.image = ImageTk.PhotoImage(self.cur_image)

        self.image_panel.image = self.image
        self.image_panel.create_image(0, 0, anchor='nw', image=self.image)

    # Finished : Working
    def refresh(self):
        if self.raw_image is not None:
            width, height = self.cur_image.size
            if width != self.image_panel.winfo_width() or height != self.image_panel.winfo_height():

                self.cur_image = self.raw_image.resize((self.image_panel.winfo_width(),
                                                        self.image_panel.winfo_height()), Image.ANTIALIAS)

                self.image = ImageTk.PhotoImage(self.cur_image)

                self.image_panel.image = self.image
                self.image_panel.create_image(0, 0, anchor='nw', image=self.image)
        self.being_rescaled = False

    # Finished : Working
    def on_resize(self, event):
        del event
        if not self.being_rescaled:
            self.being_rescaled = True
            self.after(100, self.refresh)

    # Finished : Working
    def unload_selected(self):
        if self.list_of_open_files.curselection() is not None:
            items = self.list_of_open_files.curselection()
            pos = 0
            for i in items:
                idx = int(i) - pos
                self.list_of_open_files.delete(idx, idx)
                pos += 1

            self.list_of_open_files.selection_clear(0, self.list_of_open_files.size())
            if self.list_of_open_files.size() > 0:
                self.list_of_open_files.selection_set(items[0])
            self.trial_listbox.delete(0, self.trial_listbox.size())
            self.trial_text.configure(text='Number of trials:')
            self.file_text.configure(text='Selected File:')

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