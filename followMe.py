from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
from time import sleep

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
pins=[12,22,13,21]
for x in pins:
    GPIO.setup(x,GPIO.OUT)
def Forward():
    GPIO.output(pins,[0,1,0,1])
def Backward():
    GPIO.output(pins,[1,0,1,0])
def Left():
    GPIO.output(pins,[0,1,0,0])
def Right():
    GPIO.output(pins,[1,0,0,0])
def Stop():
    GPIO.output(pins,[0,0,0,0])

camera = PiCamera()
image_width = 640
image_height = 480
camera.resolution = (image_width, image_height)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(image_width, image_height))
center_image_x = image_width / 2
center_image_y = image_height / 2
minimum_area = 2500
maximum_area = 100000

HUE_VAL = 29 #for Yellow
#HUE_VAL = 103  #for light blue
lower_color = np.array([HUE_VAL-10,100,100])
upper_color = np.array([HUE_VAL+10, 255, 255])

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    color_mask = cv2.inRange(hsv, lower_color, upper_color)

    countours, hierarchy = cv2.findContours(color_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    object_area = 0
    object_x = 0
    object_y = 0

    for contour in countours:
        x, y, width, height = cv2.boundingRect(contour)
        found_area = width * height
        center_x = x + (width / 2)
        center_y = y + (height / 2)
        if object_area < found_area:
            object_area = found_area
            object_x = center_x
            object_y = center_y
    if object_area > 0:
        object_location = [object_area, object_x, object_y]
    else:
        object_location = None

    if object_location:
        if (object_location[0] > minimum_area) and (object_location[0] < maximum_area):
            if object_location[1] > (center_image_x + (image_width/3)):
                Right()
                print("Turning left")
            elif object_location[1] < (center_image_x - (image_width/3)):
                Left()
                print("Turning right")
            else:
                Backward()
                print("Forward")
        elif (object_location[0] < minimum_area):
            Stop()
            print("Target isn't large enough, searching")
        else:
            Stop()
            print("Target large enough, stopping")
    else:
        Stop()
        print("Target not found, searching")
    rawCapture.truncate(0)
