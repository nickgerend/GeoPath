import pandas as pd
import os
import math
pd.options.mode.chained_assignment = None

#region Functions

def sphere_distance_miles(lat1, lon1, ele1, lat2, lon2, ele2):
    degrees_to_radians = math.pi/180.0
    theta1 = lat1 * degrees_to_radians
    phi1 = lon1 * degrees_to_radians
    theta2 = lat2 * degrees_to_radians
    phi2 = lon2 * degrees_to_radians

    earth_radius1 = 3958.8 + ele1
    earth_radius2 = 3958.8 + ele2

    x1 = earth_radius1 * math.cos(theta1) * math.cos(phi1)
    x2 = earth_radius2 * math.cos(theta2) * math.cos(phi2)
    y1 = earth_radius1 * math.cos(theta1) * math.sin(phi1)
    y2 = earth_radius2 * math.cos(theta2) * math.sin(phi2)
    z1 = earth_radius1 * math.sin(theta1)
    z2 = earth_radius2 * math.sin(theta2)

    distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)
    return distance

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

def cross_track_distance_miles(start_lat, start_lon, end_lat, end_lon, point_lat, point_lon):
    earth_radius = 3958.8
    degrees_to_radians = math.pi/180.0
    start_point_angular_distance = haversine_miles(start_lat, start_lon, point_lat, point_lon) / earth_radius
    start_end_bearing = heading(start_lat, start_lon, end_lat, end_lon)
    start_point_bearing = heading(start_lat, start_lon, point_lat, point_lon)    
    delta_bearing = (start_point_bearing - start_end_bearing) * degrees_to_radians
    XT_distance = math.asin(math.sin(start_point_angular_distance) * math.sin(delta_bearing)) * earth_radius
    return XT_distance

def along_track_dstance_miles(start_lat, start_lon, end_lat, end_lon, point_lat, point_lon):
    earth_radius = 3958.8
    start_point_angular_distance = haversine_miles(start_lat, start_lon, point_lat, point_lon) / earth_radius
    XT_angular_distance = cross_track_distance_miles(start_lat, start_lon, end_lat, end_lon, point_lat, point_lon) / earth_radius
    AT_distance = math.acos(math.cos(start_point_angular_distance)/math.cos(XT_angular_distance)) * earth_radius
    return AT_distance
#endregion

df_final = pd.read_csv(os.path.dirname(__file__) + '/df_final2.csv', engine='python')

maxpath = df_final.groupby(['Route'])['Path'].max().reset_index(name = 'Max_Path')
df_final = pd.merge(df_final, maxpath, on=['Route'], how='inner')
df_final['Slat_i'] = df_final.apply(lambda x: x['Latitude'] if x['Path'] == 0 else -9999, axis=1)
df_final['Slong_i'] = df_final.apply(lambda x: x['Longitude'] if x['Path'] == 0 else -9999, axis=1)
df_final['Elat_i'] = df_final.apply(lambda x: x['Latitude'] if x['Path'] == x['Max_Path'] else -9999, axis=1)
df_final['Elong_i'] = df_final.apply(lambda x: x['Longitude'] if x['Path'] == x['Max_Path'] else -9999, axis=1)

maxcoord = df_final.groupby(['Route'])['Slat_i', 'Slong_i', 'Elat_i', 'Elong_i'].max().reset_index()
df_final = pd.merge(df_final, maxcoord, on=['Route'], how='inner')

df_final['X'] = df_final.apply(lambda x: cross_track_distance_miles(x['Slat_i_y'], x['Slong_i_y'], x['Elat_i_y'], x['Elong_i_y'], x['Latitude'], x['Longitude']), axis=1)
df_final['Y'] = df_final.apply(lambda x: along_track_dstance_miles(x['Slat_i_y'], x['Slong_i_y'], x['Elat_i_y'], x['Elong_i_y'], x['Latitude'], x['Longitude']), axis=1)
df_final['X'] = df_final.apply(lambda x: 0 if x['Path'] == -0 else x['X'], axis=1)
df_final['Y'] = df_final.apply(lambda x: 0 if x['Path'] == -0 else x['Y'], axis=1)

#df_final.to_csv(os.path.dirname(__file__) + '/df_final_X_Y.csv', encoding='utf-8', index=False)