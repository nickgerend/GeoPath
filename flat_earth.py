# Written by: Nick Gerend, @dataoutsider
# Viz: "Geo Path", enjoy!

import pandas as pd
import os
import math
pd.options.mode.chained_assignment = None

df_final = pd.read_csv(os.path.dirname(__file__) + '/df_final_X_Y_Z_E.csv', engine='python')

def flat_sphere_xyz(lat, lon, ele, xyz):
    degrees_to_radians = math.pi/180.0
    
    theta = lat * degrees_to_radians
    phi = lon * degrees_to_radians
    earth_radius = 3958.8 + ele

    x = earth_radius * math.cos(theta) * math.cos(phi)
    y = earth_radius * math.cos(theta) * math.sin(phi)
    z = earth_radius * math.sin(theta)

    return { 'x': x, 'y': y, 'z': z }.get(xyz, 0)

df_final['X_flat'] = df_final.apply(lambda x: flat_sphere_xyz(x['Latitude'], x['Longitude'], x['Z_miles'], 'x'), axis=1)
df_final['Y_flat'] = df_final.apply(lambda x: flat_sphere_xyz(x['Latitude'], x['Longitude'], x['Z_miles'], 'y'), axis=1)
df_final['Z_flat'] = df_final.apply(lambda x: flat_sphere_xyz(x['Latitude'], x['Longitude'], x['Z_miles'], 'z'), axis=1)

df_final.to_csv(os.path.dirname(__file__) + '/df_final_X_Y_Z_E_FLAT.csv', encoding='utf-8', index=False)