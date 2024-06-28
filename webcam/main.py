#emotion_detection.py
#10/03/2024

import cv2
from deepface import DeepFace
import numpy as np  

#getting a haarcascade xml file
face_cascade_name = cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml'  
#processing it for our project
face_cascade = cv2.CascadeClassifier()  
#adding a fallback event
if not face_cascade.load(cv2.samples.findFile(face_cascade_name)):  
    print("Error loading xml file")

video=cv2.VideoCapture(2)
    
def videopick():
    cv2.destroyAllWindows()

    #checking if are getting video feed and using it
    if video.isOpened():  
        _,frame = video.read()
        try:
            
            #key=cv2.waitKey(1) 
            # zoom 
            
            gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)  
            face=face_cascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=6)
            for x,y,w,h in face:
                    #making a recentangle to show up and detect the face and setting it position and colour
                    img=cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),1) 
                    cv2.imshow("frame",img)

                    print("il volto si trova in: "+ str(x) + " "+ str(y))
                   
                    return img
        except cv2.error as e:
            print("errore nella lettura dell'immagine", e)            

def analize(img):
    #making a try and except condition in case of any errors
    try:
        try:
            analyze = DeepFace.analyze(img, actions=['emotion'])
            print(analyze)
            dominant_emotion = analyze[0]['dominant_emotion']
            print("----------- "+dominant_emotion+" ------------")
            
        except Exception as e:
            print("error: ", e)
            print("problem during analisys..")
    except cv2.error as e:
        print("no face detected, error: ", e)    


x = "s"

while x == "s":
    img = videopick()
    analize(img)
    # print("altro giro? s/n")               
    # x = input()
video.release()
         
       