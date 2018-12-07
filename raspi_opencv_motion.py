# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import cv2
import imutils
import datetime
from imutils.video import VideoStream
import time
from threading import Thread
import copy
cap = cv2.VideoCapture('tcpclientsrc host=RASPI_IP_ADDRESS port=5000 ! gdpdepay ! rtph264depay !avdec_h264 ! videoconvert ! appsink sync=false', cv2.CAP_GSTREAMER)
# initialize the first frame in the video stream
motionDet = False
firstFrame = None
count = 0
text = "Unoccupied"
fourcc = cv2.VideoWriter_fourcc(*'X264')
buffer = []
prev_buffer = []
referenceFrame = 300
def recordVideo(fileName):
    global prev_buffer
    out = cv2.VideoWriter(fileName+'.avi',fourcc, 25.0, (len(frame[0,:]),len(frame[:,0])))
    for f in prev_buffer:
        out.write(f)
    out.release()

if __name__ == "__main__":
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()    	
        frameSmall = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frameSmall, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # if the first frame is None, initialize it
        if firstFrame is None:
            firstFrame = gray
            continue
        
        if count == referenceFrame:
            count = 0
            text = "No Motion"
            motionDet = False
            firstFrame = grayPrev
            continue
        cv2.imshow('frame',frame)
        # compute the absolute difference between the current frame and
        # first frame
        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
     
        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
     
        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 500:#args["min_area"]:
                continue
     
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frameSmall, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Motion Detected"
            motionDet = True
        # draw the text and timestamp on the frameSmall
        cv2.putText(frameSmall, "Room Status: {}".format(text), (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frameSmall, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
            (10, frameSmall.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        
        # show the frame and record if the user presses a key
        cv2.imshow("Security Feed", frameSmall)
        cv2.imshow("Thresh", thresh)
        cv2.imshow("Frame Delta", frameDelta)
        key = cv2.waitKey(1) & 0xFF
        
        if motionDet == True:
            buffer.append(frame)#append frames to a buffer which we will record later
        else:
            if len(buffer) > 0:
                prev_buffer = copy.deepcopy(buffer)
                timeStr = str(time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime()))
                thread = Thread(target = recordVideo, args = (timeStr, ))
                thread.start()
                #thread.join()
                print('saved video')
                buffer = []
        # if the `q` key is pressed, break from the lop
        if key == ord("q"):
            break
        if count == int(referenceFrame/2):
            grayPrev = np.copy(gray)
        #iterate the count
        count += 1
    # cleanup the camera and close any open windows
    cap.stop() if args.get("video", None) is None else cap.release()
    cv2.destroyAllWindows()
    
        