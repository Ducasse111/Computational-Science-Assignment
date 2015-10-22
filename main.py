import tkinter as tk
import os
import main_gui
import graphing_api
import sys
import time
import multiprocessing
from itertools import repeat
from multiprocessing import Process, Queue, Pool, Manager

platform_filename = ''
os.chdir('..')
if sys.platform == ("win32" or "cygwin"):
    platform_filename = '\\'

elif sys.platform == "darwin":
    platform_filename = '/'


class MainApp(Process):
    def __init__(self, queue):
        Process.__init__(self)
        self.queue = queue
        self.new_windows = []

    def run(self):
        self.root = tk.Tk()
        self.my_application = main_gui.Application(self.root)
        self.root.after(100, self._check_queue)
        self.my_application.pack(fill='both', expand=True)
        self.my_application.mainloop()

    def _check_queue(self):
        if self.my_application.highlighted is not None and self.my_application.new_window not in self.new_windows\
                and self.my_application.new_window is not None:
            selection = self.my_application.highlighted
            self.queue.put(self.my_application.listbox_data[selection])
            self.new_windows.append(self.my_application.new_window)
        self.root.after(100, self._check_queue)


class NewWindow(Process):
    def __init__(self, number_of_trials, file, data):
        Process.__init__(self)
        self.number_of_trials = number_of_trials
        self.file = file
        self.data = data

    def run(self):
        self.root = tk.Tk()
        self.my_application = main_gui.SeparateWindowFile(self.root, self.number_of_trials, self.file, self.data)
        self.my_application.pack(fill='both', expand=True)
        self.my_application.mainloop()


def load_to_memory(file, trial):
    temp_graph = graphing_api.GraphingApplication()
    temp_graph.open_file(file)
    image = temp_graph.get_graph(trial)
    return image, trial

def delay(t0):
    return time.time() - t0

def start_new_window(file_name, number_of_trials, received_data):
    pass

if __name__ == '__main__':
    data_catcher = Queue()

    app_process = MainApp(data_catcher)
    app_process.start()

    cur_file = []

    parsed = False

    received_data = {}
    active_processes = {}

    while True:
        data = data_catcher.get()
        file = data
        file = file.split('/')
        file_name = file[-1]
        file_path = file[:-1]
        if file_name not in active_processes.keys():
            api = graphing_api.GraphingApplication()
            api.open_file(data)

            number_of_trials = int(api.number_trials) + 1

            manager = Manager()
            queue = manager.Queue()
            pool_count = multiprocessing.cpu_count() * 2
            processes = Pool(processes=pool_count, maxtasksperchild=2)
            list_of_trials = [str(x) for x in range(1, number_of_trials)]

            print('starting file analysis')
            start_time = time.time()
            for image, trial in processes.starmap_async(load_to_memory, zip(repeat(data), list_of_trials)).get():
                received_data[trial] = image
            print('Took ' + str(delay(start_time)) + 'to finish analysis of file')

            parsed = True
            active_processes[file_name] = NewWindow(number_of_trials, file_name, received_data)
            active_processes[file_name].start()