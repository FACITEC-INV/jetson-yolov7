import numpy as np
from sort.sort import Sort
from counter import *

mot_tracker = Sort()

def update(detections,categories,frame):
    drawLines(frame)
    normalizedDet = []
    for obj in detections:
        x1,y1,x2,y2 = obj['box']
        if obj['classId'] == 2 or obj['classId'] == 7:
            normalizedDet.append([x1,y1,x2,y2,obj['conf'],obj['classId']])
    if(len(normalizedDet)>0):
        tracks = mot_tracker.update(np.array(normalizedDet))
    else:
        tracks = np.empty((0, 5))
    for track in tracks:
        xmin,ymin,xmax,ymax,track_id,_,label_idx = track.astype(int)
        countUk(track_id,categories[label_idx],int((xmin+xmax)/2),int((ymin+ymax)/2),frame)
    return tracks
