import tkinter as tk
from tkinter import filedialog

import Graph


class Application(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.activefile = "Unloaded"
        self.add_widgets()


    def add_widgets(self):
        self.quitButton = tk.Button(self, text = "Quit", command = self.quit)
        self.Graphbutton = tk.Button(self, text = "Graph selected trial", command = self.Create_Graph)
        self.BrowseButton = tk.Button(self, text = "Browse", command = self.Browse)
        self.statustext = tk.Text(self, width = 30, height = 5)
        self.TrialEntry = tk.Entry(self)
        self.TrialEntry.bind('<Return>', self.Create_Graph)
        self.TrialLabel = tk.Label(self, text = "Trial Number:")
        self.Graphbutton.grid(column=0, row=0)
        self.TrialLabel.grid(column=0, row=1)
        self.TrialEntry.grid(column=0, row=2)
        self.BrowseButton.grid(column = 0, row = 3)
        self.statustext.grid(column = 0, row = 4)
        self.quitButton.grid(column=0, row=5)
        self.statustext.insert("1.0","Waiting for input.\n")


    def Browse(self):
        self.activefile = filedialog.askopenfilename()
        self.activefile = self.activefile.split("/")
        print(self.activefile)
        self.activefile = self.activefile[len(self.activefile)-1]
        if self.activefile != "":
            self.statustext.insert("1.0","Opened file: \n\"" + self.activefile + "\"\n")


    def Create_Graph(self, event):
        TrialNum = self.TrialEntry.get()
        self.statustext.insert("1.0","Attempting to graph trial "+TrialNum+" \nof file " + self.activefile + "\n")
        if self.activefile != None:
            StimTrig_Stimuli, StimTrig_Time, Sch_wav_Time, trial_dictionary, Sch_wav_Time_Trialled, number_of_trials\
                                                                            = Graph.open_matlab_file(self.activefile)

            try:
                Graph.trial_graphs(Sch_wav_Time_Trialled, StimTrig_Stimuli, StimTrig_Time, trial_dictionary, TrialNum)

            except IndexError:
                self.statustext.insert("1.0", "No such trial.\n")

        else:
            self.statustext.insert("1.0","No File Selected\n")

app = Application()
app.master.title("Tkinter GUI V0.5")
app.master.minsize(217,217)
app.mainloop()