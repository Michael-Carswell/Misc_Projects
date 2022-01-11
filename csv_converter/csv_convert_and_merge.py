import pathlib
import pandas
import json
import csv
import os.path
from pprint import pprint
import datetime
import calendar
import glob
import os
import multiprocessing as mp

### SETUP ###
### Enter the file name from the name of the logging module in cube monitor flow ###
print("\nThis is a .stcm to .csv converter make sure your file is in the same folder as this script.\n")
#file_name = input("Enter file name before timestamp e.g for \"Log_Sensor Data_2021-11-25_15h34m34s.stcm\" enter \"Log_Sensor Data_\" :")
file_name = "Log_myVariables_"
output_name = "output"

dir = str(pathlib.Path(__file__).parent.resolve()) 
dir = dir.replace("\\","/") + "/" 
output_dir = dir + "output/"
dir = dir + "input/"

time_date_format = "%Y-%m-%d_%Hh%Mm%Ss"
file_extension = ".stcm"
time_date_dir = dir.replace("/","\\")
time_date_dir = time_date_dir + file_name + time_date_format + file_extension 
print(time_date_dir)
print(output_dir)
csv_files = []

### Helper functions ###

# take the second element for sort
def take_second(elem):
    return elem[1]

# function to replace "." with "__"
def make_file_name(label):
    new_label = label.replace(".","__")
    new_label = new_label + ".csv"
    return new_label

# function to check if variable is part of the current list
def search(list, value):
    for n in (list):
        if n[1] == value:
            return True
    return False


### Script ###

#Join all .stcm log files together in a list.
json_file_list = []
for m in pathlib.Path(dir).glob('*.stcm'):
    date = datetime.datetime.strptime(m.__str__(), time_date_dir)
    unix_timestamp = calendar.timegm(date.utctimetuple())
    json_file_list.append([m, unix_timestamp])


# sort list
json_file_list = sorted(json_file_list, key=take_second)

#Scrub through json_file_list and generate list of variables.
for m in json_file_list:
    with open(m[0], 'r') as json_in:
            for line in json_in:
                if line[0] != "[" and line[0] != "]":
                    if line[-2] == ",":
                        line = line[:-2] + line[-1]
                    json_object = json.loads(line)
                    if search(csv_files , json_object["variablename"]) == False:
                        new_file_name = make_file_name(json_object["variablename"])
                        csv_files.append([new_file_name,json_object["variablename"]])

# Printing out the list we generate.
print(*csv_files, sep = "\n")
progress = 0
#Generate CSV file for each variable in the list.
time_offset = 0
for n in csv_files:
    progress = progress +1
    percentage = progress/len(csv_files)*100
    print("progress:" + str(round(percentage, 1)) + "%")
    for m in json_file_list:
        with open(m[0], 'r') as json_in, open(dir+n[0], 'a', newline='') as csv_out:
            writer = csv.writer(csv_out, delimiter=',')
            # Time offset used for synchronizing across multiple files.
            time_offset_found = True
            if os.path.getsize(dir+n[0]) == 0:
                writer.writerow(['Time (ms)', n[0][0:-4]])
                time_offset_found = False
            # Scanning through each line of the JSON
            for line in json_in:
                if line[0] != "[" and line[0] != "]":
                    if line[-2] == ",":
                        line = line[:-2] + line[-1]
                    json_object = json.loads(line)
                    if json_object['variablename'] == n[1]:
                        variable_data = json_object['variabledata']
                        if not time_offset_found:
                            time_offset = variable_data[0]['x']
                            time_offset_found = True

                        for coordinate in variable_data:
                            writer.writerow([coordinate['x'] - time_offset, coordinate['y']])

# Merge all csv files into one dataframe and export as a csv or excel spreadsheet

input_files = "*.csv"
first_loop  = True

for fname in glob.glob(dir + input_files):
    if first_loop:
        out = pandas.read_csv(fname)
        os.remove(fname)
        first_loop = False
    else:
        df = pandas.read_csv(fname)
        df = df.drop("Time (ms)", axis = 1)
        out = out.join(df, how = 'right', lsuffix= ' ')
        os.remove(fname)

## Outputing data frame as a csv
if os.path.exists(output_dir):
    if os.path.isfile(output_dir + output_name + ".csv"):
        os.remove(output_dir + output_name + ".csv")
else:
    os.mkdir(output_dir)

out.to_csv(output_dir + output_name + ".csv")
# # #need to work on outputting to excel format but not important right now.
# # #out.to_excel(dir + file_name + ".xlsx")