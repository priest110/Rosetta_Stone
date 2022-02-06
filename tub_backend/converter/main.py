# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import json
import codecs
import re as regex
import os

filenames = ['/home/ruizinho/Desktop/Universidade/Mestrado/PI/scripts/agency.txt',
             '/home/ruizinho/Desktop/Universidade/Mestrado/PI/scripts/calendar.txt',
             '/home/ruizinho/Desktop/Universidade/Mestrado/PI/scripts/calendar_dates.txt',
             '/home/ruizinho/Desktop/Universidade/Mestrado/PI/scripts/lines.txt',
             '/home/ruizinho/Desktop/Universidade/Mestrado/PI/scripts/routes.txt',
             '/home/ruizinho/Desktop/Universidade/Mestrado/PI/scripts/stops.txt',
             '/home/ruizinho/Desktop/Universidade/Mestrado/PI/scripts/stop_times.txt',
             '/home/ruizinho/Desktop/Universidade/Mestrado/PI/scripts/trip_notes.txt',
             '/home/ruizinho/Desktop/Universidade/Mestrado/PI/scripts/trips.txt',
             '/home/ruizinho/Desktop/Universidade/Mestrado/PI/scripts/shapes.txt']

content = []
obj = {}

for fn in filenames:
    content = []
    with codecs.open(fn, 'r', encoding='ISO-8859-1') as file:
        for idx, line in enumerate(file):
            obj = {}
            if idx == 0:
                commands = line.strip().split(",")
            else:
                values = line.strip().split(",")
                for i in range(len(commands)):
                    if commands[i] != "shape_id" or values[
                        0] == '29517' or fn == "/home/ruizinho/Desktop/Universidade/Mestrado/PI/scripts/shapes.txt":
                        obj[commands[i]] = values[i]
                    else:
                        obj[commands[i]] = ""
                content.append(obj)
    out_filename = fn.split(".txt")[0] + ".json"
    print(out_filename)
    out_file = open(out_filename, "w")
    json.dump(content, out_file, indent=4, sort_keys=False, ensure_ascii=False)
    out_file.close()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
