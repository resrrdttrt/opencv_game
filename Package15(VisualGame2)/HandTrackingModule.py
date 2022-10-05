import cv2 as cv
import mediapipe as mp
import numpy as np
import time

class handDetector():
    def __init__(self,mode=False,maxHands=2,model=1,minDet=0.5,minTrack=0.5):
        self.static_image_mode=mode
        self.max_num_hands=maxHands
        self.model_complexity=model
        self.min_detection_confidence=minDet
        self.min_tracking_confidence=minTrack

        self.mpHands=mp.solutions.hands
        self.mpDraws=mp.solutions.drawing_utils
        self.hands=self.mpHands.Hands(self.static_image_mode,self.max_num_hands,self.model_complexity,self.min_detection_confidence,self.min_tracking_confidence)

    def find_landmark(self,img,draw=True):
        imgRGB=cv.cvtColor(img,cv.COLOR_BGR2RGB) #mediapipe work for RGB image
        self.result=self.hands.process(imgRGB)
        if draw:
            if self.result.multi_hand_landmarks: #la 1 list 21 diem khac nhau tren tay va toa do tuong ung cua chung
                for value in self.result.multi_hand_landmarks:
                    self.mpDraws.draw_landmarks(img,value,self.mpHands.HAND_CONNECTIONS)
        return img

    def find_position(self,img,hand_number):
        lmlisk=[]
        if self.result.multi_hand_landmarks:
            myhand=self.result.multi_hand_landmarks[hand_number]
            for id,lm in enumerate(myhand.landmark):
                h,w,c=img.shape
                cx,cy=int(lm.x*w),int(lm.y*h)
                lmlisk.append([id,cx,cy])
        return lmlisk
    
    def find_handedness(self,hand_number):
        hdlisk=[]
        if self.result.multi_handedness: #list index=1 label=right,index=0 label=left
            myhand=self.result.multi_handedness[hand_number].classification[hand_number]
            hdlisk.append([myhand.index,myhand.label])
        return hdlisk

    def count_finger(self,img,hand_number):
        lmlisk=self.find_position(img,hand_number)
        indexList=[]
        tipList=[8,12,16,20]
        if lmlisk:
            if max(lmlisk[4][1],lmlisk[0][1])>lmlisk[2][1]>min(lmlisk[4][1],lmlisk[0][1]):
                indexList.append(1)
            else:
                indexList.append(0)
            for i in range(4):
                if lmlisk[tipList[i]][2]>lmlisk[tipList[i]-2][2]:
                    indexList.append(0)
                else:
                    indexList.append(1)
            return indexList


def main():
    curTime=0
    preTime=0
    cap=cv.VideoCapture(0) 
    detector=handDetector()
    while True:
        isTrue,unflip_frame=cap.read()
        if isTrue:
            frame=cv.flip(unflip_frame,1)
            print(frame.shape[0],frame.shape[1])
            frame=detector.find_landmark(frame)

            curTime=time.time()
            fps=1//(curTime-preTime)
            preTime=curTime
            
            cv.putText(frame,str(fps),(30,30),cv.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1)
            cv.imshow('Camera',frame)
            if cv.waitKey(1)==ord('a'):
                break
    cap.release()
    cv.destroyAllWindows()

if __name__=='__main__':
    main()