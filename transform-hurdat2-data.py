#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Juanma Lora
"""
import csv
import json
import matplotlib.path as mplPath
import numpy as np

inputFilename   = "data/hurdat2-1851-2018-120319.txt"
outputFilename  = "data/hurdat2-formattted.csv"
caribbeanJsonData = "data/caribbean-polygon.json"

HEADER_ROW_FIELDS = 4 # Header rows have 4 fields
DATA_ROW_FIELDS   = 21  # Data rows have 21 fields

loadedCount = 0
writtenCount = 0
unprocessedRows = 0
hurrycanes = 0
coordsOnGround = 0
coordsOnSea = 0

# Create a MatPlotLib Path from an coordinates array
def createPolygonFromGeoJson(polygon):
    return mplPath.Path(polygon)

# Returns 1 if coordinate is on the ground
def isCoordOnGround(coordinate, mplpath):
    return str(int(not mplpath.contains_point((float(coordinate[0]), float(coordinate[1])))))

with open(caribbeanJsonData) as jsonFile:
    caribbeanData = json.load(jsonFile)

coordinates = caribbeanData['features'][0]['geometry']['coordinates'][0]
caribbeanPath = createPolygonFromGeoJson(coordinates)

outputFile = open(outputFilename, 'w')
writer = csv.writer(outputFile)

headers = "Identifier;Name;Date;Time;Land;System Status;Longitude;Latitude;Max wind;Min pressure;34 kt wind northeastern;34 kt wind radii southeastern;34 kt wind radii southwestern;34 kt wind radii southwestern;50 kt wind northeastern;50 kt wind radii southeastern;50 kt wind radii southwestern;50 kt wind radii southwestern;64 kt wind northeastern;64 kt wind radii southeastern;64 kt wind radii southwestern;64 kt wind radii southwestern"
outputFile.write(headers + "\n")

with open(inputFilename, newline='') as csvFile:
    csvData = csv.reader(csvFile, delimiter=',')

    headerRow = []
    dataRow = []

    for index, row in enumerate(csvData):
        loadedCount += 1
        if (len(row) == HEADER_ROW_FIELDS):
            headerRow = row[:len(row) - 1]
            hurrycanes += 1
        elif (len(row) == DATA_ROW_FIELDS):
            rowToWrite = headerRow + row[:len(row) - 1]
            rowToWrite = [s.strip() for s in rowToWrite] # Remove spaces

            # Transform coordinates
            transformedLat = str(float(rowToWrite[7][:-1]))
            transformedLon = str(-float(rowToWrite[8][:-1]))
            rowToWrite[7] = transformedLon
            rowToWrite[8] = transformedLat

            coordOnGround = isCoordOnGround(rowToWrite[7:9], caribbeanPath)
            coordsOnGround += 1 if coordOnGround == '1' else 0
            coordsOnSea    += 0 if coordOnGround == '1' else 1

            # Remove columns 'Rows' and 'Record Identifier'
            rowToWrite.pop(2)
            rowToWrite.pop(4)

            rowToWrite.insert(4, coordOnGround)

            outputFile.write(";".join(rowToWrite) + "\n")
            writtenCount += 1
        else:
            print("Undefined row at index {}".format(index))
            unprocessedRows += 1

outputFile.close()

print("**********************************")
print("Process finished:")
print("\tLoaded rows: {}".format(loadedCount))
print("\tWritten rows: {}".format(writtenCount))
print("\tUnprocessed rows: {}".format(unprocessedRows))
print("\tTotal hurrycanes: {}".format(hurrycanes))
print("\tTotal coordinates on ground: {}".format(coordsOnGround))
print("\tTotal coordinates on sea: {}".format(coordsOnSea))
print("\tTotal coordinates analyzed: {}".format(coordsOnSea + coordsOnGround))
print("**********************************")
