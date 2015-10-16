import tkinter as tk
import os
import main_gui
import graphing_api
import sys
import time
from itertools import repeat
from multiprocessing import Process, Queue, Pool, Manager

# Written by Jay

platform_filename = ''
os.chdir('..')
if sys.platform == ("win32" or "cygwin"):
    platform_filename = '\\'

elif sys.platform == "darwin":
    platform_filename = '/'


class AppProcess(Process):
    def __init__(self, queue):
        Process.__init__(self)
        self.queue = queue

    def run(self):
        self.root = tk.Tk()
        self.my_application = main_gui.Application(self.root)
        self.root.after(100, self._check_queue)
        self.my_application.pack(fill='both', expand=True)
        self.my_application.mainloop()

    def _check_queue(self):
        if self.my_application.selected_file is not None:
            self.queue.put(self.my_application.listbox_data[self.my_application.selected_file])
        self.root.after(100, self._check_queue)


def load_to_memory(file, trial):
    temp_graph = graphing_api.GraphingApplication()
    temp_graph.open_file(file)
    image = temp_graph.get_graph(trial)
    return (image, trial)

def delay(t0):
    return time.time() - t0

if __name__ == '__main__':
    data_catcher = Queue()

    app_process = AppProcess(data_catcher)
    app_process.start()

    cur_file = []
    parsed = False

    received_data = {}

    while True:
        data = data_catcher.get()
        if data is not None and data not in cur_file and not parsed:
            cur_file.clear()
            cur_file.append(data)
            api = graphing_api.GraphingApplication()
            api.open_file(data)

            number_of_trials = int(api.number_trials)

            start_time = time.time()
            manager = Manager()
            queue = manager.Queue()
            processes = Pool(processes=int(number_of_trials/7))
            list_of_trials = [str(x) for x in range(1, number_of_trials)]

            print('starting file analysis')
            for x in processes.starmap_async(load_to_memory, zip(repeat(data), list_of_trials)).get():
                received_data[x[1]] = x[0]
            parsed = True
            print('Took ' + str(delay(start_time)) + 'to finish analysis of file')

        elif data is not None and data not in cur_file:
            cur_file = []
            parsed = False