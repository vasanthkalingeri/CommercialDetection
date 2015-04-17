import cv2
import time

DARK = 0
video = cv2.VideoCapture('data.mp4')
#NO_FRAMES = video.get(8)
NO_FRAMES = 30

base = time.time()
blank = False

while True:
    
    ret, frame = video.read()
    delta = time.time() - base

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    x = gray.ravel()
    
    if x.mean() < 0.3:
        blank = True
    else:
        if blank:
            print "scene changed at", time.strftime("%H:%M:%S", time.gmtime(delta))   
        blank = False

    cv2.imshow('frame',frame)
    if cv2.waitKey(NO_FRAMES) & 0xFF == ord('q'):
        break
