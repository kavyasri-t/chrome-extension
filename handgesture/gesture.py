import cv2
import numpy as np
import math
from websocket_server import WebsocketServer

stop = False
global id1
global id2
global id3
global id4
id1=0
id2=0
id3=0
id4=0
def new_client(client,server):
    print("New client connected and was given id %d" % client['id'])
    server.send_message_to_all("Hey all, a new client has joined us")
    cap = cv2.VideoCapture(0)
    id1=0
    id2=0
    id3=0
    id4=0
    j=""
    while(cap.isOpened()):
        ret, img = cap.read()
        cv2.rectangle(img,(500,500),(100,100),(0,255,0),0)
        crop_img = img[100:500, 100:500]
        grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        value = (35, 35)
        blurred = cv2.GaussianBlur(grey, value, 0)
        _, thresh1 = cv2.threshold(blurred, 127, 255,
                                   cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        #cv2.imshow('Thresholded', thresh1)
        contours, hierarchy = cv2.findContours(thresh1.copy(),cv2.RETR_TREE, \
                cv2.CHAIN_APPROX_NONE)
        max_area = -1
        for i in range(len(contours)):
            cnt=contours[i]
            area = cv2.contourArea(cnt)
            if(area>max_area):
                max_area=area
                ci=i
        cnt=contours[ci]
        x,y,w,h = cv2.boundingRect(cnt)
        cv2.rectangle(crop_img,(x,y),(x+w,y+h),(0,0,255),0)
        hull = cv2.convexHull(cnt)
        drawing = np.zeros(crop_img.shape,np.uint8)
        cv2.drawContours(drawing,[cnt],0,(0,255,0),0)
        cv2.drawContours(drawing,[hull],0,(0,0,255),0)
        hull = cv2.convexHull(cnt,returnPoints = False)
        defects = cv2.convexityDefects(cnt,hull)
        count_defects = 0
        cv2.drawContours(thresh1, contours, -1, (0,255,0), 3)
        for i in range(defects.shape[0]):
            s,e,f,d = defects[i,0]
            start = tuple(cnt[s][0])
            end = tuple(cnt[e][0])
            far = tuple(cnt[f][0])
            a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
            c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
            angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57
            if angle <= 90:
                count_defects += 1
                cv2.circle(crop_img,far,1,[0,0,255],-1)
            #dist = cv2.pointPolygonTest(cnt,far,True)
            cv2.line(crop_img,start,end,[0,255,0],2)
            #cv2.circle(crop_img,far,5,[0,0,255],-1)
        if count_defects == 1 and id1==0:
            id1=1
            id2=0
            id3=0
            id4=0
            j="Scroll Up"
            #cv2.putText(img,"Scroll Up", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
            server.send_message_to_all('scroll-up')
            count_defects=0
        elif count_defects == 2 and id2==0:
            id2=1
            id1=0
            id3=0
            id4=0
            str = "Scroll Down"
            j="Scroll Down"
            #cv2.putText(img, str, (5,50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
            server.send_message_to_all('scroll-down')
            count_defects=0
        elif count_defects == 3 and id3==0:
            id3=1
            id1=0
            id2=0
            id4=0
            j="Zoom Out"
            #cv2.putText(img,"Zoom Out", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
            server.send_message_to_all('zoom-out')
            count_defects=0
        elif count_defects == 4 and id4==0:
            id4=1
            id1=0
            id2=0
            id3=0
            j="Zoom In"
            #cv2.putText(img,"Zoom In", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
            server.send_message_to_all('zoom-in')
            count_defects=0
        else:
            print("No Gesture")
            #cv2.putText(img,"No Gesture", (50,50),\
             #   cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
        cv2.putText(img,j, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
        #cv2.imshow('drawing', drawing)
        #cv2.imshow('end', crop_img)
        cv2.imshow('Gesture', img)
        all_img = np.hstack((drawing, crop_img))
        #cv2.imshow('Contours', all_img)
        k = cv2.waitKey(10)
        if k == 27:
            break
def client_left(client, server):
    stop = True
    print("Client(%d) disconnected" % client['id'])

# Called when a client sends a message


def message_received(client, server, message):
    if len(message) > 200:
        message = message[:200] + '..'
    print("Client(%d) said: %s" % (client['id'], message))

PORT = 9001
server = WebsocketServer(PORT,host="192.168.1.102")#192.168.43.56
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()
