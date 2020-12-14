# Written by: Nick Gerend, @dataoutsider
# Viz: "Geo Path", enjoy!

import requests
import urllib
import pandas as pd
import os

df_final_X_Y = pd.read_csv(os.path.dirname(__file__) + '/df_final_X_Y.csv', engine='python')

# USGS Elevation Point Query Service
url = r'https://nationalmap.gov/epqs/pqs.php?'

# # coordinates with known elevation 
# lat = [48.633, 48.733, 45.1947, 45.1962]
# lon = [-93.9667, -94.6167, -93.3257, -93.2755]

# # create data frame
# df = pd.DataFrame({
#     'lat': lat,
#     'lon': lon
# })

def elevation_function(df, lat_column, lon_column):
    """Query service using lat, lon. add the elevation values as a new column."""
    elevations = []
    i = 0
    for lat, lon in zip(df[lat_column], df[lon_column]):

        # define rest query params
        params = {
            'output': 'json',
            'x': lon,
            'y': lat,
            'units': 'Feet'
        }

        # format query string and return query value
        result = requests.get((url + urllib.parse.urlencode(params)))
        print(i)
        i += 1
        elevations.append(result.json()['USGS_Elevation_Point_Query_Service']['Elevation_Query']['Elevation'] / 5280)

    df['Z_miles'] = elevations

#elevation_function(df, 'lat', 'lon')
elevation_function(df_final_X_Y, 'Latitude', 'Longitude')

df_final_X_Y.to_csv(os.path.dirname(__file__) + '/df_final_X_Y_Z.csv', encoding='utf-8', index=False)