import csv

import pandas as pd

import os

directory = './Data/'

if not os.path.exists(directory):
    os.makedirs(directory)

df = pd.read_csv('../DataExtraction/airline.csv.suffle',nrows=0,encoding='latin1')
header = df.columns.tolist()

for Y in range(1987,2009):
    with open(f'./Data/{Y}.csv','w',newline='') as csvfile:
        w = csv.writer(csvfile)
        w.writerow(header)


ChunkSize = 100000
completed = 0
for chunk in pd.read_csv('../DataExtraction/airline.csv.suffle',chunksize=ChunkSize,encoding='latin1'):
    for year in range(1987,2009):
        year_df = chunk[chunk['Year'] == year]
        year_df.to_csv(f'./Data/{year}.csv', mode='a', header=False, index=False)
    completed = completed + ChunkSize
    print(f"COMPLETED {completed}...")





