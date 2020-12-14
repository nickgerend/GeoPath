# Written by: Nick Gerend, @dataoutsider
# Viz: "Geo Path", enjoy!

import pandas as pd
import os
import math
pd.options.mode.chained_assignment = None

df_final = pd.read_csv(os.path.dirname(__file__) + '/df_final_X_Y_Z_E_FLAT.csv', engine='python')

df_final['Flat_Traveled'] = df_final.groupby('Route')['Flat_Miles_Travled'].transform(pd.Series.cumsum)
df_final['Elevation_Traveled'] = df_final.groupby('Route')['Elevaiton_Miles_Travled'].transform(pd.Series.cumsum)
print(df_final)

df_final.to_csv(os.path.dirname(__file__) + '/df_final_X_Y_Z_E_FLAT.csv', encoding='utf-8', index=False)