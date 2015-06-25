from django.shortcuts import render
from django.http import HttpResponse
from django.template import Template, Context
from django.template.loader import get_template

from web.settings import BASE_DIR
import sys
sys.path.append(BASE_DIR + "/../") #Shift one higher up the parent directory 
import os
from constants import *
import fileHandler
import timeFunc

#<button onClick='play({{item.3}});' id='{{item.4}}'>{{item.2}}</button>

def get_list(labels):
    
    l = []
    for item in labels:
        name = item[2]
        t3 = timeFunc.get_seconds(item[0])
        hid = name[0:2] + str(t3)
        item.append(t3)
        item.append(hid)
        l.append(item)
    return l

def index(request):
    
    t = get_template('output/index.html')
    labels = fileHandler.LabelsFile(infile=BASE_DIR + "/../" + OUTPUT).read_lables(skip=False)
    html = t.render(Context({'video_path': 'out1.webm', 'item_list': get_list(labels)}))
    return HttpResponse(html)
