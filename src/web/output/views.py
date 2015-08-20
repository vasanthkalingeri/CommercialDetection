from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import Template, Context, RequestContext
from django.template.loader import get_template
from web.settings import BASE_DIR
import sys
sys.path.append(BASE_DIR + "/../") #Shift one higher up the parent directory to reach src/
import os
from constants import *
from generate import Generate
import fileHandler
import timeFunc
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson

lines = {} #dictionary, with key as start_secs

def get_dict(labels):
    
    """
        Given labels(output from the labels object in fileHandler.py), it creates a dictionary of the form {key:value}
        Where,
        key = start time in seconds = start_secs
        value = line corresponding to that start time = [start, end, name, start_secs, end_secs]
        Returns: Dictionary
    """
    
    d = {}
    for item in labels:
        #Things are extracted based on labels format
        name = item[2]
        
        #We obtain the start and end time in seconds
        start_secs = timeFunc.get_seconds(item[0])
        end_secs = timeFunc.get_seconds(item[1])
        
        item.append(start_secs)
        item.append(end_secs)
        
        #Create the dictionary
        d[start_secs] = item
        
    return d

@csrf_exempt
def index(request):
    
    """
        The url /output maps to this function.
        Displays the video and the corresponding labels file on the browser.
        This page is called in two ways:
            normal way: When the user visits the site
            Ajax way: When user makes some changes to the labels, the page is reloaded with the help of this function
    """
    
    global lines
    t = get_template('output/index.html')
    
    #If the page requested by the user(and not ajax), we have to read the labels file
    if request.is_ajax() == False:
        #Page was requested by the user
        labels = fileHandler.LabelsFile(infile=BASE_DIR + "/../" + WEB_LABELS).read_lables(skip=False)
        lines = get_dict(labels)
    
    #Since keys are assorted in a dict, we sort them.
    keys = lines.keys()
    keys.sort()
    
    #Now we have start_secs in increasing order, store this value in values.
    values = [lines[key] for key in keys]
    
    html = t.render(Context({'video_path': WEB_VIDEO_NAME, 'item_list': values}))
    return HttpResponse(html)

@csrf_exempt
def update(request):
    
    """
        The url /output/update is mapped to this function.
        This function is always called through ajax
        When the user edits any label on the browser, this function is called to reflect the changes in "lines" dictionary
    """
    
    global lines 
    
    #Obtain the start_secs of the label which the user just edited
    start = int(request.POST.get(u'start'))
    
    #Obtain the new text
    text = str(request.POST.get(u'text'))
    
    #Update the text
    l = lines[start]
    l[2] = text
    lines.update({start:l})
    
    return HttpResponse(simplejson.dumps({'server_response': '1' }))

@csrf_exempt
def save(request):
    
    """
        The url /output/save/ is mapped to this function.
        This function is called with the click of the "Save changes" button.
        The function writes the "lines" dictionary back into the labels file and ends the program.
    """
    
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
    
    """
        The url /output/delete/ maps to this function.
        This function is called by the click of the button '-'.
        It is used to delete the label, intended to be deleted by the user.
        When a label is deleted the following operations take place:
            - the end time of the to be deleted label is written onto the end time of the label preceeding it.
            - the label to be deleted is removed from lines dictionary
    """
    
    global lines
    keys = lines.keys()
    keys.sort()
    start = int(request.POST.get(u'start_sec'))
    end = int(request.POST.get(u'end_sec'))
    
    #Now we find the preceeding label
    for i in range(len(keys)):
        if keys[i] == start:
            break
    
    #This will be the label, just above the label to be deleted
    old_start = keys[i - 1]
    
    #Performing the operations
    
    #We assign the endtime of this to the previous start
    lines[old_start][1] = timeFunc.get_time_string(end)
    lines[old_start][-1] = end
    
    del lines[start]
    
    return HttpResponse(simplejson.dumps({'server_response': '1' }))

@csrf_exempt    
def add(request):
    
    """
        The url /output/add/ maps to this function.
        The function is called by the click of the button '+'.
        It is used to add another label.
        When the function is called, these are the following operations performed.
            - Obtain the new start time in seconds of the next label
            - Make the end time of the new label, equal to the end time of the original label(where + was clicked)
            - Change the end time of the previous label(the label whose + was clicked) to the new start time
    """
    
    global lines 
    actual_start = int(request.POST.get(u'actual_start'))
    start = int(request.POST.get(u'start_sec'))
    end = int(request.POST.get(u'end_sec'))
    
    if start in lines.keys():
        #If already in the dictionary don't update
        return HttpResponse(simplejson.dumps({'server_response': '1' }))
        
    #Now we add the value in lines as well
    lines.update({start: [timeFunc.get_time_string(start), timeFunc.get_time_string(end), UNCLASSIFIED_CONTENT, start, end]})
    
    #We change the "end" of the previous start
    lines[actual_start][1] = timeFunc.get_time_string(start)
    
    print len(lines[start]), len(lines[actual_start])
    return HttpResponse(simplejson.dumps({'server_response': '1' }))
