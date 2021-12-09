'''
Oskar Garcia - SFSU, CCC, CHEM 667 November 2021
Dec 9
Opens Video mp4 and Track.csv, analyzes aspect ratios and takes screenshots
of each object when their aspect ratio changes too much from the local average

Oskar Garcia CCC, CHEM 667 November 2021
'''

import numpy as np
import cv2
from modifyFindZ_func import *
import os
import sys

#ref AR per obj
def saveCrop(row, data, grayIM): # if an image exceeds max area, just do not save it ************************
    ymax, xmax = grayIM.shape
    clipped = False
    # print('area:', str(data[row,AREA]))
    enlarge = (( data[row,X1] - data[row,X0]) * .5)
    # enlarge = 0 #make it a func based on the size of image, ratiometric | take width of object and double it
    #find width, x1 - x0, take center and increase boundaries by factor
    #also be careful to keep object centered
    _y0 = clamp((int(data[row,Y0] - enlarge)), 0, ymax)
    _y1 = clamp((int(data[row, Y1] + enlarge)), 0, ymax)
    _x0 = clamp((int(data[row,X0] - enlarge)), 0, xmax)
    _x1 = clamp((int(data[row,X1] + enlarge)), 0, xmax)
    name = 'images/detected_' + str(int(data[row,FRAME])) + '_' + str(int(data[row,ID])) + '.jpg'
    cropped_img = grayIM[_y0:_y1, _x0:_x1]
    if (int(data[row,Y0]) - enlarge < 0) or (int(data[row, Y1]) + enlarge > ymax) or (int(data[row,X0]) - enlarge < 0) or (int(data[row,X1]) + enlarge > xmax):
        clipped = True
    if not clipped:
        cv2.imwrite(name, cropped_img)
    # cv2.imshow('croppedGray',cropped_img)
    # cv2.waitKey(500) #was 500
    return clipped



# def reCrop(x0,x1,y0,y1):
    
def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)



########## USER SETTINGS ##############################
vid = sys.argv[1]#'fiveSecondPlankton.mp4'
reco = bool(sys.argv[2])
data = np.loadtxt('Track.csv', delimiter=',',skiprows=1) # Open this and read it to decide which objects to screenshot
# print(len(data))
X_REZ = 640;
Y_REZ = 480;  # viewing resolution
MIN_AREA = 2500  # min area of object detected
# MAX_AREA = 1000  # max area of object detected
THICK = 1  # bounding box line thickness
BLUR = 7  # object bluring to help detection
VGA = (640, 480)
PROCESS_REZ = (320, 240)



############# DEFINE VARIABLES ##################
detectHeader = 'FRAME,ID,X0,Y0,X1,Y1,XC,YC,AREA,AR,ANGLE'
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
detectArray = np.empty((0, MAX_COL), dtype='int')  # detection features populated with object for each frame
imgCount = 0
cap = cv2.VideoCapture(vid) #start reading file
frameCount = 0
thresh = .1
maxObj = np.amax(data[:ID])
# print(maxObj)
lastAR = np.zeros((int(maxObj)))

while cap.isOpened():
    cap.set(cv2.CAP_PROP_POS_FRAMES, frameCount)
    ret, colorIM = cap.read()
    # cv2.imshow('grayTest', colorIM)
    # input()
    grayIM = cv2.cvtColor(colorIM, cv2.COLOR_BGR2GRAY)
    if not ret:
        print('can not find a video or video is finished at', frameCount)
        break
    # colorIM = cv2.resize(colorIM, PROCESS_REZ)
    frameCount += 1
    # print(frameCount)
    # for each object in frame
    # for row in data[data[:,FRAME] == frameCount]:
    rows = np.where(data[:, FRAME] == frameCount)[0] #list of all rows in next frame
    # print(rows, type(rows))
    for row in rows:
        # print(row, data[row,FRAME])
        # grab all previous frames
        # prevData = data[np.logical_and(data[:,FRAME] < frameCount, data[:,ID] == row[ID])]
        # print(prevData)
        # np.sort(prevData, axis= 0) # Sort so latest is available at bottom
        #for row get id and ar, then compare since last
        _id = int(data[row, ID])
        _ar = int(data[row, AR])
        deltaAR = abs(lastAR[_id] - _ar)
        if reco == True:
            grayIM = autoReco(grayIM)
        if deltaAR > thresh and data[row,AREA] > MIN_AREA and not saveCrop(row, data, grayIM):
            lastAR[_id] = _ar
            imgCount += 1

# print('GETIMAGE')
            # print(frameCount)
        if frameCount == np.max(data[:,FRAME]):
            cap.release()

print(imgCount, 'total images')


