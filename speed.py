print("Initialising...")
import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
from tracker import *
import time
from handler import *
from line_segment import checkIntersection
from math import dist


model=YOLO('yolov8s.pt')


print("Imported Successfully")

# def RGB(event, x, y, flags, param):
#     if event == cv2.EVENT_MOUSEMOVE :  
#         colorsBGR = [x, y]
#         print(colorsBGR)
        

# cv2.namedWindow('RGB')
# cv2.setMouseCallback('RGB', RGB)

cap=cv2.VideoCapture('../cars.mp4')


my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n") 
#print(class_list)

prev_tracker = None 
count = 0
countDown = 0
filename = "trip_images/trip{}.png"
while True:    
    ret,frame = cap.read()
    if not ret:
        break
   

    results=model.predict(frame)
    a=results[0].boxes.data
    
    px=pd.DataFrame(a).astype("float")
    l=[]
             
    for index,row in px.iterrows():
        x1=int(row[0])
        y1=int(row[1])
        x2=int(row[2])
        y2=int(row[3])
        conf = int(float(row[4])*100)
        d=int(row[5])
        c=class_list[d]
        cv2.putText(frame,str(c),(x1,y1),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),1)
        # cv2.putText(frame,"Conf:"+str(conf)+"%",(x2,y2),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),1)
        l.append(row)
    tracker = Tracker(l)
    
    """
    draw a line from point1 to point 2
    """
    cv2.line(frame,(220,300),(1250,300),(255,255,255),1)
    cv2.line(frame,(150,50),(350,130),(255,255,255),1)
    
    """
    Get both points and then pass to func to get mapping dictionary
    """
    if prev_tracker:
        l1 = prev_tracker.get_center_points()
        l2 = tracker.get_center_points()
        closest_point_dict = get_closest_point_dict(l1,l2)
        
        for k,v in closest_point_dict.items():
            if checkIntersection((220,300),(1250,301),k,v):
                count += 1
                cv2.imwrite(filename.format(count), frame)
                # input()
            if checkIntersection((150,50),(350,130),k,v):
                countDown += 1
                # input()

    
    for rect in tracker.get_rects():
        x1,y1,x2,y2 = rect
        cv2.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),2)

    cv2.putText(frame,('goingdown:-')+str(countDown),(1060,50),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)

    cv2.putText(frame,('goingup:-')+str(count),(1060,100),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)

    prev_tracker = tracker

    cv2.imshow("Car test", frame)
    if cv2.waitKey(1)&0xFF==ord('q'):
        break
cap.release()
cv2.destroyAllWindows()