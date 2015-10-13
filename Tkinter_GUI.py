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
        self.activefile = "Unloaded"
        self.NumberOfTrials = "Unknown"
        self.add_widgets()

    # Function Reference: B
    def add_widgets(self):
        # for rows in range(0, 7):
        #     tk.Grid.rowconfigure(self, rows, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)

        self.quitButton = tk.Button(self, text="Quit", command=self.quit)
        self.Graphbutton = tk.Button(self, text="Graph selected trial", command=self.create_graph)
        self.BrowseButton = tk.Button(self, text="Browse", command=self.browse)
        self.statustext = tk.Text(self, width=30, height=5)
        self.Trialtext = tk.Text(self, width=30, height=1)
        self.TrialEntry = tk.Entry(self)
        self.TrialLabel = tk.Label(self, text="Trial Number:")

        self.Graphbutton.grid(column=0, row=0, sticky="E"+"W")
        self.TrialLabel.grid(column=0, row=1, sticky="E"+"W")
        self.TrialEntry.grid(column=0, row=2, sticky="E"+"W")
        self.BrowseButton.grid(column=0, row=3, sticky="E"+"W")
        self.Trialtext.grid(column=0, row=4, sticky="E"+"W")
        self.statustext.grid(column=0, row=5, sticky="E"+"W")
        self.quitButton.grid(column=0, row=6, sticky="E"+"W")

        self.statustext.insert("1.0", "Waiting for input.\n")
        self.Trialtext.insert("1.0", "Number of trials: " + self.NumberOfTrials + "\n")

        self.TrialEntry.bind('<Return>', self.create_graph)
        self.bind('<Configure>', self.on_resize)

        self.image = None
        self.raw_img = None
        self.panel = tk.Label(self, image=self.image)
        self.panel.grid(column=0, row=7, sticky="N"+"S"+"E"+"W")
        tk.Grid.rowconfigure(self, 7, weight=1)

    def on_resize(self, event):
        if self.raw_img is not None:
            self.img = self.raw_img
            self.raw_img = self.img
            self.img = self.img.resize((self.panel.winfo_width(), self.panel.winfo_height()), Image.ANTIALIAS)
            self.tkimage = ImageTk.PhotoImage(self.img)

            self.panel.image = self.tkimage
            self.panel.configure(image=self.tkimage)

    # Function Reference: C
    def browse(self):
        self.activefile = filedialog.askopenfilename()
        self.activefile = self.activefile.split("/")
        self.activefile = self.activefile[len(self.activefile)-1]
        if self.activefile != "":
            self.statustext.insert("1.0", "Opened file: \n\"" + self.activefile + "\"\n")
            self.StimTrig_Stimuli, self.StimTrig_Time, self.Sch_wav_Time, self.trial_dictionary,\
                self.Sch_wav_Time_Trialled, self.number_of_trials = Graph.open_matlab_file(self.activefile)
            self.Trialtext.insert("1.0", "Number of trials: " + str(self.number_of_trials) + "\n")

    # Function Reference: D
    def create_graph(self, event=None):
        TrialNum = self.TrialEntry.get()
        self.statustext.insert("1.0", "Attempting to graph trial "+TrialNum+" \nof file " + self.activefile + "\n")
        if self.activefile is not None:
            try:
                x = Graph.trial_graphs(self.Sch_wav_Time_Trialled, self.StimTrig_Stimuli, self.StimTrig_Time,
                                   self.trial_dictionary, TrialNum)
                self.img = Image.open(io.BytesIO(x))
                self.raw_img = self.img
                self.img = self.img.resize((self.panel.winfo_width(), self.panel.winfo_height()), Image.ANTIALIAS)
                self.tkimage = ImageTk.PhotoImage(self.img)

                self.panel.image = self.tkimage
                self.panel.configure(image=self.tkimage)
            except IndexError:
                self.statustext.insert("1.0", "No such trial.\n")

        else:
            self.statustext.insert("1.0", "No File Selected\n")

# Section Reference: B
app = Application()
app.master.title("Tkinter GUI V0.5")
app.pack(fill="both", expand="YES")
app.master.minsize(217, 217)
app.mainloop()

# try:
#     app = Application()
#     app.master.title("Tkinter GUI V0.5")
#     app.master.minsize(217, 217)
#     app.mainloop()
# except Exception as error:
#     print("Error Caught: Code: 01-B", error)
#some stuff to push across changes