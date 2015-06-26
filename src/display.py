import os
from django import template
from constants import *
import sys
import fileHandler
import timeFunc
from bs4 import BeautifulSoup

sys.path.append(WEB_FOLDER)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

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
    
def render_page(video_name, page_name=RESULTS_HTML):
    
    html = open(OUTPUT_TEMPLATE).read()   
    labels = fileHandler.LabelsFile(infile=OUTPUT).read_lables(skip=False)    
    t = template.Template(html)
    c = template.Context({'video_path':video_name, 'item_list':get_list(labels)})
    html = t.render(c)
    f = open(page_name, 'w')
    f.write(html)
    
def update_output(page_name=RESULTS_HTML, output_file='temp.txt'):
    
    page = open(page_name).read()
    soup = BeautifulSoup(page)
    labels = fileHandler.LabelsFile(outfile=output_file)
    for tr in soup.find_all('tr')[5:]:
        tds = tr.find_all('td')
        start = tds[0].string
        end = tds[1].string
        name = tds[2].find('button').string
        labels.write_labels([start, end, name])
        

def test():
            
    render_page('../../data/out1.webm')
    #update_output()

test()
