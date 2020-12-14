# Written by: Nick Gerend, @dataoutsider
# Viz: "Geo Path", enjoy!

import pandas as pd
import os
import math
pd.options.mode.chained_assignment = None

#region Data
#region Stations
df_s = pd.read_csv(os.path.dirname(__file__) + '/Amtrak_Stations.csv', engine='python')
df_s = df_s.loc[(((df_s['STATE'] == 'TX') & (df_s['STNTYPE'] == 'RAIL')) | (df_s['STNNAME'] == 'Texarkana, Arkansas'))]
df_s = df_s.reset_index(drop=True)
df_s = df_s[['Latitude','Longitude','ADDRESS1','CITY','STATE','ZIP','STNNAME']]
df_s['index'] = df_s['STNNAME']
df_s['MILES'] = ''
df_s['Type'] = 'station'
df_s['Group'] = ''
#endregion

#region Route Points
df_r = pd.read_csv(os.path.dirname(__file__) + '/Amtrak_Routes_Transpose.csv', engine='python')
df_r = df_r.reset_index(drop=True)
df_r = df_r[['MILES','Latitude','Longitude','FRFRANODE','TOFRANODE','OBJECTID','index']]
df_r['ADDRESS1'] = ''
df_r['CITY'] = ''
df_r['STATE'] = 'TX'
df_r['ZIP'] = ''
df_r['STNNAME'] = ''
df_r['Type'] = 'route'

# -- Add Fork Data
df_r['from'] = df_r['FRFRANODE']
df_r['to'] = df_r['TOFRANODE']
# -- Fort Worth
df_r['to'][df_r['OBJECTID']==8272] = 'FW_ST'
df_r['from'][df_r['OBJECTID']==8273] = 'FW_S'
df_r['from'][df_r['OBJECTID']==8270] = 'FW_SE'
# -- San Antonio
df_r['to'][df_r['OBJECTID']==3809] = 'SA_N'
df_r['to'][df_r['OBJECTID']==3808] = 'SA_ST'
df_r['from'][df_r['OBJECTID']==3810] = 'SA_E'

df_r['Group'] = ''
#endregion

#region From-To Route Directions
df_ft = pd.read_csv(os.path.dirname(__file__) + '/From_To.csv', engine='python')
df_ft['From_Lat'] = 0.0
df_ft['From_Long'] = 0.0
df_ft['To_Lat'] = 0.0
df_ft['To_Long'] = 0.0
#endregion
#endregion

#region Functions
def delta_latitude(miles):
    earth_radius = 3958.8
    radians_to_degrees = 180.0/math.pi
    return (miles/earth_radius)*radians_to_degrees

def delta_longitude(latitude, miles):
    earth_radius = 3958.8
    radians_to_degrees = 180.0/math.pi
    degrees_to_radians = math.pi/180.0
    r = earth_radius*math.cos(latitude*degrees_to_radians)
    return (miles/r)*radians_to_degrees

def haversine_miles(lat1, lon1, lat2, lon2):    
    degrees_to_radians = math.pi/180.0
    dLat = (lat2 - lat1) * degrees_to_radians
    dLon = (lon2 - lon1) * degrees_to_radians
    lat1 = (lat1) * degrees_to_radians
    lat2 = (lat2) * degrees_to_radians
    h = (pow(math.sin(dLat / 2), 2) + pow(math.sin(dLon / 2), 2) * math.cos(lat1) * math.cos(lat2))
    earth_radius = 3958.8
    return  2 * earth_radius * math.asin(math.sqrt(h)) 

def heading(lat1, lon1, lat2, lon2):
    degrees_to_radians = math.pi/180.0
    radians_to_degrees = 180.0/math.pi
    lat1 = (lat1) * degrees_to_radians
    lat2 = (lat2) * degrees_to_radians
    dLon = (lon2 - lon1) * degrees_to_radians
    X = math.cos(lat2) * math.sin(dLon)
    Y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
    bearing_degrees = math.atan2(X,Y) * radians_to_degrees
    return (bearing_degrees + 360) % 360

def chain(df, to_, from_):
    u_vals = (df[to_].append(df[from_])).unique()
    val_2_index = {}
    index_2_val = {}   
    i = 0
    for val in u_vals:
        val_2_index[val] = i
        index_2_val[i] = val
        i += 1
    df['to_id'] = df[to_].replace(val_2_index)
    df['from_id'] = df[from_].replace(val_2_index)
    groups= []
    for i in range(len(u_vals)):
        groups.append({i})
    for index, row in df.iterrows():
        union = groups[row['from_id']]|groups[row['to_id']]
        for p in union:
            groups[p]=union
    sets= set()
    for g in groups:
        sets.add(tuple(g))
    sets_final= set()
    for s in sets:
        L = list(s)
        for i in range(len(L)):
            L[i] = index_2_val[s[i]]
        sets_final.add(tuple(L))
    return(sets_final)

def nearest_index(df, lat_col, lon_col, lat, lon, search_box_miles):
    
    #region Create box around the From station and identify route points
    lat_min = lat - delta_latitude(search_box_miles)
    lat_max = lat + delta_latitude(search_box_miles)
    long_min = lon - delta_longitude(lat, search_box_miles)
    long_max = lon + delta_longitude(lat, search_box_miles)
    df_box = df.loc[(df[lat_col] >= lat_min) & (df[lat_col] <= lat_max) & (df[lon_col] >= long_min) & (df[lon_col] <= long_max)].copy()
    df_r.to_csv(os.path.dirname(__file__) + '/df_r.csv', encoding='utf-8', index=False)
    # df_box['dist_from'] = 0.0
    # for index, row in df_box.iterrows():
    #     row['dist_from'] = haversine_miles(row[lat_col], row[lon_col], lat, lon)
    df_box['dist_from'] = df_box.apply(lambda x: haversine_miles(x[lat_col], x[lon_col], lat, lon), axis=1)
    # endregion

    #region Identify the (best) route point closest to the "From" Station and it's distance to the "To" Station
    min_dist = df_box['dist_from'].min() # identify the route location's (with the minimum distance between itself and the station,"From") distance
    df_box_min = df_box.loc[(df_box['dist_from'] == min_dist)] # use this distance to extract the route's record from the original df   
    route_point_ID = df_box_min.index._values[0] # select the record ID
    #endregion

    return route_point_ID, df_box
#endregion

#region Group the Routes

# # -- Collect Forks:
# SanAntonio_Fork = nearest_index(df_r, 'Latitude', 'Longitude', 29.435131, -98.442696, 10)
# Dallas_Fork = nearest_index(df_r, 'Latitude', 'Longitude', 32.744918, -97.321524, 10)

# -- Chain from-to
chains = chain(df_r, 'from', 'to')

i_chain = 0
for chain in chains:
    df_r['Group'][df_r['from'].isin(chain) | df_r['to'].isin(chain)] = i_chain
    i_chain += 1
# -- df_r.to_csv(os.path.dirname(__file__) + '/df_r.csv', encoding='utf-8', index=False)
#endregion

#region Combine Datasets
df_r_s = pd.concat([df_r, df_s], ignore_index=True)
df_r_s['Crawled'] = 'No'
df_r_s['Path'] = -1
df_r_s['Route'] = ''
df_r_s['Elevation'] = 0.0
df_final = df_r_s[0:0]
path = 0
last_stop = ''
final_stop = ''
#endregion

df_r_s.to_csv(os.path.dirname(__file__) + '/df_routes_and_stations.csv', encoding='utf-8', index=False)
