#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oskar Garcia - SFSU, CCC, CHEM 667 November 2021
Dec 9
HW6Task3_helper

This code matches the object in a second frame to the closest object in the first frame and copies the ID of the closest object in the first frame to the ID of the object in the second frame.

For HW6 Task 3 you need to modify this code so it works over all the frames in the video and saves the modified data array at track.csv (hint, use np.savetxt() command)
I've also included a flag ASSIGNED you can use so you don't assign an ID to more than one object.

Thomas Zimmerman, IBM Research-Almaden
This work is funded by the National Science Foundation (NSF) grant No. DBI-1548297, Center for Cellular Construction.
Disclaimer:  Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation. 
"""

import numpy as np
import math

outputFileName = 'track.csv'
detectFileName = 'detection.csv'  # output file containing object location, area, aspect ratio for each video frame
FRAME = 0;
ID = 1;
X0 = 2;
Y0 = 3;
X1 = 4;
Y1 = 5;
XC = 6;
YC = 7;
AREA = 8;
AR = 9;
ANGLE = 10;
MAX_COL = 11  # pointers to detection features


################# FUNCTION ###################
def distance(x2, y2, x1, y1):
    """calculate the distance of the objects in current frame to 
    objects in past frame"""
    return (math.sqrt((int(x2) - int(x1)) ** 2 + (int(y2) - int(y1)) ** 2))


#################### MAIN ####################
data = np.loadtxt(detectFileName, delimiter=',', skiprows=1)
print('data shape', data.shape)

maxFrames = len(np.unique(data[:, FRAME]))
print('max frames', maxFrames)

# get index of all rows with the frame we are interested in
# np.where returns a tuple containing an array, so we get to the array by rquesting the first element of the tuple with [0]
# for a detailed explaination of why np.where returns a tuple, see https://stackoverflow.com/questions/50646102/what-is-the-purpose-of-numpy-where-returning-a-tuple
# a = np.where(data[:, FRAME] == 1)
f1 = np.where(data[:, FRAME] == 1)[0]
# f2 = np.where(data[:, FRAME] == 2)[0]
# print('objects in frame2=', len(f1), 'objects in frame1=', len(f1), '\n')
# comboArray = np.zeros((objPrevFrame,3))
latestID = len(f1)
for frame in range(maxFrames - 1):
    # print('now in frame ', frame)
    f2 = np.where(data[:, FRAME] == frame + 1)[0] #list of all rows in next frame
    f1 = np.where(data[:, FRAME] == frame)[0] #ditto in first frame
    #for all objects in next frame calc dist in prev frame
    # for obj2 in f2:
    #     for obj1 in f1:
    # print(frame,obj1,obj2)
    xc2 = data[f2,XC]
    # print(xc2)
    xc1 = data[f1,XC]
    yc1 = data[f1,YC]
    yc2 = data[f2,XC]
    id1 = data[f1,ID]
    id2 = data[f2,ID]
    objCurrFrame = len(f2)
    objPrevFrame = len(f1)
    assigned = []
    if(objPrevFrame > 0 and objCurrFrame > 0):
        for j in range(objCurrFrame):
            x2 = xc2[j]
            y2 = yc2[j]
            index = 0

            minDist = 9999
            bestID = 0
            for k in range(objPrevFrame):# maybe use a mask here and another array with ID's to be ignored to filter out the previous IDs
                x1 = xc1[k]
                y1 = yc1[k]
                d = distance(x2,y2,x1,y1)
                # print(frame, j,k,d)
                if(d < minDist and id1[k] not in assigned): #Checks to see if object is close to others in previous frame but it's ID is not assigned to another object
                    bestID = id1[k]
                    minDist = d
            if bestID not in assigned:
                data[f2[j],ID] = bestID
                assigned.append(bestID)
            else:
                latestID += 1
                data[f2[j], ID] = latestID
# print(data[50:])
# print(np.unique(data[:,1]))
detectHeader= 'FRAME,ID,X0,Y0,X1,Y1,XC,YC,AREA,AR,ANGLE'

np.savetxt(outputFileName, data,header=detectHeader, delimiter=',', fmt='%d')

