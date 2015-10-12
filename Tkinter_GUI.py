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
        self.quitButton = tk.Button(self, text="Quit", command=self.quit)
        self.Graphbutton = tk.Button(self, text="Graph selected trial", command=self.create_graph)
        self.BrowseButton = tk.Button(self, text="Browse", command=self.browse)
        self.statustext = tk.Text(self, width=30, height=5)
        self.Trialtext = tk.Text(self, width=30, height=1)
        self.TrialEntry = tk.Entry(self)
        self.TrialEntry.bind('<Return>', self.create_graph)
        self.TrialLabel = tk.Label(self, text="Trial Number:")
        self.Graphbutton.grid(column=0, row=0)
        self.TrialLabel.grid(column=0, row=1)
        self.TrialEntry.grid(column=0, row=2)
        self.BrowseButton.grid(column=0, row=3)
        self.Trialtext.grid(column=0, row=4)
        self.statustext.grid(column=0, row=5)
        self.quitButton.grid(column=0, row=6)
        self.statustext.insert("1.0", "Waiting for input.\n")
        self.Trialtext.insert("1.0", "Number of trials: " + self.NumberOfTrials + "\n")

        self.panel = tk.Label(self, image=None)
        self.panel.grid(column=0, row=7)

    # Function Reference: C
    def browse(self):
        self.activefile = filedialog.askopenfilename()
        self.activefile = self.activefile.split("/")
        self.activefile = self.activefile[len(self.activefile)-1]
        if self.activefile != "":
            self.statustext.insert("1.0","Opened file: \n\"" + self.activefile + "\"\n")
            self.StimTrig_Stimuli, self.StimTrig_Time, self.Sch_wav_Time, self.trial_dictionary,\
                self.Sch_wav_Time_Trialled, self.number_of_trials = Graph.open_matlab_file(self.activefile)
            self.Trialtext.insert("1.0","Number of trials: " + str(self.number_of_trials) + "\n")

    # Function Reference: D
    def create_graph(self, event=None):
        TrialNum = self.TrialEntry.get()
        self.statustext.insert("1.0", "Attempting to graph trial "+TrialNum+" \nof file " + self.activefile + "\n")
        if self.activefile is not None:
            try:
                x = Graph.trial_graphs(self.Sch_wav_Time_Trialled, self.StimTrig_Stimuli, self.StimTrig_Time,
                                   self.trial_dictionary, TrialNum)
                img = Image.open(io.BytesIO(x))
                tkimage = ImageTk.PhotoImage(img)

                self.panel.image = tkimage
                self.panel.configure(image=tkimage)
            except IndexError:
                self.statustext.insert("1.0", "No such trial.\n")

        else:
            self.statustext.insert("1.0", "No File Selected\n")

# Section Reference: B
try:
    app = Application()
    app.master.title("Tkinter GUI V0.5")
    app.master.minsize(217, 217)
    app.mainloop()
except Exception as error:
    print("Error Caught: Code: 01-B", error)