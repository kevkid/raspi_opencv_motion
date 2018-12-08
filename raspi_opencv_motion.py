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
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst, GstBase, Gtk, GObject
import multiprocessing
import time

cap = cv2.VideoCapture('tcpclientsrc host=192.168.11.31 port=5000 ! gdpdepay ! rtph264depay !avdec_h264 ! videoconvert ! appsink sync=false', cv2.CAP_GSTREAMER)
setKeyFrame = 300

class Recorder:
    def __init__(self):
        Gst.init(None)
        timeStr = str(time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime()))
        self.pipeline = Gst.parse_launch('tcpclientsrc host=192.168.11.31 port=5000 ! gdpdepay ! rtph264depay !avdec_h264 ! videoconvert ! x264enc bitrate=512 ! matroskamux ! filesink async=0 location='+timeStr+'.mkv')
    def play(self):
        #self.pipeline.send_event(Gst.Event.new_flush_start())
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline.set_state(Gst.State.PAUSED)
        self.pipeline.set_state(Gst.State.READY)
        self.pipeline.set_state(Gst.State.PLAYING)
    def stop(self):
        self.pipeline.set_state(Gst.State.PAUSED)
        self.pipeline.set_state(Gst.State.READY)
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline.send_event(Gst.Event.new_eos())


if __name__ == "__main__":
    keyFrame = None
    count = 0
    slidingWindow = []
    startRecord = True
    rec=Recorder()
    while(True):
        #capture frames and apply some blurs to later check absolute value
        ret, frame = cap.read()
        frameSmall = imutils.resize(frame, width=400)
        gray = cv2.cvtColor(frameSmall, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        #if this is the begining of a stream set the keyframe to the first frame
        if keyFrame is None:
            keyFrame = gray
        #show our frame
        #cv2.imshow('frame',frame)
        #key = cv2.waitKey(1) & 0xFF
        

        # compute the absolute difference between the current frame and
        frameDelta = cv2.absdiff(keyFrame, gray)
        #thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        slidingWindow.append(np.average(frameDelta))
        if np.average(slidingWindow)/255 > 0.05:
            if startRecord == True:#if we are already recording dont start again
                rec=Recorder()
                rec.play()
                startRecord = False
            if count % 5 == 0:
                print('motion detected')
        else:
            if count == setKeyFrame:#record till last keyframe
                if startRecord == False:#checks if we are recording
                    rec.stop()
                    startRecord = True#sets flag to start recording again
                
            if count % 5 == 0:
                print('no motion')
        if count == setKeyFrame:
            #reset keyframe after x frames
            keyFrame = gray
            count = 0
            print('keyframe set!')
        del slidingWindow[0]
            
        count += 1
    


rec=Recorder()
rec.play()
rec.stop()
Gtk.main()
e = multiprocessing.Event()
p = multiprocessing.Process(target=rec.play(), args=())
p.start()        