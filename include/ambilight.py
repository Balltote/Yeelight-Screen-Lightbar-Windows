import os
from turtle import screensize
from typing import List
import cv2
import numpy as np
import time
import pyautogui
from mss import mss
from yeelight.transitions import *
from yeelight.flows import *
from yeelight import *
import tempfile

fldr = tempfile.gettempdir()
file = open(fldr+"/bulbIP.txt", "r")
text = file.read()
b = Bulb(text, effect="smooth", model="color")
#b = Bulb("192.168.1.104", effect="smooth")
#b.turn_on(light_type=LightType.Ambient)
b.set_brightness(100, light_type=LightType.Ambient)
b.stop_flow(light_type=LightType.Ambient)
screen_size = pyautogui.size()
#mon = {'top': int(screen_size[1]/4), 'left':int(screen_size[0]/2) , 'width': screen_size[0], 'height': screen_size[1]}
mon = {'top': int(screen_size[1]/3), 'left':int(screen_size[0]/2) , 'width': 1, 'height': 1}
sct = mss()

def b_set_rgb(rgb: List):
	#b.set_rgb(int(rgb[0]), int(rgb[1]), int(rgb[2]), light_type=LightType.Ambient)
		transitions = [
    	RGBTransition(int(rgb[0]), int(rgb[1]), int(rgb[2]), duration=500)
	]

		flow = Flow(
    	count=0,  # Cycle forever.
    	transitions=transitions
	)
		b.start_flow(flow, light_type=LightType.Ambient)
		#time.sleep(1)
		#b.stop_flow(light_type=LightType.Ambient)
prev_rgb = np.array([0, 0, 0])

while True:
	try:
		sct_img = sct.grab(mon)
		img = np.array(sct_img)
		img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)[0][0]

		if (prev_rgb == img_rgb).all():
			continue

		prev_rgb = img_rgb
		b_set_rgb(img_rgb)

		print(img_rgb)

		cv2.waitKey(750)
	except BulbException as e:
		print(str(e))
		time.sleep(2)
		continue
	# print(img_rgb)

	# cv2.namedWindow('Screen Point', cv2.WINDOW_KEEPRATIO)
	# cv2.imshow('Screen Point', img)

	# if cv2.waitKey(1000) & 0xFF == ord('q'):
	# 	cv2.destroyAllWindows()
	# 	break
