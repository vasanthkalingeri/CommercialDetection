from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import Template, Context, RequestContext
from django.template.loader import get_template
from web.settings import BASE_DIR
import sys
sys.path.append(BASE_DIR + "/../") #Shift one higher up the parent directory 
import os
from constants import *
import fileHandler
import timeFunc
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
#from generate import Generate

lines = {} #dictionary, with key as start_secs

def get_dict(labels):
    
#    Each element of list is
#        [start, end, name, start_secs, end_secs]
    d = {}
    for item in labels:
        name = item[2]
        start_secs = timeFunc.get_seconds(item[0])
        end_secs = timeFunc.get_seconds(item[1])
        hid = name[0:2] + str(start_secs) #Forms unique id based on type of content and start of it in seconds
        item.append(start_secs)
        item.append(end_secs)
        d[start_secs] = item
    return d

@csrf_exempt
def index(request):
    
    global lines
    t = get_template('output/index.html')
    os.system('cp ' + BASE_DIR + "/../" + OUTPUT + " "+ BASE_DIR + "/../" + WEB_LABELS)
    labels = fileHandler.LabelsFile(infile=BASE_DIR + "/../" + WEB_LABELS).read_lables(skip=False)
    lines = get_dict(labels)
    keys = lines.keys()
    keys.sort()
    values = [lines[key] for key in keys]
    html = t.render(Context({'video_path': WEB_VIDEO_NAME, 'item_list': values}))
    return HttpResponse(html)

@csrf_exempt
def update(request):
    
    global lines 
    print request.POST
    start = int(request.POST.get(u'start')[0])
    text = str(request.POST.get(u'text'))
    #Now we update the value in lines as well
    lines[start][2] = text
    print lines
    return HttpResponse(simplejson.dumps({'server_response': '1' }))

@csrf_exempt
def save(request):
    
    global lines
    print BASE_DIR + "/../" + WEB_LABELS
    labels = fileHandler.LabelsFile(outfile=BASE_DIR + "/../" + WEB_LABELS)
    print lines
    print "Creating the new labels file..."
    keys = lines.keys()
    keys.sort()
    lines_list = [lines[key] for key in keys]
    print lines_list
    for line in lines_list:
        start_secs = str(line[3])
        start = unicode('start' + start_secs)
        end = unicode('end' + start_secs)
        name = unicode('name' + start_secs)
        l = [str(request.POST.get(start)), str(request.POST.get(end)), str(request.POST.get(name))]
        print l
        labels.write_labels(l)
    return HttpResponse('Thank you for teaching me :-)')
