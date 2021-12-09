'''
Oskar Garcia - SFSU, CCC, CHEM 667 November 2021
Dec 9
Applies a fixed threshold to a blurred image of each video frame to create binary objects.
Draw bounding box around binary objects in each frame of video and saves location, area and aspect ratio for tracking.

Use keyboard to adjust threshold. Click on image to enable keyboard.
Press 't' to select threshold. Press '+' and '-' to change value by increments of 1.
Hold shift while pressing '+' or '-' to change value by increments of 10. 
Press 'q' to quit

v2 09.02.2021 Uses keyboard to change variables
v1 08.31.2020

Tom Zimmerman CCC, IBM Research March 2020
This work is funded by the National Science Foundation (NSF) grant No. DBI-1548297, Center for Cellular Construction.
Disclaimer:  Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation.
'''
import numpy as np
import cv2
import keyboard as k     # reads keyboard and updates program variable with key presses
import os
import sys
print(sys.argv)


########## USER SETTINGS ##############################
vid= sys.argv[1]

detectFileName='detection.csv'      # output file containing object location, area, aspect ratio for each video frame
X_REZ=640; Y_REZ=480;               # viewing resolution
MIN_AREA=100                         # min area of object detected
MAX_AREA=1000                       # max area of object detected
THICK=1                             # bounding box line thickness
BLUR=7                              # object bluring to help detection
VGA=(640,480)
PROCESS_REZ=(320,240)
    
############# DEFINE VARIABLES ##################
detectHeader= 'FRAME,ID,X0,Y0,X1,Y1,XC,YC,AREA,AR,ANGLE'
FRAME=0; ID=1;  X0=2;   Y0=3;   X1=4;   Y1=5;   XC=6;   YC=7; AREA=8; AR=9; ANGLE=10; MAX_COL=11 # pointers to detection features
detectArray=np.empty((0,MAX_COL), dtype='float')  # detection features populated with object for each frame

################### MAIN ###################
#print('''
'''How to use keyboard to adjust threshold.....
Click on image to enable keyboard.
Press 't' to select threshold.
Press '+' and '-' to change value by increments of 1.
Hold shift while pressing '+' or '-' to change value by increments of 10. 
Press 'q' to quit
'''#)


def progresspercent(frame, length):
    if (int(frame) % (int(length) / 10) == 0):
        print(str((frame / length) * 100) + "%")


def getAR(obj):
    ((xc,yc),(w,h),(angle)) = cv2.minAreaRect(obj)  # get parameters from min area rectangle
    ar=0.0      # initialize aspect ratio as a floating point so calculations are done in floating point
    # calculate aspect ratio (always 1 or greater)
    if w>=h and h>0:
        ar=float(w)/float(h)
    elif w>0:
        ar=float(h)/(w)
    return(xc,yc,ar,angle)         

######### start capturing frames of video #############
cap = cv2.VideoCapture(vid)         # start video file reader
length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frameCount=0                        # keeps track of frame number
while(cap.isOpened() and k.run):    # process each frame until end of video or 'q' key is pressed
    progresspercent(frameCount, length)
    # check for key activity that changes program variables
    (thresh,b,x,y)=k.processKey()   # b,x,y variables currently not used, just put in there to show usage
    
    # get image
    ret, colorIM = cap.read()
    if not ret:                     # check to make sure there was a frame to read
        print('Can not find video or we are all done')
        break
    frameCount+=1
    
    # blur and threshold image
    # colorIM=cv2.resize(colorIM,PROCESS_REZ)
    grayIM = cv2.cvtColor(colorIM, cv2.COLOR_BGR2GRAY)  # convert color to grayscale image       
    blurIM=cv2.medianBlur(grayIM,BLUR)                  # blur image to fill in holes to make solid object
    ret,binaryIM = cv2.threshold(blurIM,thresh,255,cv2.THRESH_BINARY_INV) # threshold image to make pixels 0 or 255
    
    # get contours  
    contourList, hierarchy = cv2.findContours(binaryIM, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # all countour points, uses more memory
    
    # draw bounding boxes around objects
    objCount=0                                      # used as object ID in detectArray
    for objContour in contourList:                  # process all objects in the contourList
        area = int(cv2.contourArea(objContour))     # find obj area
        # print(area)
        if area>MIN_AREA:                           # only detect large objects       
            PO = cv2.boundingRect(objContour)
            x0=PO[0]; y0=PO[1]; x1=x0+PO[2]; y1=y0+PO[3]
            cropped_image = colorIM[(y0):(y1), (x0):(x1), :]
            cv2.rectangle(colorIM, (x0,y0), (x1,y1), (0,255,0), THICK) # place GREEN rectangle around each object, BGR
            (xc,yc,ar,angle)=getAR(objContour)
            # print(type(ar))
            # if frameCount <= 100:
                # print(frameCount,ar,xc*yc)
            # print("x " , x0,x1,y0,y1, ar)

            # cv2.imshow("cropped", cv2.resize(cropped_image,VGA))

            # save object parameters in detectArray in format FRAME=0; ID=1;  X0=2;   Y0=3;   X1=4;   Y1=5;   XC=6;   YC=7; CLASS=8; AREA=9; AR=10; ANGLE=11; MAX_COL=12
            parm=np.array([[frameCount,objCount,x0,y0,x1,y1,xc,yc,area,ar,angle]],dtype='float') # create parameter vector (1 x MAX_COL)
            detectArray=np.append(detectArray,parm,axis=0)  # add parameter vector to bottom of detectArray, axis=0 means add row
            objCount+=1                                     # indicate processed an object
    #print('frame:',frameCount,'objects:',len(contourList),'big objects:',objCount)

    # shows results
    #print(cropped_image.shape, colorIM.shape)
    #cv2.imshow("cropped", cropped_image)

    cv2.imshow('colorIM', cv2.resize(colorIM,VGA))      # display image
    # cv2.imshow('blurIM', cv2.resize(blurIM,VGA))# display thresh image
    # cv2.imshow('binaryIM', cv2.resize(binaryIM,VGA))# display thresh image
    # break
# program ending, test why
if frameCount>0:            # normal ending, save detection file
    print('Done with video. Saving feature file and exiting program')
    np.savetxt(detectFileName,detectArray,header=detectHeader,delimiter=',', fmt='%10.5f')#fmt='%d' was original but resulted in only saving values as int
    cap.release()
else:                       # abnormal ending, don't save detection file
    print('Count not open video',vid)
    
cv2.destroyAllWindows()     # clean up to end program
print('bye!')               # tell the user program has ended

print(len(detectArray))







