#!/usr/bin/env python
import roslib
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
#from __future__ import print_function
def getTrackValue(value):
	return value
def getthresholdedimg(hsv):
	threshImg = cv2.inRange(hsv,np.array((cv2.getTrackbarPos ('Hue_Low','Trackbars'),cv2.getTrackbarPos('Saturation_Low','Trackbars'),cv2.getTrackbarPos('Value_Low','Trackbars'))),np.array((cv2.getTrackbarPos('Hue_High','Trackbars'),cv2.getTrackbarPos('Saturation_High','Trackbars'),cv2.getTrackbarPos('Value_High','Trackbars'))))
	return threshImg
class image_converter:

  def __init__(self):
    self.image_pub = rospy.Publisher("ball_detector",Image,queue_size=10)

    self.bridge = CvBridge()
    self.image_sub = rospy.Subscriber("/camera/rgb/image_raw",Image,self.callback)
    cv2.namedWindow('Image window')
    cv2.namedWindow('Trackbars', cv2.WINDOW_NORMAL)
    cv2.createTrackbar('Hue_Low','Trackbars',0,255, getTrackValue)
    cv2.createTrackbar('Saturation_Low','Trackbars',0,255, getTrackValue)
    cv2.createTrackbar('Value_Low','Trackbars',0,255, getTrackValue)
 
    cv2.createTrackbar('Hue_High','Trackbars',0,255, getTrackValue)
    cv2.createTrackbar('Saturation_High','Trackbars',0,255, getTrackValue)
    cv2.createTrackbar('Value_High','Trackbars',0,255, getTrackValue)
    cv2.createTrackbar('erode radi','Trackbars',1,100, getTrackValue)
    cv2.createTrackbar('minDist','Trackbars',1,680, getTrackValue)
    cv2.createTrackbar('Hough_param1','Trackbars',1,1000, getTrackValue)
    cv2.createTrackbar('Hough_param2','Trackbars',1,1000, getTrackValue)
    cv2.createTrackbar('Find circle','Trackbars',0,1, getTrackValue)
    self.fgbg = cv2.BackgroundSubtractorMOG2()
  def callback(self,data):
    try:
      cv_image_bgr = self.bridge.imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
      print(e)
    fgmask = self.fgbg.apply(cv_image_bgr);
    cv2.medianBlur(cv_image_bgr,3,cv_image_bgr);
    image_hsv = cv2.cvtColor(cv_image_bgr,cv2.COLOR_BGR2HSV)
    hsv_threshold = getthresholdedimg(image_hsv)
    #print hsv_threshold.shape[1]
    #print cv2.getTrackbarPos('Find circle','Trackbars')
    output = cv_image_bgr.copy();
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(cv2.getTrackbarPos('erode radi','Trackbars'),cv2.getTrackbarPos('erode radi','Trackbars')));
    erosion = cv2.erode(hsv_threshold,kernel,iterations = 1)
    #edge = cv2.Canny(hsv_threshold,100,200)
    if cv2.getTrackbarPos('Find circle','Trackbars') is 1:
	print ('fetching ball....')
    	circles = cv2.HoughCircles(hsv_threshold, cv2.cv.CV_HOUGH_GRADIENT, 1,cv2.getTrackbarPos('minDist','Trackbars'),cv2.getTrackbarPos('Hough_param1','Trackbars'),cv2.getTrackbarPos('Hough_param2','Trackbars'));
	print circles
	if circles is not None:
		print 'circle found!'
	# convert the (x, y) coordinates and radius of the circles to integers
		circles = np.round(circles[0, :]).astype("int")
	# loop over the (x, y) coordinates and radius of the circles
		for (x, y, r) in circles:
			# draw the circle in the output image, then draw a rectangle
			# corresponding to the center of the circle
			cv2.circle(output, (x, y), r, (0, 255, 0), 4)
			cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
		cv2.imshow("Ball tracking window", output)
		#cv2.waitKey(0)
    cv2.imshow("hsv Image window",hsv_threshold)
    cv2.imshow("background subtractor Image window",fgmask)
    cv2.waitKey(3)

    try:
      self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv_image_bgr, "bgr8"))
    except CvBridgeError as e:
      print(e)

def main(args):

  ic = image_converter()
  rospy.init_node('image_converter', anonymous=True)
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")
  cv2.destroyAllWindows()


if __name__ == '__main__':
    main(sys.argv)
