
# from __future__ import print_function
from time import gmtime, strftime 
from MicroExpNet import *
from PIL import Image, ImageOps
import tensorflow as tf
import numpy as np
import cv2
import imagezmq
import sys
import os
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import matplotlib.pyplot as plt
import socket
import requests
import json

from collections import deque

#colors for hue lights
red=2000
yellow=4000
green=20000
blue=42000
purple=50000
no_face_count=0
sum_predictions=np.zeros((1,1,8)) #avoid toggle between no_face and face_detetected
final_sum_predictions=np.zeros((1,1,8)) #for average probability for every emotion 

labels = ["neutral", "anger", "contempt", "disgust", "fear", "happy", "sadness", "surprise"]
#emotion_color=[8000,2000,50000,16000,0,38000,46000,54000] 
emotion_color=[0,2000,60000,16000,20000,10000,46000,38000]#mapping meotion to color
color_names=["yellow", "red", "purple", "green", "dark red", "light blue", "dark blue", "pink"] #colornames for emotions
modelDir = "Models/CK/"
hue_group_name='pixelflux'
bridge_ip="192.168.20.101"#ip of hue bridge
bridge_username="ZdgukOoXbpuwxKhcMioCljyeyCMKXIeJC0LmEtKI" #username to get permission for hue lights
#hue functions
def turn_on_group(where): #enable lights
    groups = { hue_group_name: 1} #name of hue group
    group_id = groups[where]

    payload = {"on":True}
    headers = {'content-type': 'application/json'}
    r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id)+"/action", data=json.dumps(payload), headers=headers)

# Beispiel:
# turn_off_group('kitchen')
def turn_off_group(where): #disable hue lights
    groups = { hue_group_name: 1}
    group_id = groups[where]

    payload = {"on":False}
    headers = {'content-type': 'application/json'}
    r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id)+"/action", data=json.dumps(payload), headers=headers)

def switch_light_color(where,what):
    groups = { hue_group_name: 1}
    group_id = groups[where]
    if what==0: #neutral
        payload = {"on":True,"sat":0, "bri":128,"hue":27000} #daturation, brightness and color
    else:
        payload = {"on":True,"sat":254, "bri":200,"hue":what} #daturation, brightness and color
    headers = {'content-type': 'application/json'}
    r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id)+"/action", data=json.dumps(payload), headers=headers)
def switch_to_white(where): #changes color to white
    groups = { hue_group_name: 1}
    group_id = groups[where]

    payload = {"on":True,"sat":0, "bri":255,"hue":27000}
    headers = {'content-type': 'application/json'}
    r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id)+"/action", data=json.dumps(payload),headers=headers)

# Import the xml files of frontal face and eye
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') #initalize cv2.face_detection
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml') 

def detectFaces(img):
    # Convertinto grayscale since it works with grayscale images
    gray_img= cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect the face
    faces = face_cascade.detectMultiScale(gray_img, 1.3, 5)

    return faces 

# Detects the face and eliminates the rest and resizes the result img
def segmentFace(inputFile, imgXdim, imgYdim):
    # Read the image
     

    # Detect the face
    deteced_faces = detectFaces(inputFile)
    # Return the whole image if it fails to detect the face
    if len(deteced_faces) > 0: #at least one face detceted
        (p,q,r,s) = deteced_faces[0] 
        img = inputFile[q:q+s, p:p+r]
        img = cv2.resize(img, (imgXdim, imgYdim)) 
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return (img,p,q,r,s) #return image and 
    else:
        return None

    # Crop & resize the image
    #img = cv2.resize(inputFile, (256, 256)) 	
    #img = img[32:256, 32:256]
   

def get_time():
    return strftime("%a, %d %b %Y %X", gmtime())    
# not used but can be used to stream over ethernet 
#HOST = '192.168.178.24' # Enter IP or Hostname of your server
#PORT = 5555 # Pick an open Port (1000+ recommended), must match the server port
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((HOST,PORT))
# initialze picamera 
camera = PiCamera()
camera.framerate = 30
camera.resolution = (700, 600)
rawCapture = PiRGBArray(camera)
camera.capture(rawCapture,format='bgr')
rawCapture.truncate(0)
time.sleep(0.1)

    # Static parameters
imgXdim = 84 #size of image for emotion recognition
imgYdim = 84
nInput = imgXdim*imgYdim # Since RGB is transformed to Grayscale

x = tf.placeholder(tf.float32, shape=[None, nInput])


# Construct model
classifier = MicroExpNet(x)

# Deploy weights and biases for the model saver
weights_biases_deployer = tf.train.Saver({"wc1": classifier.w["wc1"], \
                                    "wc2": classifier.w["wc2"], \
                                    "wfc": classifier.w["wfc"], \
                                    "wo": classifier.w["out"],   \
                                    "bc1": classifier.b["bc1"], \
                                    "bc2": classifier.b["bc2"], \
                                    "bfc": classifier.b["bfc"], \
                                    "bo": classifier.b["out"]})

emotions = deque(maxlen=15)

turn_on_group(hue_group_name)
with tf.Session() as sess:
    # Initializing the variables
    sess.run(tf.global_variables_initializer())
    print("[" + get_time() + "] " + "Testing is started...")
    weights_biases_deployer.restore(sess, tf.train.latest_checkpoint(modelDir))
    print("[" + get_time() + "] Weights & Biases are restored.")
    last_emotion = ""
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):#take a picture
        t1=time.time()
        image = frame.array #extract image
        #face recognition and segmentation
        image_rec = segmentFace(image, imgXdim, imgYdim) #detects the face

        #screen size 1024*600
        ww = 1024
        hh = 600
        color = (0,0,0)
        ht,wt,cc=image.shape
        result = np.full((hh,ww,cc), color, dtype=np.uint8)
        x_offset=324
        y_offset=0;
        #adding black border on the left side to leave space for text
        result[y_offset:y_offset+image.shape[0], x_offset:x_offset+image.shape[1]] = image 

        if image_rec is not None: #face detected
            image_seg,x1,y1,w1,h1=image_rec
            cv2.putText(result, "Face Detected", (50,50),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
            cv2.rectangle(result,(x1+x_offset,y1),(x1+w1+x_offset,y1+h1),(0,255,0),1)
            testX = np.reshape(image_seg, (1, imgXdim*imgYdim))
            testX = testX.astype(np.float32)
            # truncate buffer
            rawCapture.truncate(0)
            # emotion recognition   
        
            predictions = sess.run([classifier.pred], feed_dict={x:testX})
            emotion = np.argmax(predictions)
            sum_predictions=np.add(sum_predictions,predictions)

            emotions.append(emotion)           


            # control hue lights        
            if(len(emotions)==10): #vector captures the last emotions with highest percentage
                final_sum_predictions=np.divide(sum_predictions,10)
                counts = np.bincount(emotions)
                final_emotion = np.argmax(counts)
                #["neutral", "anger", "contempt", "disgust", "fear", "happy", "sadness", "surprise"]
                

               # cv2.putText(result, labels[emotion], (50,50),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
                #cv2.putText(result, labels[final_emotion], (50,75), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
                sum_predictions=np.zeros((1,1,8)) 
                emotions.clear()

            #percentage of every emotion
           
            neutral_percentage=str((final_sum_predictions[0][0][0]*100).round(1,None))
            anger_percentage=str((final_sum_predictions[0][0][1]*100).round(1,None))
            contempt_percentage=str((final_sum_predictions[0][0][2]*100).round(1,None))
            disgust_percentage=str((final_sum_predictions[0][0][3]*100).round(1,None))
            fear_percentage=str((final_sum_predictions[0][0][4]*100).round(1,None))
            happy_percentage=str((final_sum_predictions[0][0][5]*100).round(1,None))
            sadness_percentage=str((final_sum_predictions[0][0][6]*100).round(1,None))
            surprise_percentage=str((final_sum_predictions[0][0][7]*100).round(1,None))
            
            #print all emotins an probability
            cv2.putText(result, labels[1]+": "+anger_percentage+"%", (50,400),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            cv2.putText(result, labels[3]+": "+disgust_percentage+"%", (50,425),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            cv2.putText(result, labels[4]+": "+fear_percentage+"%", (50,450),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            cv2.putText(result, labels[5]+": "+happy_percentage+"%", (50,475),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            cv2.putText(result, labels[6]+": "+sadness_percentage+"%", (50,500),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            cv2.putText(result, labels[7]+": "+surprise_percentage+"%", (50,525),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            if(modelDir == "Models/CK/"):
                cv2.putText(result, labels[0]+": "+neutral_percentage+"%", (50,550),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
                cv2.putText(result, labels[2]+": "+contempt_percentage+"%", (50,575),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            
            final_emotion=np.argmax(final_sum_predictions)
            cv2.putText(result, "You're emotion is:", (50,90),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            cv2.putText(result, labels[final_emotion], (15,240),  cv2.FONT_HERSHEY_SIMPLEX,2, (0, 255, 0), 1)
            if labels[final_emotion] != last_emotion:
                    #if emotion_color[final_emotion]!=0:
                switch_light_color(hue_group_name,emotion_color[final_emotion])
                last_emotion = labels[final_emotion]
                    #else:
                #switch_to_white(hue_group_name)

        else:
            cv2.putText(result, "No Face Detected", (25,50),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
            no_face_count+=1
            if(no_face_count==15):
                no_face_count=0
                turn_off_group(hue_group_name)
        rawCapture.truncate(0)
       #print image fullscreen
        cv2.namedWindow("emotion_recognition", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("emotion_recognition",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow("emotion_recognition",result)
        cv2.waitKey(1)
      

