# Written by: Nick Gerend, @dataoutsider
# Viz: "Geo Path", enjoy!

import pandas as pd
import os
import math
pd.options.mode.chained_assignment = None

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
    df_box = df.loc[(df[lat_col] >= lat_min) & (df[lat_col] <= lat_max) & (df[lon_col] >= long_min) & (df[lon_col] <= long_max)].copy(deep=True)
    df_box['dist_from'] = df_box.apply(lambda x: haversine_miles(x[lat_col], x[lon_col], lat, lon), axis=1)
    # endregion

    #region Identify the (best) route point closest to the "From" Station and it's distance to the "To" Station
    min_dist = df_box['dist_from'].min() # identify the route location's (with the minimum distance between itself and the station,"From") distance
    df_box_min = df_box.loc[(df_box['dist_from'] == min_dist)] # use this distance to extract the route's record from the original df   
    route_point_ID = df_box_min.index._values[0] # select the record ID
    #endregion

    return route_point_ID, df_box
#endregion

#region Load Data
df_r_s = pd.read_csv(os.path.dirname(__file__) + '/df_routes_and_stations.csv', engine='python')
df_ft = pd.read_csv(os.path.dirname(__file__) + '/From_To.csv', engine='python')

df_final = df_r_s[0:0]
path = 0
last_stop = ''
final_stop = ''
#endregion

for index, row in df_ft.iterrows():
    
    #region box around the station
    lat_from = df_r_s.loc[(df_r_s['STNNAME'] == row['From'])]['Latitude']._values[0]
    long_from = df_r_s.loc[(df_r_s['STNNAME'] == row['From'])]['Longitude']._values[0]
    df_r_index, df_box = nearest_index(df_r_s, 'Latitude', 'Longitude', lat_from, long_from, 10)
    #endregion

    #region distance to end station
    lat_to = df_r_s.loc[(df_r_s['STNNAME'] == row['To'])]['Latitude']._values[0]
    long_to = df_r_s.loc[(df_r_s['STNNAME'] == row['To'])]['Longitude']._values[0]
    df_box['dist_to'] = df_box.apply(lambda x: haversine_miles(x['Latitude'], x['Longitude'], lat_to, long_to), axis=1)
    #endregion

    #region clip points outside of station
    s_to_s_distance = df_box.loc[(df_box['dist_from'] == 0)]['dist_to']._values[0]
    clip_points = df_box.loc[(df_box['dist_to'] > s_to_s_distance)]['index']._values
    #endregion

    #region collect route data to crawl
    groups = list(map(int, row['Group'].split(",")))
    df_ft_route = df_r_s.loc[(df_r_s['Group'].isin(groups) & ~df_r_s['index'].isin(clip_points)) | (df_r_s['Type'] == 'station')].copy(deep=True)
    df_ft_route.to_csv(os.path.dirname(__file__) + '/df_ft_route_TEST1.csv', encoding='utf-8', index=False)
    #endregion

    #region crawl
    node = df_r_s.loc[(df_r_s['STNNAME'] == row['From'])]['index']._values[0]
    df_remaining = df_r_s
    path = 0
    last_stop = node
    final_stop = df_r_s.loc[(df_r_s['STNNAME'] == row['To'])]['index']._values[0]

    for index_2, row_2 in df_ft_route.iterrows():
        
        #region Add entry to the final table
        entry = df_remaining.loc[df_remaining['index'] == node]
        type_ = entry['Type']._values[0]        
        
        #---
        if (path > 0 and type_ == 'station'):
            # Final route point:
            entry['Path'] = path
            entry['Route'] = ''
            df_final = df_final.append([entry],ignore_index=True)
            # Reset and finalize route name:
            path = 0
            df_final['Route'][(df_final['Route'] == '')] = last_stop + ' to ' + node
            last_stop = node
            if node == final_stop:
                break
        #---

        entry['Path'] = path
        entry['Route'] = ''
        df_final = df_final.append([entry],ignore_index=True)
        path += 1
        #endregion

        #region Identify the next node
        lat_entry = entry['Latitude']._values[0]
        long_entry = entry['Longitude']._values[0]
        df_ft_route['Crawled'][df_ft_route['index']==node] = 'Yes'
        df_remaining = df_ft_route.loc[(df_ft_route['Crawled'] == 'No')]      
        next_index, df_box = nearest_index(df_remaining, 'Latitude', 'Longitude', lat_entry, long_entry, 10)
        next_entry = df_box.loc[[next_index]]['index']._values[0]     
        node = next_entry
        print(path)
        #endregion

df_final.to_csv(os.path.dirname(__file__) + '/df_final2.csv', encoding='utf-8', index=False)