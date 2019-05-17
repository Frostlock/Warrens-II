# Converts a csv file to a json file

import json
import csv

csv_file = "input.csv"
output = {}

f = open(csv_file, 'r')
columns = f.readline().replace("\n", "").split(",")
reader = csv.DictReader(f, fieldnames=columns)

for row in reader:
    json_row = {}
    for i in range(0, len(columns)):
        try:
            if columns[i] == "color":
                json_row[columns[i]] = eval(row[columns[i]])
            else:
                json_row[columns[i]] = int(row[columns[i]])
        except ValueError as e:
            json_row[columns[i]] = row[columns[i]]
    output[row[columns[0]]] = json_row

print(json.dumps(output, indent=4, sort_keys=True))
