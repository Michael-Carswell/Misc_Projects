import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import pathlib


input_name = "output"

dir = str(pathlib.Path(__file__).parent.resolve()) 
dir = dir.replace("\\","/") + "/" 
input_dir = dir + "output/"
input_file = input_dir + input_name + ".csv"

df = pd.read_csv(input_file)

#Checking df
print(df.shape)
print(df.info)

#Print Columns
df = df.drop(['Serial No.'], axis=1)
print(df.head())





