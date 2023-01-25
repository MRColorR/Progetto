import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()

with open(file_path, 'r') as original_file, open('modified.txt', 'w') as modified_file:
    rows = original_file.readlines()[1:]
    rows = [row.strip().split(',') for row in rows]
    rows = sorted(rows, key=lambda x: float(x[2]))
    fieldnames = ["app", "func", "end_timestamp", "duration", "delays"]
    modified_file.write(','.join(fieldnames)+'\n') #write the new field names to modified file
    previous_row = None
    for row in rows:
        if previous_row:
            diff = float(row[2]) - float(previous_row)
            row.append(str(diff))
        else:
            row.append("0")
        previous_row = row[2]
        modified_file.write(','.join(row)+'\n') #join the row elements by comma and write to the new file
