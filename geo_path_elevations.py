# Written by: Nick Gerend, @dataoutsider
# Viz: "Geo Path", enjoy!

import pandas as pd
import os
import math
pd.options.mode.chained_assignment = None

def avg_elevation_haversine_miles(lat1, lon1, lat2, lon2, avg_elev_miles):
    degrees_to_radians = math.pi/180.0
    dLat = (lat2 - lat1) * degrees_to_radians
    dLon = (lon2 - lon1) * degrees_to_radians
    lat1 = (lat1) * degrees_to_radians
    lat2 = (lat2) * degrees_to_radians
    h = (pow(math.sin(dLat / 2), 2) + pow(math.sin(dLon / 2), 2) * math.cos(lat1) * math.cos(lat2))
    earth_radius = 3958.8 + avg_elev_miles
    return  2 * earth_radius * math.asin(math.sqrt(h)) 

def haversine_miles(lat1, lon1, lat2, lon2):
    degrees_to_radians = math.pi/180.0
    dLat = (lat2 - lat1) * degrees_to_radians
    dLon = (lon2 - lon1) * degrees_to_radians
    lat1 = (lat1) * degrees_to_radians
    lat2 = (lat2) * degrees_to_radians
    h = (pow(math.sin(dLat / 2), 2) + pow(math.sin(dLon / 2), 2) * math.cos(lat1) * math.cos(lat2))
    earth_radius = 3958.8
    return  2 * earth_radius * math.asin(math.sqrt(h)) 

df_final = pd.read_csv(os.path.dirname(__file__) + '/df_final_X_Y_Z.csv', engine='python')
df_final['Flat_Miles_Travled'] = 0
df_final['Elevaiton_Miles_Travled'] = 0

final_group = df_final.groupby(['Route'])
check = 0
for group in final_group:
    df_group = group[1]
    for i in range(1, len(df_group)):
        g_start_lat = df_group.loc[(df_group['Path'] == i-1)]['Latitude']._values[0]
        g_start_long = df_group.loc[(df_group['Path'] == i-1)]['Longitude']._values[0]
        g_end_lat = df_group.loc[(df_group['Path'] == i)]['Latitude']._values[0]
        g_end_long = df_group.loc[(df_group['Path'] == i)]['Longitude']._values[0]
        g_start_elev = df_group.loc[(df_group['Path'] == i-1)]['Z_miles']._values[0]
        g_end_elev = df_group.loc[(df_group['Path'] == i)]['Z_miles']._values[0]
        avg_elevation = (g_start_elev + g_end_elev) / 2

        dist = haversine_miles(g_start_lat, g_start_long, g_end_lat, g_end_long)
        avg_dist = avg_elevation_haversine_miles(g_start_lat, g_start_long, g_end_lat, g_end_long, avg_elevation)

        df_final['Flat_Miles_Travled'][(df_final['Path']==i) & (df_final['Route']==group[0])] = dist
        df_final['Elevaiton_Miles_Travled'][(df_final['Path']==i) & (df_final['Route']==group[0])] = avg_dist
    print(check)
    check += 1
    # if check == 3:
    #     break

#print(df_final)
df_final.to_csv(os.path.dirname(__file__) + '/df_final_X_Y_Z_E.csv', encoding='utf-8', index=False)