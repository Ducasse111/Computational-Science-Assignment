# File Reference Number: 01
import tkinter as tk
import logging
from tkinter import filedialog
from PIL import Image, ImageTk
import io

import Graph

# Class Reference: A
class Application(tk.Frame):

    # Function Reference: A
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.activefile = None
        self.NumberOfTrials = "Unknown"
        self.add_widgets()
        self.refresh_rate = 100
        self.after(self.refresh_rate, self.check_update)

    # Function Reference: B
    def add_widgets(self):
        self.quitButton = tk.Button(self, text="Quit", command=self.quit)
        self.Graphbutton = tk.Button(self, text="Graph selected trial", command=self.create_graph)
        self.BrowseButton = tk.Button(self, text="Browse", command=self.browse)
        self.Trialtext = tk.Text(self, width=30, height=1)
        self.TrialEntry = tk.Entry(self)
        self.TrialLabel = tk.Label(self, text="Trial Number:")

        self.statustext = tk.Text(self, width=30, height=5)

        self.statustext.configure(state='disabled')
        self.Trialtext.configure(state='disabled')

        self.BrowseButton.grid(column=0, row=0, sticky="W")
        self.TrialLabel.grid(column=1, row=0, sticky="W")
        self.TrialEntry.grid(column=2, row=0, sticky="W")
        self.Graphbutton.grid(column=3, row=0, sticky="W")

        self.quitButton.grid(column=4, row=0, sticky="E")

        self.Trialtext.grid(column=0, columnspan=5, row=1, sticky="E"+"W")
        self.statustext.grid(column=0, columnspan=5, row=2, sticky="E"+"W")

        self.edit_text(self.statustext, "Waiting for input.\n")
        self.edit_text(self.Trialtext, "Number of trials: " + self.NumberOfTrials + "\n")

        self.TrialEntry.bind('<Return>', self.create_graph)
        # self.bind('<Configure>', self.on_resize)

        self.image = None
        self.raw_img = None
        self.panel = tk.Label(self, image=self.image)
        self.panel.grid(column=0, columnspan=5, row=3, sticky="N"+"S"+"E"+"W")

        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 4, weight=1)
        tk.Grid.rowconfigure(self, 3, weight=1)

    def check_update(self):
        if self.raw_img is not None:
            if self.raw_img.width != self.panel.winfo_width() or self.raw_img.height != self.panel.winfo_height():
                self.img = self.raw_img
                self.raw_img = self.img
                self.img = self.img.resize((self.panel.winfo_width()-4, self.panel.winfo_height()-4), Image.ANTIALIAS)
                self.tkimage = ImageTk.PhotoImage(self.img)

                self.panel.image = self.tkimage
                self.panel.configure(image=self.tkimage)
        self.after(self.refresh_rate, self.check_update)

    # Function Reference: C
    def browse(self):
        self.activefile = filedialog.askopenfilename()
        self.activefile = self.activefile.split("/")
        self.activefile = self.activefile[len(self.activefile)-1]
        if self.activefile != "":
            self.edit_text(self.statustext, "Opened file: \n\"" + self.activefile + "\"\n")
            self.StimTrig_Stimuli, self.StimTrig_Time, self.Sch_wav_Time, self.trial_dictionary,\
                self.Sch_wav_Time_Trialled, self.number_of_trials = Graph.open_matlab_file(self.activefile)
            self.edit_text(self.Trialtext, "Number of trials: " + str(self.number_of_trials) + "\n")

    # Function Reference: D
    def create_graph(self, event=None):
        if self.activefile is not None:
            TrialNum = self.TrialEntry.get()

            self.edit_text(self.statustext, "Attempting to graph trial "+TrialNum+" \nof file " + self.activefile + "\n")
            if TrialNum != '':
                try:
                    x = Graph.trial_graphs(self.Sch_wav_Time_Trialled, self.StimTrig_Stimuli, self.StimTrig_Time,
                                       self.trial_dictionary, TrialNum)
                    self.img = Image.open(io.BytesIO(x))
                    self.raw_img = self.img
                    self.img = self.img.resize((self.panel.winfo_width()-4, self.panel.winfo_height()-4), Image.ANTIALIAS)
                    self.tkimage = ImageTk.PhotoImage(self.img)

                    self.panel.image = self.tkimage
                    self.panel.configure(image=self.tkimage)
                except KeyError as e:
                    self.edit_text(self.statustext, "Trial out of range.\n", e)
                except IndexError as e:
                    self.edit_text(self.statustext, "Trial out of range.\n", e)
            else:
                self.edit_text(self.statustext, "No trial selected.\n")
        else:
            self.edit_text(self.statustext, "No file selected.\n")

    def edit_text(self, textbox, text):
        textbox.configure(state='normal')
        textbox.insert("1.0", text)
        textbox.configure(state='disabled')

    # def on_resize(self, event):
    #     if self.raw_img is not None:
    #         if self.raw_img.width != self.panel.winfo_width() or self.raw_img.height != self.panel.winfo_height():
    #             self.img = self.raw_img
    #             self.raw_img = self.img
    #             self.img = self.img.resize((self.panel.winfo_width(), self.panel.winfo_height()), Image.ANTIALIAS)
    #             self.tkimage = ImageTk.PhotoImage(self.img)
    #
    #             self.panel.image = self.tkimage
    #             self.panel.configure(image=self.tkimage)

# Section Reference: B
app = Application()
app.master.title("Tkinter GUI V0.5")
app.pack(fill="both", expand="YES")
app.master.minsize(217, 217)
app.mainloop()

#te
# try:
#     app = Application()
#     app.master.title("Tkinter GUI V0.5")
#     app.master.minsize(217, 217)
#     app.mainloop()
# except Exception as error:
#     print("Error Caught: Code: 01-B", error)