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
sum_predictions=np.zeros((1,1,8))
final_sum_predictions=np.zeros((1,1,8))

labels = ["neutral", "anger", "contempt", "disgust", "fear", "happy", "sadness", "surprise"]
emotion_color=[8000,2000,50000,16000,0,38000,46000,54000]
color_names=["yellow", "red", "purple", "green", "dark red", "light blue", "dark blue", "pink"]
modelDir = "Models/OuluCASIA/"
bridge_ip="192.168.178.79"
bridge_username="ZdgukOoXbpuwxKhcMioCljyeyCMKXIeJC0LmEtKI"
#hue functions
def turn_on_group(where):
    groups = { 'pixelflux': 1}
    group_id = groups[where]

    payload = {"on":True}
    headers = {'content-type': 'application/json'}
    r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id)+"/action", data=json.dumps(payload), headers=headers)

# Beispiel:
# turn_off_group('kitchen')
def turn_off_group(where):
    groups = { 'pixelflux': 1}
    group_id = groups[where]

    payload = {"on":False}
    headers = {'content-type': 'application/json'}
    r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id)+"/action", data=json.dumps(payload), headers=headers)

def switch_light_color(where,what):
    groups = { 'pixelflux': 1}
    group_id = groups[where]

    payload = {"on":True,"sat":254, "bri":254,"hue":what}
    headers = {'content-type': 'application/json'}
    r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id)+"/action", data=json.dumps(payload), headers=headers)

# functions for face_detection and face-marking
def get_resize_factor(max_length):
    image = rawCapture.array
    width,height,channel=image.shape
    print(image.shape)
    rawCapture.truncate(0)
    if (width>height):
        target_width=max_length
        resize_factor=width/target_width
    elif height>width:
        target_height=max_length
        resize_factor=height/target_height
    else: 
        target_width=max_length
        resize_factor=width/target_width
    print(resize_factor)
    return resize_factor,width,height

def rect_to_bb(rect):
    # take a bounding predicted by dlib and convert it
    # to the format (x, y, w, h) as we would normally do
    # with OpenCV
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y
    # return a tuple of (x, y, w, h)
    return (x, y, w, h)

def shape_to_np(shape, dtype="int"):
    # initialize the list of (x, y)-coordinates
    coords = np.zeros((68, 2), dtype=dtype)
    # loop over the 68 facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    # return the list of (x, y)-coordinates
    return coords

# Import the xml files of frontal face and eye
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
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
    # Return the whole image if it failed to detect the face
    if len(deteced_faces) > 0:
        (p,q,r,s) = deteced_faces[0]
        img = inputFile[q:q+s, p:p+r]
        img = cv2.resize(img, (imgXdim, imgYdim)) 
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img
    else:
        return None

    # Crop & resize the image
    #img = cv2.resize(inputFile, (256, 256)) 	
    #img = img[32:256, 32:256]
   

def get_time():
    return strftime("%a, %d %b %Y %X", gmtime())    
# camera config 
HOST = '192.168.178.24' # Enter IP or Hostname of your server
PORT = 5555 # Pick an open Port (1000+ recommended), must match the server port
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((HOST,PORT))
# initialze picamera 
camera = PiCamera()
camera.framerate = 30
camera.resolution = (600, 800)
rawCapture = PiRGBArray(camera)
camera.capture(rawCapture,format='bgr')
rawCapture.truncate(0)
time.sleep(0.1)

    # Static parameters
imgXdim = 84
imgYdim = 84
nInput = imgXdim*imgYdim # Since RGB is transformed to Grayscale
"""
image = segmentFace(rawCapture.array, imgXdim, imgYdim)
image_nr=0
fin_emotions=[0]*len(labels)
final_emotion=0
no_face=0
testX = np.reshape(image, (1, imgXdim*imgYdim))
testX = testX.astype(np.float32)
"""
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

turn_on_group('pixelflux')
with tf.Session() as sess:
    # Initializing the variables
    sess.run(tf.global_variables_initializer())
    print("[" + get_time() + "] " + "Testing is started...")
    weights_biases_deployer.restore(sess, tf.train.latest_checkpoint(modelDir))
    print("[" + get_time() + "] Weights & Biases are restored.")
    last_emotion = ""
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        t1=time.time()
        image = frame.array
        #face recognition and segmentation
        image_seg = segmentFace(image, imgXdim, imgYdim)

        image=cv2.resize(image,(800,600))
        ww = 1024
        hh = 600
        color = (0,0,0)
        ht,wt,cc=image.shape
        result = np.full((hh,ww,cc), color, dtype=np.uint8)
        x_offset=224
        y_offset=0;
        result[y_offset:y_offset+image.shape[0], x_offset:x_offset+image.shape[1]] = image

        if image_seg is not None:
            cv2.putText(result, "Face Detected", (50,50),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
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
            if(len(emotions)==10):
                final_sum_predictions=np.divide(sum_predictions,10)
                counts = np.bincount(emotions)
                final_emotion = np.argmax(counts)
                #["neutral", "anger", "contempt", "disgust", "fear", "happy", "sadness", "surprise"]
                

               # cv2.putText(result, labels[emotion], (50,50),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
                #cv2.putText(result, labels[final_emotion], (50,75), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
                sum_predictions=np.zeros((1,1,8))
                emotions.clear()

            #label image
            #print("[" + get_time() + "] Emotion: " + labels[argmax])
            neutral_percentage=str((final_sum_predictions[0][0][0]*100).round(1,None))
            anger_percentage=str((final_sum_predictions[0][0][1]*100).round(1,None))
            contempt_percentage=str((final_sum_predictions[0][0][2]*100).round(1,None))
            disgust_percentage=str((final_sum_predictions[0][0][3]*100).round(1,None))
            fear_percentage=str((final_sum_predictions[0][0][4]*100).round(1,None))
            happy_percentage=str((final_sum_predictions[0][0][5]*100).round(1,None))
            sadness_percentage=str((final_sum_predictions[0][0][6]*100).round(1,None))
            surprise_percentage=str((final_sum_predictions[0][0][7]*100).round(1,None))
            cv2.putText(result, labels[0]+": "+neutral_percentage+"%", (50,400),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            cv2.putText(result, labels[1]+": "+anger_percentage+"%", (50,425),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            cv2.putText(result, labels[2]+": "+contempt_percentage+"%", (50,450),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            cv2.putText(result, labels[3]+": "+disgust_percentage+"%", (50,475),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            cv2.putText(result, labels[4]+": "+fear_percentage+"%", (50,500),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            cv2.putText(result, labels[5]+": "+happy_percentage+"%", (50,525),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            cv2.putText(result, labels[6]+": "+sadness_percentage+"%", (50,550),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            cv2.putText(result, labels[7]+": "+surprise_percentage+"%", (50,575),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            
            final_emotion=np.argmax(final_sum_predictions)
            cv2.putText(result, "You're emotion is: "+labels[final_emotion], (50,90),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
            if labels[final_emotion] != last_emotion:
                    switch_light_color('pixelflux',emotion_color[final_emotion])
                    last_emotion = labels[final_emotion]

            t2=time.time()
            

        else:
            cv2.putText(result, "No Face Detected", (50,50),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
        rawCapture.truncate(0)
        #marks start
        #start=(27119).to_bytes(3,'big')
        #s.send(start)
        #s.send(image)
        
        #cv2.copyMakeBorder(image,0,0,200,0,cv2.BORDER_CONSTANT,value=[255,0,0])
        cv2.namedWindow("emotion_recognition", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("emotion_recognition",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow("emotion_recognition",result)
        cv2.waitKey(1)
        #print("versenden:",time.time()-t1)
        #print("aufnehmen und senden:",time.time()-t2)
        #print("emotion"+labels[argmax])

