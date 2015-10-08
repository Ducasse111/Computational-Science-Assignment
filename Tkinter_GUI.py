import tkinter as tk

import Graph


class Application(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.add_widgets()

    def add_widgets(self):
        self.quitButton = tk.Button(self, text = "Quit", command = self.quit)
        self.Graphbutton = tk.Button(self, text = "Graph selected trial", command = self.Create_Graph)
        self.TrialEntry = tk.Entry(self)
        self.TrialLabel = tk.Label(self, text = "Trial Number:")
        self.quitButton.grid(column=0, row=0)
        self.Graphbutton.grid(column=0, row=1)
        self.TrialLabel.grid(column=0, row=2)
        self.TrialEntry.grid(column=1, row=2)

    def Create_Graph(self):
        TrialNum = self.TrialEntry.get()
        print(TrialNum)
        StimTrig_Stimuli, StimTrig_Time, Sch_wav_Time, trial_dictionary, Sch_wav_Time_Trialled = Graph.open_matlab_file('660806_rec03_all')
        Graph.trial_graphs(Sch_wav_Time_Trialled, StimTrig_Stimuli, StimTrig_Time, trial_dictionary)


app = Application()
app.master.title("Tkinter GUI V0.1")
app.mainloop()