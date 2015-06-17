import cv2
from constants import *
import timeFunc
import os
import numpy as np
from matplotlib import pyplot as plt
import pylab
import ffmpeg
import cv
import sys
import cPickle as pickle
from sklearn.covariance import EllipticEnvelope

def auto_canny(image, sigma=0.33):
    
    #Guassian blurrs the image and then edge detects it

	# compute the median of the single channel pixel intensities
	v = np.median(image)
    
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	blur = cv2.GaussianBlur(image, (3, 3), 0)
	edged = cv2.Canny(blur, lower, upper)
 
	# return the edged image
	return edged

def get_color_info(img1, img2, advanced=False):
    
    #Get the aspect ratio
    #---Yet to be implemented --- #
    
    gray2 = cv2.cvtColor(img2, cv.CV_BGR2GRAY)
    gray1 = cv2.cvtColor(img1, cv.CV_BGR2GRAY)
    hist1 = cv2.calcHist([gray1],[0],None,[256],[0,256])
    hist2 = cv2.calcHist([gray2],[0],None,[256],[0,256])
    diff = cv2.compareHist(hist1, hist2, cv.CV_COMP_CORREL)
    
    hsl2 = cv2.cvtColor(img2, cv.CV_BGR2HSV)
    h,s,l2 = cv2.split(hsl2)
    
    hsl1 = cv2.cvtColor(img1, cv.CV_BGR2HSV)
    h,s,l1 = cv2.split(hsl1)
    
    #Average luminance
    avg_lum = (np.mean(l1) + np.mean(l2)) / 2 
    
    #Uniformity of the image
    uniformity = (np.var(l1) + np.mean(l2)) / 2
    
    #Initially, edge change ratio and edge stable ratio are -1
    ecr = esr = -1
    
    if diff < HIST_CHANGE_THRESH:
        
        #If histogram difference is less than a threshold, then we confirm with edge information
        
        #Edge change ratio
        edge1 = auto_canny(gray1) / 255
        edge2 = auto_canny(gray2) / 255
        kernel = np.ones((5,5),np.uint8)
        temp1 = cv2.dilate(edge1, kernel, iterations=2)
        temp2 = cv2.dilate(edge2, kernel, iterations=2)
        temp1 = 1 - temp1
        temp2 = 1 - temp2
        res1 = np.bitwise_and(temp2, edge1)
        res2 = np.bitwise_and(temp1, edge2)
        ec1 = np.sum(res1)
        ec2 = np.sum(res2)
        ecr = max(ec1, ec2) / np.prod(np.shape(edge2))
        
        #Calculating the edge stable ratio
        esr = (np.sum(np.bitwise_and(edge1, edge2)) + 1) / (np.sum(np.bitwise_or(edge1, edge2) + 1) * 1.0)
        
    if advanced is False:
        return [diff, avg_lum, uniformity, ecr, esr]

def extract_video_features(video_name, filename, clf=None, labels_file="", train=False):
    
    cap = cv2.VideoCapture(video_name)
    present1, img1 = cap.read()
    y = []
    x = []
    f = open(filename, 'w')
    
    #Location of splits for that video file, which would be ideally loaded from labels file
    times = ['9:37', '9:52', '10:06', '10:37', '10:39', '11:08', '11:16', '13:20', '13:48', '14:04', '14:33', '15:05', '15:18']
    
    times = [timeFunc.get_time_string(timeFunc.get_seconds(i) - (9*60)) for i in times]
    i = 0
    X = np.array([])
#    y = np.array([])
    m = 0
    while present1:
        
        present2, img2 = cap.read()
        time_now = timeFunc.get_time_string(i / 60)
        if present2:
            #If the images can be read
            features = get_color_info(img1, img2)
            if features[-1] != -1:
                #We might have to check for boundaries
                print clf.predict(np.array(features))
                if train is True:
#                    X = np.append(X, features)
                    label = 0
                    if time_now in times:
                        X = np.append(X, features)
                        m += 1
                        label = 1
#                    y = np.append(y, label)
                elif clf.predict(np.array(features)) == 1:
                    print "WOHOOO!!", timeFunc.get_time_string(i / 60)
                    f.write(timeFunc.get_time_string(i / 60) + "\n")
            i += 1
        else:
            #EOF
            break
        
        #Writing progress
        sys.stdout.write('\r')
        sys.stdout.write(timeFunc.get_time_string(i / 60))
        sys.stdout.flush()
        
        cv2.imshow("image", img2)
        cv2.waitKey(3)
        
        img1 = img2
        
    cv2.destroyAllWindows()
    f.close()
    clf = None
#    pickle.dump([X, y], open('data', 'wb'))
#    [X, y] = pickle.load(open('data'))
    features = [1]*5
    if train is True:
        X = np.resize(X, (y.shape[0], len(features)))
        clf = EllipticEnvelope()
        clf = clf.fit(X)
        clf = clf.decision_function(X)
    return clf

def train_data():
    
    clf = extract_video_features("shot_det.mpg", "shots.csv", train=True)
    pickle.dump(clf, open("class.data", 'wb'))
            
def test():  
    
    clf = pickle.load(open("class.data"))  
    clf = extract_video_features("shottest.mpg", "shots.csv", clf=clf)
    
#    train_data()

test()
