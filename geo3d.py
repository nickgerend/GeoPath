# Written by: Nick Gerend, @dataoutsider
# Viz: "Geo Path", enjoy!

import pandas as pd
import os
import math
pd.options.mode.chained_assignment = None

df = pd.read_csv(os.path.dirname(__file__) + '/df_final_X_Y_Z_E_FLAT.csv', engine='python')

maxroute = df.groupby(['Route'])['Path'].max().reset_index(name = 'Max_Path')
df = pd.merge(df, maxroute, on=['Route'], how='inner')
df['Set'] = '1'

df2 = df.copy(deep=True)

df2['Path'] = df2.apply(lambda x: x['Max_Path_y'] + (x['Max_Path_y'] - x['Path']) + 1, axis=1)
df2['Z_miles'] = 0
df2['Set'] = '2'

union = pd.concat([df, df2], ignore_index=True)
print(union)

union.to_csv(os.path.dirname(__file__) + '/df_final_X_Y_Z_E_FLAT_3D.csv', encoding='utf-8', index=False)