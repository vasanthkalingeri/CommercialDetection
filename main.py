import cv2

DARK = 0
video = cv2.VideoCapture('data.mp4')

while True:
    
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    x = gray.ravel()
#    print max(x), min(x)
    
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
