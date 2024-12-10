print("Initialising...")
import cv2
import pandas as pd
from ultralytics import YOLO
import os

from tracker import *
from handler import *
from line_segment import checkIntersection

if not os.path.exists("./yolo11n_ncnn_model"):
    model=YOLO('yolo11n.pt')
    model.export(format="ncnn")
ncnn_model = YOLO("./yolo11n_ncnn_model")

print("Imported Successfully")

cap=cv2.VideoCapture('cars.mp4')


my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n") 

prev_tracker = None 
count = 0
countDown = 0
folder = "trip_images"
filename = folder+"/trip{}.png"
if not os.path.exists(folder):
    os.makedirs(folder)
frame_count=0
while True:    
    ret,frame = cap.read()
    if not ret:
        break
    results=ncnn_model(frame)
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
                cv2.imwrite(filename.format(countDown).replace(".png","_down.png"), frame)
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
