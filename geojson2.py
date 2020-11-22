import json
import csv
import argparse
import sys
import os


def main():
    with open(os.path.dirname(__file__) + '/Amtrak_Stations.geojson') as json_file: 
        geojson_data = json.load(json_file) 
    if geojson_data['type'] == 'FeatureCollection':
        out = open(os.path.dirname(__file__) + '/Amtrak_Stations.csv', 'w') 
        parse_feature_collection(geojson_data['features'], out)
    else:
        print("Can currently only parse FeatureCollections, but I found ", geojson_data['type'], " instead")


def parse_feature_collection(features, outfile):

    # create the csv writer object
    csvwriter = csv.writer(outfile, lineterminator='\n') #, lineterminator='\n'os.linesep

    count = 0
    header = []
    for feature in features:
        if count == 0:
            header = list(feature['properties'].keys())
            header.extend(['Longitude', 'Latitude'])
            csvwriter.writerow(header)
            count += 1
        csvwriter.writerow(feature_to_row(feature, feature['properties'].keys()))
    outfile.close()

def feature_to_row(feature, header):
    l = []
    for k in header:
        l.append(feature['properties'][k])
    l.append(feature['geometry']['coordinates'][0])
    l.append(feature['geometry']['coordinates'][1])
    return l


if __name__ == "__main__":
    main()