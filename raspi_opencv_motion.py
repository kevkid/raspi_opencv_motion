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

class Monitor:
    def __init__(self, ipAddr, port, threshold = 0.05, timeToRecord = 30, bitrate=512):
        self.keyFrame = None
        self.count = 0
        self.slidingWindow = []
        self.startRecord = True
        self.t_end = None
        self.thresh = threshold
        self.timeToRecord = timeToRecord#Amount of time to record in seconds
        self.ipAddr = ipAddr
        self.cap = cv2.VideoCapture('tcpclientsrc host='+ipAddr+' port='+port+' ! gdpdepay ! rtph264depay ! avdec_h264 ! videoconvert ! appsink sync=false', cv2.CAP_GSTREAMER)
        self.setKeyFrame = 60
        self.bitrate = str(bitrate)
        Gst.init(None)
    
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
        
    def run(self):
        while(True):
        #capture frames and apply some blurs to later check absolute value
            ret, frame = self.cap.read()
            frame = imutils.resize(frame, width=300)#calculate on a small frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            #if this is the begining of a stream set the keyframe to the first frame
            if self.keyFrame is None:
                self.keyFrame = gray
            # compute the absolute difference between the current frame and
            frameDelta = cv2.absdiff(self.keyFrame, gray)
            self.slidingWindow.append(np.average(frameDelta))
            if np.average(self.slidingWindow)/255 > self.thresh:
                if self.startRecord == True:#if we are already recording dont start again
                    print('Started Recording')
                    timeStr = str(time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime()))
                    self.pipeline = Gst.parse_launch('tcpclientsrc host='+self.ipAddr+' port=5000 ! gdpdepay ! rtph264depay ! avdec_h264 ! videoconvert ! x264enc bitrate='+self.bitrate+' ! matroskamux ! filesink async=0 location='+timeStr+'.mkv')
                    self.play()
                    self.t_end = time.time() + self.timeToRecord
                    self.startRecord = False
            else:
                if self.startRecord == False:#checks if we are recording
                    if time.time() >= self.t_end:
                        print('Stopped Recording')
                        self.stop()
                        del self.pipeline
                        self.startRecord = True#sets flag to start recording again
            if self.count == self.setKeyFrame:
                #reset keyframe after x frames
                self.keyFrame = gray
                self.count = 0
                print('keyframe set!')
            del self.slidingWindow[0]
            self.count += 1
        
        

if __name__ == "__main__":
    cameraMonitor = Monitor(ipAddr='192.168.1.3', port='5000', threshold=0.05, timeToRecord=30, bitrate=2048)
    cameraMonitor.run()