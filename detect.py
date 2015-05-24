import cv2
import cv
import numpy as np
from constants import *

WHITE = np.array([255,255,255])
BLACK = np.array([0,0,0])

def crop(img):
    
    [topx, topy, botx, boty] = [0]*4
    
    #find top left corner
    for i in xrange(0, img.shape[0]):
        for j in xrange(img.shape[1]):
            color = img[i,j]
            if any(color != WHITE) and all(np.mod(color, 32) != BLACK):
                [topx, topy] = [i, j]
                break
        if j < (img.shape[1] - 1):
            break
    
    #find bottom right corner
    for i in xrange(img.shape[0] - 1, -1, -1):
        for j in xrange(img.shape[1] - 1, -1, -1):
            color = img[i, j]
            if any(color != WHITE) and all(np.mod(color, 32) != BLACK):
                [botx, boty] = [i, j]
                break
        if j > 0:
            break
    
    img = img[topx:botx, topy:boty]
    return img

def preprocess(img):
    
    img = crop(img)
    img = cv2.cvtColor(img, cv.CV_BGR2GRAY, img)

    blur = cv2.GaussianBlur(img,(5,5),0)
    ret3,th3 = cv2.threshold(blur,0,255,cv2.THRESH_OTSU)
    img = th3

    kernel = np.ones((3,3),np.uint8)
    erosion = cv2.morphologyEx(img,cv2.MORPH_OPEN, kernel,iterations = 8)
    img = erosion
    return img
    
def analyze(img):
    
    img = preprocess(img)
    #We find the outer border
    positions = np.argmin(img, axis=0)  
    
    #Compute the height of drop/pit in the image
    distance = max(positions) - min(positions)  
    
    if distance > THRESHOLD:
        return True
    else:
        return False
    
def main():
    
    for i in range(1, 24):
        img = cv2.imread(SPEC_FOLDER + str(i) + ".png")
        print analyze(img)
        cv2.imshow('image',img)
        cv2.waitKey(0)
        
    cv2.destroyAllWindows()
    
main()
