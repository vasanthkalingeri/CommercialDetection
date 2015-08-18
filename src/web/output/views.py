from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import Template, Context, RequestContext
from django.template.loader import get_template
from web.settings import BASE_DIR
import sys
sys.path.append(BASE_DIR + "/../") #Shift one higher up the parent directory 
import os
from constants import *
from generate import Generate
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
        item.append(start_secs)
        item.append(end_secs)
        d[start_secs] = item
    return d

@csrf_exempt
def index(request):
    
    global lines
    t = get_template('output/index.html')
    os.system('cp ' + BASE_DIR + "/../" + OUTPUT + " "+ BASE_DIR + "/../" + WEB_LABELS)
    if request.is_ajax() == False:
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
    start = int(request.POST.get(u'start'))
    text = str(request.POST.get(u'text'))
    #Now we update the value in lines as well
#    lines[start][2] = text
    l = lines[start]
    l[2] = text
    lines.update({start:l})
#    print "Updated", lines[start]
    return HttpResponse(simplejson.dumps({'server_response': '1' }))

@csrf_exempt
def save(request):
    
    global lines
    labels = fileHandler.LabelsFile(outfile=BASE_DIR + "/../" + WEB_LABELS)
    keys = lines.keys()
    keys.sort()
    lines_list = [lines[key] for key in keys]
    for line in lines_list:
        l = [line[i] for i in range(3)]
        labels.write_labels(l)
    return HttpResponse('Successfully updated :-)')

@csrf_exempt
def delete(request):
    
    global lines
    keys = lines.keys()
    keys.sort()
    start = int(request.POST.get(u'start_sec'))
    end = int(request.POST.get(u'end_sec'))
    
    #Now we find the key which had the previous start
    for i in range(len(keys)):
        if keys[i] == start:
            break
    old_start = keys[i - 1]
    
    #We assign the endtime of this to the previous start
    lines[old_start][1] = timeFunc.get_time_string(end)
    lines[old_start][-1] = end
    
    del lines[start]
    
    print lines[old_start]
    return HttpResponse(simplejson.dumps({'server_response': '1' }))

@csrf_exempt    
def add(request):
    
    global lines 
    actual_start = int(request.POST.get(u'actual_start'))
    start = int(request.POST.get(u'start_sec'))
    end = int(request.POST.get(u'end_sec'))
    
    if start in lines.keys():
        #If already in the dictionary don't update
        return HttpResponse(simplejson.dumps({'server_response': '1' }))
        
    #Now we add the value in lines as well
    lines.update({start: [timeFunc.get_time_string(start), timeFunc.get_time_string(end), UNCLASSIFIED_CONTENT, start, end]})
    
#    print lines[actual_start]
    #We change the "end" of the previous start
    lines[actual_start][1] = timeFunc.get_time_string(start)
    
    print len(lines[start]), len(lines[actual_start])
    return HttpResponse(simplejson.dumps({'server_response': '1' }))
