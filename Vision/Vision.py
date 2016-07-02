__author__ = 'teddycool'
#Master class for the vision system, using other classes for each type of detection
#
#Webinfo used for this part of project:
# http://blog.miguelgrinberg.com/post/stream-video-from-the-raspberry-pi-camera-to-web-browsers-even-on-ios-and-android
import time
import sys

import cv2

from picamera import PiCamera
#import picamera.array
from picamera.array import PiRGBArray
import LaserFinder
import ContourFinder
import FaceDetector
import os
from RoverConfig import config


class Vision(object):

    def __init__(self, resolution):
        print "Vision object started..."
        self._seqno = 0
        #self._log = Logger.Logger("Vision")
        #self._contourFinder = ContourFinder.ContourFinder()
        #self._faceDetector = FaceDetector.FaceDetector()
        self._cam = PiCamera()
        self._cam.resolution = resolution
        self._cam.framerate = 10
        self._rawCapture = PiRGBArray(self._cam, size=resolution)
        self._center = (resolution[0]/2, resolution[1]/2)
        #self._laserfinder = LaserFinder.LaserFinder()
       # self._signFinder = SignFinder.SignFinder()
        print "Starting streamer..."
        print os.system('sudo mkdir /tmp/stream')
        print os.system('sudo LD_LIBRARY_PATH=/home/pi/mjpg-streamer/mjpg-streamer /home/pi/mjpg-streamer/mjpg-streamer/mjpg_streamer -i "input_file.so -f /tmp/stream -n pic.jpg" -o "output_http.so -w /home/pi/mjpg-streamer/mjpg-streamer/www" &')


        #TODO: check that streamer is running


    def initialize(self):
        print "Vision initialised"
        self._lastframetime = time.time()
        self._imagegenerator = self._cam.capture_continuous(self._rawCapture, format="bgr", use_video_port=True)
        frame = self.update()
       # self._signFinder.initialize()
        return frame



    def update(self):
        print "Vision update"
        #self._log.info("Update started")
         #TODO: make threaded in exception catcher
        # https://picamera.readthedocs.org/en/release-1.10/recipes2.html#rapid-capture-and-processing

        frame = self._imagegenerator.next()
        self._rawCapture.truncate()
        self._rawCapture.seek(0)
        self._frame = frame.array

        if config["Vision"]["WriteRawImageToFile"]:
            cv2.imwrite("/home/pi/LegoRover/Imgs/camseq"+str(self._seqno)+".jpg",self._frame )
        #TODO: deliver found obstacles back to main-loop or sensor-module
        #self._signFinder.update(self._frame)
        #self._contourFinder.update(self._frame)
        #self._faceDetector.update(frame)
        #self._laserfinder.update(frame)
        #self._log.info("Update finnished")
        #TODO: return detected obstacles etc
        return self._frame

    def draw(self, frame):
        #self._log.info("Draw started")
        framerate = 1/(time.time()-self._lastframetime)
        print "Vision framerate: " + str(framerate)
        self._lastframetime= time.time()
        #frame = self._signFinder.draw(frame)
        #self._contourFinder.draw(frame)
       # frame = self._faceDetector.draw(frame)
        #frame = self._laserfinder.draw(frame)

        #draw cross for center of image
        cv2.line(frame,(self._center[0]-20,self._center[1]),(self._center[0]+20, self._center[1]),(255,255,255),2)
        cv2.line(frame,(self._center[0],self._center[1]-20),(self._center[0],self._center[1]+20),(255,255,255),2)
        #cv2.line(frame, self._laserfinder._point, self._center,(0,255,0),2)
        cv2.putText(frame,"Streamer: " + config["Streamer"]["StreamerImage"] + " Current framerate: " + str(round(framerate, 2)), (5,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        #Draw to streamer lib to 'publish'
        cv2.imwrite(config["Streamer"]["StreamerImage"],frame)
        if config["Vision"]["WriteCvImageToFile"]:
            cv2.imwrite("/home/pi/LegoRover/Imgs/cvseq"+str(self._seqno)+".jpg",frame)
        self._seqno = self._seqno+1 #Used globally but set here        #TODO: set up a defined (max) framerate from config
        #self._log.info("Draw finnished")


    def getCurrentFrame(self):
        return self._frame


    def __del__(self):
        print "Vision object deleted..."
        self._cam.close()




if __name__ == '__main__':
    print "Testcode for Vision"
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)

    vision= Vision( (640,480))
    vision.initialize()
    try:
        while 1:
            #print "Updating frame..."
            frame = vision.update()
            #print "Drawing frame..."
            vision.draw(frame)
            time.sleep(0.2)
    except:
        GPIO.cleanup()
        e = sys.exc_info()[0]
        print e