#!/usr/bin/env python3


import cv2
import numpy as np
import argparse


	

#init video
# cap = cv2.VideoCapture('/dev/video'+str(dev), cv2.CAP_V4L)
cap = cv2.VideoCapture(0)

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
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cv2.namedWindow('Thermal',cv2.WINDOW_GUI_NORMAL)
font=cv2.FONT_HERSHEY_SIMPLEX


while(cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if ret == True:
        # Display the resulting frame
        image_array = np.reshape(frame, (2, 192, 256, 2))
        terzo = image_array[0, :, :, 0]

        quarto = image_array[1, :, :, 1]
        hi = terzo[175][100]
        lo = quarto[175][100]
        lo = lo * 256
        rawtemp = lo + hi
        temp = (rawtemp / 64) - 273.15
        temp = round(temp, 2)
        print(f"Temp: {temp}")

        max_temp = (-float("inf"), 0, 0)
        for i in range(192):
            for j in range(256):
                hi = image_array[0, i, j, 0]
                lo = image_array[1, i, j, 1]
                lo = lo * 256
                rawtemp = lo + hi
                temp = (rawtemp / 64) - 273.15
                if temp > max_temp[0]:
                    max_temp = (temp, i, j)
        print(f"Max Temp: {round(max_temp[0], 2)}")
        # Draw a marker at the location of maximum temperature
        frame_with_marker = cv2.circle(terzo.copy(), (max_temp[2], max_temp[1]), 2, (0, 0, 255), -1)

        # Display the frame with marker
        cv2.imshow('Thermal', frame_with_marker)

        # Check for 'q' key to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release video capture object and close windows
cap.release()
cv2.destroyAllWindows()
        