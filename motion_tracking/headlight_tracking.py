import numpy as np
import cv2
import glob
import argparse 
import imutils
import time
from collections import deque
#from bluetooth import Bluetooth


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help = "Path to video file")
args = vars(ap.parse_args())

# load the video. If no video file is specified, 
# grab from webcam
if args.get("video", None) is None:
	camera = cv2.VideoCapture(0)
	time.sleep(0.25)
else:
	camera = cv2.VideoCapture(args["video"])

"""

# Initialize and wait for pair
bluetooth = Bluetooth("/dev/ttyAMA0/", 115000)

"""
# define the lower and upper boundaries of the headlights
# in the HSV color space
maskLower = (0, 0, 255)
maskUpper = (255, 255, 255)

# Range of locations for cars. 
# backLeft is the blindspot area around 7 o'clock
# backBackLeft is behind the blind spot area, further back
# TODO: Make one for rear
backLeftRangeX = (220, 320)
backLeftRangeY = (0, 50)
backBackLeftRangeX = (155, 219)
backBackLeftRangeY = (75, 275)


backLeft = False
backBackLeft = False

while True:
	backLeft = False
	backbackLeft = False
	# grab the current frame
	(grabbed, orig) = camera.read()
 
	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if args.get("video") and not grabbed:
		print "Can't grab video"
		continue
		
 	# Resize for faster processing
	orig = imutils.resize(orig, width=600)

	# Convert to HSV color to find headlights
	hsv = cv2.cvtColor(orig, cv2.COLOR_BGR2HSV)

	# Mask headlights. Ranges found with https://github.com/jrosebr1/imutils/blob/master/bin/range-detector
	mask = cv2.inRange(hsv, maskLower, maskUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)


	# find contours in the mask and initialize the current
	# (x, y) center of the contours
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None
	contours = orig.copy()
	cv2.drawContours(contours, cnts, -1, (0,255,0), 3)
	cv2.imshow("Contours", contours)

	# only proceed if at least one contour was found
	if len(cnts) > 0:
		for i in range(0, len(cnts)):
			# find the minimum enclosing circle in the contour
			((x, y), radius) = cv2.minEnclosingCircle(cnts[i])
			
			# Only proceed if radius is less than maximum size
			if radius < 10:

				# Find center coordinates
				M = cv2.moments(cnts[i])
				cX = int(M["m10"] / M["m00"])
				cY = int(M["m01"] / M["m00"])

				# Used to ignore the sky (place on the lefthand side of the frame
				# because the sky is the same color as the headlights)
				if cX < 150:
					continue
					
				# If the headlight is on lefthand side, print left,
				# if right, print right
				if cX > 220 and cX < 320:
					backLeft = True
				elif cX < 219 and cX > 155:
					backBackLeft = True

				
				center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
				
				# draw the circle and centroid on the frame
				cv2.circle(orig, (int(x), int(y)), int(radius), (0, 255, 255), 2)
				cv2.circle(orig, center, 5, (0, 0, 255), -1)

		if backLeft:
			print "back Left"
			#bluetooth.write("1xx")
		else:
			print ""
			#bluetooth.write("0xx")
		if backBackLeft:
			print "back back left"
			#bluetooth.write("1xx")
		else:
			print ""
			#bluetooth.write("0xx")

		# show the frame to our screen
		cv2.imshow("Headlights", orig)
 	
	key = cv2.waitKey(1) & 0xFF
 
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break
 
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()


