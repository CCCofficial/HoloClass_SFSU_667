# -*- coding: utf-8 -*-
"""
Detect script but for images
Created on Tue Oct 12 12:18:53 2021

@author: salma

v4.1
User can choose the csv filename and where they want to save it

v4.0
Some buttons were replaced with a scale (scrolling bar)

v3.0
Replaced the keyboard keys with mouse buttons

v2.0
The keyboard module was added to adjust parameters. Keys such as 'n' and 's' were
added in order to go to the next image and save the object parameters respectively.
This also includes the image name in the csv file

v1.0
This script should detect objects for an image. In the future, it might be a module
added to the final detect script?
"""
import cv2
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import warnings

warnings.filterwarnings('ignore')
#################### CSV FILE NAME AND IMAGE RES ##############################

X_REZ=640; Y_REZ=480;               # viewing resolution
THICK=1                             # bounding box line thickness
BLUR=7                              # object bluring to help detection
VGA=(640,480)
PROCESS_REZ=(320,240)
window=[0,Y_REZ,0,X_REZ]
    
############################ DEFINE VARIABLES ################################
detectHeader= 'IMAGE_NAME,ID,X0,Y0,X1,Y1,XC,YC,AREA,AR,ANGLE'
detectHeader= detectHeader.split(',')
#print(detectHeader)
FRAME=0; ID=1;  X0=2;   Y0=3;   X1=4;   Y1=5;   XC=6;   YC=7; AREA=8; AR=9; ANGLE=10; MAX_COL=11 # pointers to detection features
#detectArray=np.empty((0,MAX_COL))  # detection features populated with object for each frame
detectList = []

#variables associated with buttons (originally with keystrokes) and the starting values
#thresh = 50
#MIN_AREA = 50
#MAX_AREA = 1500
skip_im = 1     # goes to the next image (the word "next" is already a keyword)
save = 0        # saves the objects detected to the csv file
show_welcome_wid = True

########################## DEFINING FUNCTIONS IN ORDER ############################
def getImage():
    global root, file
    root = tk.Tk()
    #widget with welcome message
    root.title('Start program')
    label = tk.Label(root, text = welcome_message, justify = 'left')
    label.pack()
    if show_welcome_wid == False:
        root.withdraw()
    cv2.waitKey(1000)
    file = filedialog.askopenfilename() #the file you choose is in the form of the pathway string
    if show_welcome_wid == True:
        root.withdraw()
    
    try:
        image = cv2.imread(file)
        return image
    except AttributeError:
        return 'Must be a jpg or a png!'

#function to name image (for 1st column in the csv file)
def csv_image_name(filename):
    filename = filename[:-4]
    split_file = filename.split('/')
    return split_file[-1]

#get objects (contouring)
def getAR(obj):
    ((xc,yc),(w,h),(angle)) = cv2.minAreaRect(obj)  # get parameters from min area rectangle
    ar=0.0      # initialize aspect ratio as a floating point so calculations are done in floating point
    # calculate aspect ratio (always 1 or greater)
    if w>=h and h>0:
        ar=w/h
    elif w>0:
        ar=h/w
    return(xc,yc,ar,angle)

#the main detection script
def mainDetection():
    global objCount, save, MIN_AREA, MAX_AREA, x0,y0,x1,y1,xc,yc,ar,angle, area
    frameCount=0                        # keeps track of image number
    
    # blur and threshold image
    if pic is None:
        print('Please press "Exit" to properly close program')
        return
    colorIM=cv2.resize(pic,PROCESS_REZ)
    grayIM = cv2.cvtColor(colorIM, cv2.COLOR_BGR2GRAY)  # convert color to grayscale image       
    blurIM=cv2.medianBlur(grayIM,BLUR)                  # blur image to fill in holes to make solid object
    ret,binaryIM = cv2.threshold(blurIM,thresh,255,cv2.THRESH_BINARY_INV) # threshold image to make pixels 0 or 255
    
    # get contours  # dummy, 
    contourList, hierarchy = cv2.findContours(binaryIM, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # all countour points, uses more memory
    
    # draw bounding boxes around objects
    objCount=0                                      # used as object ID in detectArray
    for objContour in contourList:  # process all objects in the contourList                
        area = int(cv2.contourArea(objContour))     # find obj area        
        if MAX_AREA > area > MIN_AREA:                           # only detect large objects       
            PO = cv2.boundingRect(objContour)
            x0=PO[0]; y0=PO[1]; x1=x0+PO[2]; y1=y0+PO[3]
            cv2.rectangle(colorIM, (x0,y0), (x1,y1), (0,255,0), THICK) # place GREEN rectangle around each object, BGR
            (xc,yc,ar,angle)=getAR(objContour)
            objCount+=1                                     # indicate processed an object
            
            # save object parameters in detectArray in format FRAME=0; ID=1;  X0=2;   Y0=3;   X1=4;   Y1=5;   XC=6;   YC=7; CLASS=8; AREA=9; AR=10; ANGLE=11; MAX_COL=12
            if save:
                parm = [csv_image_name(file),objCount,x0,y0,x1,y1,xc,yc,area,ar,angle] # create parameter vector (1 x MAX_COL) 
                detectList.append(parm)
                print('Objects Saved!')
                
    save = 0 # so the code is not constantly saving the same objects after the button is pressed
    
    # shows results
    cv2.imshow('colorIM', cv2.resize(colorIM,VGA))      # display image
    #cv2.imshow('blurIM', cv2.resize(blurIM,VGA)) # display thresh image
    cv2.imshow('binaryIM', cv2.resize(binaryIM,VGA))# display thresh image
    
    frameCount+=1
    return         

def updateStatusDisplay(): #what goes on the status bar on top of the screen
    global root_2,thresh,MIN_AREA,MAX_AREA
    thresh = int(slide_var1.get())
    MIN_AREA = int(slide_var2.get())
    MAX_AREA = int(slide_var3.get())
    textOut='   Image name='+ str(csv_image_name(file)) + '    Threshold=' + str(thresh) + '    Min Area=' + str(MIN_AREA) + '    Max Area=' + str(MAX_AREA)+'   '
    tk.Label(root_2, text=textOut,bg="pink",justify = tk.LEFT).grid(row=0,column=0,columnspan=4)
    

def doButton(): #determines functions of each button
    global thresh, MIN_AREA, MAX_AREA, skip_im, save, show_welcome_wid, pic
   
    val=v.get()
    but=names[val]
    #print('But:',but,'Val:', val)

    if 'Next Image' in but:
        #skip_im = 0     # this flag stops detecting the current image to move on to the next one
        title4['text'] = ' '
        cv2.destroyAllWindows()
        show_welcome_wid = False
        pic = getImage()
        if pic is None:
            print('Canceling detection...')
            root_2.withdraw()
            root_2.quit()
            root.destroy()
            cv2.destroyAllWindows()
            return
        
    elif 'Save Parameters' in but:
        save = 1        # this flag saves the objects to the csv file
        title4['text'] = 'Detected objects were saved!'
    
    elif 'Exit' in but:
        root_2.withdraw()
        root_2.quit()
        root.destroy()
        cv2.destroyAllWindows()
        return
    
    updateStatusDisplay()
    mainDetection() #detect script
    return

def scrolling(event):  # functions for the scrolling bars
    updateStatusDisplay()
    mainDetection()
    return

def save_file():
    global detectFileName
    root = tk.Tk()
    root.withdraw()
    detectFileName=filedialog.asksaveasfilename(filetypes = [('comma-separated values (CSV)','.csv'), ('text file','.txt')], 
                                                defaultextension = '.csv')
    root.destroy()
    return

############################# GLOBAL VAR FOR MOUSE ###########################
BUTTON_WIDTH=20         # button display width
WINDOW_SCALE=10         # window size increment
FULL_SCALE=2            # reduce full scale image by this factor so it fits in window

def doc():
    print()
    print('============================ USER GUIDE ==============================')
    print('Use Min Area to adjust the minimum area for detection')
    print('Use Max Area to adjust the maximum area for detection')
    print('Use Threshold to adjust the pixel threshold for detection')
    print('Click "Save Parameters" to save the objects detected into the csv file')
    print('Click "Next Image" to go to the next image')
    print('Click "Exit" to end program')
    print('======================================================================')
    print()

# Button names. Some are left blank for future functions.
names = [
    ("Save Parameters"),
    ("Next Image"),
    ("Exit"), 
]

welcome_message = '''
                                                          MICROSCOPE UI
                            Author: Salma Ahmed         CHEM 667        Fall 2021

Welcome! This GUI uses the detect program (created by Tom Zimmerman) to detect 
objects in an image.

Choose an image in the file manager to get started!
'''

################################## MAIN #####################################

doc() #to print the user guide

pic = getImage()

if pic is not None:
    #root is for file manager, root_2 is for button grid
    root_2 = tk.Toplevel() 
    v = tk.IntVar()
    slide_var1 = tk.DoubleVar()
    slide_var2 = tk.DoubleVar()
    slide_var3 = tk.DoubleVar()

    root_2.title("Detection Functions")
    
    # Here are the sliders
    slider = ttk.Scale(root_2, from_=0, to=255, orient='horizontal', 
                       length = 200,variable=slide_var1,command=scrolling) #threshold
    slider.grid(row=1,column= 1)
    title1 = tk.Label(root_2, text = 'Threshold').grid(row = 1, column =0)
    slider.set(60)
    
    slider_2 = ttk.Scale(root_2, from_=0, to=2000, orient='horizontal', 
                        length = 500,variable=slide_var2,command=scrolling) #min area
    slider_2.grid(row=2,column= 1)
    slider_2.set(50)
    title2 = tk.Label(root_2, text = 'Minimum Area').grid(row = 2, column = 0)
    
    slider_3 = ttk.Scale(root_2, from_=0, to=3000, orient='horizontal', 
                        length = 500,variable=slide_var3,command=scrolling) #max area
    slider_3.grid(row=3,column= 1)
    slider_3.set(1500)
    title3 = tk.Label(root_2, text = 'Maximum Area').grid(row = 3, column = 0)
    
    updateStatusDisplay()
    
    # Here are the buttons
    for val, txt in enumerate(names): #goes through each button (and what they'd look like)
        r=int(4+val/4)
        c=int(val%4)
        tk.Radiobutton(root_2, text=txt,padx = 1, variable=v,width=BUTTON_WIDTH,
                       activebackground = 'pink',command=doButton,indicatoron=True,
                       value=val).grid(row=r,column=c)
    
    title4 = tk.Label(root_2, text = ' ')
    title4.grid(row=6, column = 1)
    
    mainDetection() #to detect objects (but just the first instance)
    
    root_2.mainloop() #program will keep waiting until a button has been pressed
    cv2.destroyAllWindows()     # clean up to end program
    print('Done with images.')  # once the program ends
    
    #asks for detectFileName (using file dialog box)
    save_file()
    try:
        #saves data into the csv file
        print('Saving data to CSV file ...')
        detectDF = pd.DataFrame(detectList, columns = detectHeader)
        detectDF.to_csv(detectFileName, columns = detectHeader,header = True)
    except FileNotFoundError:
        print('No file name input, CSV file was not saved...')

else:
    print('Canceling detection...')
    print('No CSV file was made')

print('bye!')               # tell the user program has ended

