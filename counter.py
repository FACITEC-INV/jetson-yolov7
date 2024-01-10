from datetime import datetime
from db import Detection
import cv2 

def display(displayResult):
    global _display
    _display = displayResult
    
font = cv2.FONT_HERSHEY_SIMPLEX

#(indice, orientacion, x1,y1,x2,y2)
countLines=[
    (0,"hr",0.90,0.18,0.90,0.53),
    (1,"vd",0.15,0.60,0.90,0.80)
]

detArea = ["centro","mapy"] 

counter=[0,0]

uk = [dict(),dict()]

def countVD(idx,rx1,ry1,rx2,ry2,m,x,y,trackId,className):
    ly = int((m*(x-rx1))+ry1) if m != None else ry1
    if y <= ly and str(trackId) not in uk[idx] and x >= rx1 and x <= rx2:
        uk[idx][str(trackId)] = datetime.now()
    elif y > ly and str(trackId) in uk[idx] and x >= rx1 and x <= rx2:
        counter[idx] = counter[idx]+1
        Detection.create(zona=detArea[int(idx)],clase=className,fecha=uk[idx][str(trackId)],enviado=False)
        del uk[idx][str(trackId)]
        
def countVU(idx,rx1,ry1,rx2,ry2,m,x,y,trackId,className):
    ly = int((m*(x-rx1))+ry1) if m != None else ry1
    if y >= ly and str(trackId) not in uk[idx] and x >= rx1 and x <= rx2:
        uk[idx][str(trackId)] = datetime.now()
    elif y < ly and str(trackId) in uk[idx] and x >= rx1 and x <= rx2:
        counter[idx] = counter[idx]+1
        Detection.create(zona=detArea[int(idx)],clase=className,fecha=uk[idx][str(trackId)],enviado=False)
        del uk[idx][str(trackId)]
        
def countHR(idx,rx1,ry1,rx2,ry2,m,x,y,trackId,className):
    lx = int(((y-ry1)/m)+rx1) if m != None else rx1
    if x <= lx and str(trackId) not in uk[idx] and y >= ry1 and y <= ry2:
        uk[idx][str(trackId)] = datetime.now()
    elif x > lx and str(trackId) in uk[idx] and y >= ry1 and y <= ry2:
        counter[idx] = counter[idx]+1
        Detection.create(zona=detArea[int(idx)],clase=className,fecha=uk[idx][str(trackId)],enviado=False)
        del uk[idx][str(trackId)]
        
def countHL(idx,rx1,ry1,rx2,ry2,m,x,y,trackId,className):
    lx = int(((y-ry1)/m)+rx1) if m != None else rx1
    if x >= lx and str(trackId) not in uk[idx] and y >= ry1 and y <= ry2:
        uk[idx][str(trackId)] = datetime.now()
    elif x < lx and str(trackId) in uk[idx] and y >= ry1 and y <= ry2:
        counter[idx] = counter[idx]+1
        Detection.create(zona=detArea[int(idx)],clase=className,fecha=uk[idx][str(trackId)],enviado=False)
        del uk[idx][str(trackId)]

def countUk(trackId,className,x,y,img):
    height, width = img.shape[:2]
    for idx,o,px1,py1,px2,py2 in countLines:
        x1=int(width*px1)
        y1=int(height*py1)
        x2=int(width*px2)
        y2=int(height*py2)
        if(_display):
            img = cv2.putText(img, str(trackId), (x, y), font, 0.2, (100, 255, 0), 1, cv2.LINE_AA) 
        m = (y2-y1)/(x2-x1) if (x2-x1) != 0 else None
        print(trackId,className)
        if o == "vd":
            countVD(idx,x1,y1,x2,y2,m,x,y,trackId,className)
        if o == "vu":
            countVU(idx,x1,y1,x2,y2,m,x,y,trackId,className)
        if o == "hl":
            countHL(idx,x1,y1,x2,y2,m,x,y,trackId,className)
        if o == "hr":
            countHR(idx,x1,y1,x2,y2,m,x,y,trackId,className)
            
def drawLines(img):
    height, width = img.shape[:2]
    for _,_,px1,py1,px2,py2 in countLines:
        x1=int(width*px1)
        y1=int(height*py1)
        x2=int(width*px2)
        y2=int(height*py2)
        if(_display):
            img = cv2.line(img, (x1,y1), (x2,y2), (0, 255, 0), 2)
