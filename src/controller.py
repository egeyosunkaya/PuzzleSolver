from datetime import datetime
import os, sys, json, htmlPy
from random import randint
import time

import src.back_end.solver.Solve as solver
import threading

class Controller(htmlPy.Object):

    puzzles = None
    scrapper = None
    base_dir = None
    cur_date = None

    def __init__(self, app, base_dir):
        super(Controller, self).__init__()
        self.app = app
        try:
            self.puzzles = json.load(open(os.path.join(base_dir, "back_end/Data/data.json")))
        except:
            self.console_log("data.json not found!", "error")

        # runtime imports
        sys.path.insert(0, os.path.join(base_dir, "back_end/"))
        self.scrapper = __import__('scrapper')
        self.base_dir = base_dir

    @htmlPy.Slot()
    def say_hello_world(self):
        self.app.html = u"Hello, world"

    @htmlPy.Slot(str)
    def get_puzzle(self, json_data):
        if (json.loads(json_data)['date'] == "today"):
            puzzle_date = datetime.today().date()
            time.sleep(randint(5, 9))
        else:
            # Check date
            puzzle_date = datetime.strptime(json.loads(json_data)['date'], "%d-%m-%Y").date()

        if puzzle_date.weekday() == 5:
            self.app.evaluate_javascript("alert('You cannot get this puzzle because, it\\'s SATURDAY!')");
            return

        # Find Puzzle
        puzzle = None
        if self.puzzles is not None:
            for x in self.puzzles:
                if x['date'] == str(puzzle_date):
                    puzzle = x
                    break

        # Not found
        if puzzle is None:
            self.app.evaluate_javascript("alert('Sorry, Puzzle not fetched yet!')");
            return
        self.app.evaluate_javascript("initPuzzle(" + json.dumps(puzzle) + ")")
        self.cur_date = puzzle_date

    @htmlPy.Slot()
    def sync_puzzles(self):
        self.app.evaluate_javascript("alert('Puzzles will be synced now. This process can take an hour. Please be patient.')");
        self.scrapper.start(os.path.join(self.base_dir, "back_end/Data/data.json"))
        self.puzzles = json.load(open(os.path.join(self.base_dir, "back_end/Data/data.json")))  # re-fetch puzzles to memory
        self.app.evaluate_javascript("alert('Sync process completed!')")

    # Forward JS console.log to shell
    @htmlPy.Slot(str, str)
    def console_log(self, log, type="log"):
        if type == "log":
            print(str(datetime.now().time()) + "[LOG] " + log)
        elif type == "error":
            print(str(datetime.now().time()) + "[ERROR] " + log)
        else:
            print(str(datetime.now().time()) + "[UNKNOWN] " + log)

    @htmlPy.Slot(list)
    def set_puzzle_as(self, puzzle):
        print('Im here')
        print(json.dumps(puzzle))
        self.app.evaluate_javascript("set_puzzle_as(" + json.dumps(puzzle) + ")")

    @htmlPy.Slot()
    def start_to_solve(self):
        if (self.cur_date is None):
            self.app.evaluate_javascript("alert('Select a puzzle first!')")

        self.app.evaluate_javascript("clear_to_solve()")
        date = ""
        elements = list(str(self.cur_date).split("-"))
        date += elements[0] + "-" + elements[1] + "-" + elements[2]
        print(date)
        self.set_puzzle_as(solver.solve([self], date))

