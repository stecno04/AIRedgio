#!/usr/bin/env python3


import cv2
import numpy as np
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--device", type=int, default=0, help="Video Device number e.g. 0, use v4l2-ctl --list-devices")
args = parser.parse_args()
	
if args.device:
	dev = args.device
else:
	dev = 0
	

#init video
# cap = cv2.VideoCapture('/dev/video'+str(dev), cv2.CAP_V4L)
cap = cv2.VideoCapture(1)

#we need to set the resolution here why?
'''
wright@CF-31:~/Desktop$ v4l2-ctl --list-formats-ext
ioctl: VIDIOC_ENUM_FMT
	Index       : 0
	Type        : Video Capture
	Pixel Format: 'YUYV'
	Name        : YUYV 4:2:2
		Size: Discrete 256x192
			Interval: Discrete 0.040s (25.000 fps)
		Size: Discrete 256x384
			Interval: Discrete 0.040s (25.000 fps)
'''



cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)

#256x192 General settings
width = 256 #Sensor width
height = 192 #sensor height
scale = 3 #scale multiplier
newWidth = width*scale 
newHeight = height*scale
alpha = 1.0 # Contrast control (1.0-3.0)
colormap = 0
font=cv2.FONT_HERSHEY_SIMPLEX
dispFullscreen = False
cv2.namedWindow('Thermal',cv2.WINDOW_GUI_NORMAL)
cv2.resizeWindow('Thermal', newWidth,newHeight)
rad = 0 #blur radius
threshold = 2
hud = True
recording = False
elapsed = "00:00:00"
snaptime = "None"

# width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# cv2.namedWindow('Thermal',cv2.WINDOW_GUI_NORMAL)
# font=cv2.FONT_HERSHEY_SIMPLEX

while(cap.isOpened):
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    np.save('frame.npy', frame)
    if ret == True:
        cv2.namedWindow('Thermal',cv2.WINDOW_NORMAL)
        cv2.imshow('Thermal',frame)
        print("frame shape",frame.shape)
		# Our operations on the frame come here
        
        

        bianco, verde = np.split(frame, 2)
        print("bianco shape",bianco.shape)
        print("verde shape",verde.shape)
        # cv2.imshow('Thermal',frame)
        continue

        #salva immagine gialla e verde
        # cv2.save(verde#
        # cv2.save(bianco)
        cv2.imwrite('verde.jpg', verde)
        cv2.imwrite('bianco.jpg', bianco)

        hi = verde[96][128][0]
        lo = verde[96][128][1]
        print(hi,lo)
        lo = lo*256
        rawtemp = hi+lo
        #print(rawtemp)
        temp = (rawtemp/64)-273.15
        temp = round(temp,2)
        print("temp",temp)
        height, width, channels = verde.shape
        hv, wv, _ = bianco.shape
        # pixel in mezzo
        # in bianco e nero 
        # verde = cv2.cvtColor(verde, cv2.COLOR_BGR2GRAY)
        # pixel = verde[int(height/2), int(width/2)]
        
        # # 255:+°celsius =pixel:x
        # # 550:255= x:pixel
        # x = int((pixel*550)/256)
        # print(x)
        
        # Estrazione della temperatura al centro dell'immagine
        temperatura_centrale_bianco = bianco[hv // 2, wv // 2]
        temperatura_centrale_verde = verde[height // 2, width // 2]

        # Stampa delle temperature
        print("Temperatura al centro (bianco):", temperatura_centrale_bianco)
        print("Temperatura al centro (verde):", temperatura_centrale_verde)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break