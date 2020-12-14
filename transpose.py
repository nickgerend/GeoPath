# Written by: Nick Gerend, @dataoutsider
# Viz: "Geo Path", enjoy!

import pandas as pd
import numpy as np
import os
from math import cos, asin, sqrt, pi
import ast

df = pd.read_csv(os.path.dirname(__file__) + '/Amtrak_Routes.csv', engine='python') # test with , nrows=20
exclude = [272956,259103,170181,170178,170175,170176,170201,170202,170203,170204,263611,256916,170905]
ex_obj = [3806]
df = df.loc[~df['FRFRANODE'].isin(exclude) & ~df['OBJECTID'].isin(ex_obj) & (df['STATEAB'] == 'TX')]
df = df.reset_index(drop=True)
df['Latitude'] = 0.0
df['Longitude'] = 0.0

o_rows = len(df.index)
i_float = 0
for index, row in df.iterrows():
    data = row['coord']
    coordinates = ast.literal_eval(data)
    df = df.append([row]*len(coordinates),ignore_index=True)
    start = o_rows + i_float
    for i in range(start, start + len(coordinates)):
        df['Longitude'][i] = coordinates[i - start][0]
        df['Latitude'][i] = coordinates[i - start][1] 
    i_float += len(coordinates)

df = df.iloc[o_rows:]
df.reset_index(inplace=True)
print(df)
df.to_csv(os.path.dirname(__file__) + '/Amtrak_Routes_Transpose.csv', encoding='utf-8', index=False)