import pygame
import random
import time
import HandTrackingModule as htm
import cv2 as cv
import numpy as np
import os

pygame.init()

window_width=800
window_height=800

fruit_icon=[]
half_icon=[]
filepath_fruit='Fruit'
filepath_half='Half'
dirListfruit=os.listdir(filepath_fruit)
dirListhalf=os.listdir(filepath_half)

for link in dirListfruit:
    icon=pygame.image.load(f'{filepath_fruit}/{link}')
    fruit_icon.append(icon)
for link in dirListhalf:
    icon=pygame.image.load(f'{filepath_half}/{link}')
    half_icon.append(icon)


class fruit:
    def __init__(self,x,y,vx,vy,icon,half):
        self.x=x
        self.y=y
        self.vx=vx
        self.vy=vy
        self.icon=icon
        self.hitbox=pygame.transform.rotozoom(icon,0,0.75)
        self.half_left=pygame.transform.flip(half,True,False)
        self.half_right=half
        self.avalable=True
        self.apart=icon.get_rect().width//2-10

    @property
    def rect(self):
        return self.hitbox.get_rect(center=(self.x,self.y))
    @property
    def half_left_rect(self):
        return self.half_left.get_rect(center=(self.x-self.apart,self.y))    
    @property
    def half_right_rect(self):
        return self.half_right.get_rect(center=(self.x+self.apart,self.y))

class bomb:
    def __init__(self,x,y,vx,vy):
        self.x=x
        self.y=y
        self.vx=vx
        self.vy=vy
        self.icon=pygame.image.load('Image/bomb.png')
        self.half=pygame.image.load('Image/explosion.png')
        self.avalable=True

    @property
    def rect(self):
        return self.icon.get_rect(center=(self.x,self.y))

def get_fruit():
    x=random.randint(0,window_width)
    y=window_height
    vx=int((window_width//2-x)/100*random.randint(1,5))
    vy=random.randint(20,40)
    icon=random.choice(fruit_icon)
    return fruit(x,y,vx,vy,icon,half_icon[fruit_icon.index(icon)])

def get_bomb():
    x=random.randint(0,window_width)
    y=window_height
    vx=int((window_width//2-x)/100*random.randint(1,5))
    vy=random.randint(20,40)
    return bomb(x,y,vx,vy)


def is_collided(ob1,ob2):
    if ob1.colliderect(ob2):
        return True
    return False


def print_text(surface,string,x,y,size,color):
    font=pygame.font.SysFont('comicsans',size)
    render=font.render(string,True,color)
    font.set_bold(True)
    surface.blit(render,(x,y))


def main(screen):
    start_time=time.time()
    fruit_time=time.time()
    fruit_spawn_time=2
    bomb_time=time.time()
    bomb_spawn_time=random.randint(5,10)
    fruitList=[]
    bombList=[]
    mouseList=[]
    score=0
    run=True
    back=pygame.image.load('Image/back.jpg')
    slash=pygame.mixer.Sound('Sound/slash.mp3')
    explosion=pygame.mixer.Sound('Sound/bomb.mp3')
    clock=pygame.mixer.Sound('Sound/clock.mp3')

    vid=cv.VideoCapture(0)
    detector=htm.handDetector(minDet=0.8,minTrack=0.8)

    while run:
        # mouseList.append(pygame.mouse.get_pos())

        isTrue,unflip_frame=vid.read()
        screen.blit(back,(0,0))
        frame=cv.flip(unflip_frame,1)
        frame=detector.find_landmark(frame,draw=False)
        if detector.result.multi_hand_landmarks:
            print_text(screen,'CONNECTED',300,10,50,(255,255,255))
            lmlisk=detector.find_position(frame,0)    
            x2,y2=lmlisk[8][1],lmlisk[8][2]
            xm=int(np.interp(x2,[100,540],[0,window_width]))
            ym=int(np.interp(y2,[100,380],[0,window_height]))
            mouseList.append((xm,ym))
        else:
            pygame.time.delay(15)


        print_text(screen,f'SCORE:{score}',10,10,50,(255,255,255))
        print_text(screen,f'TIME:{60-int(time.time()-start_time)}',600,10,50,(255,255,255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
        if time.time()-fruit_time>fruit_spawn_time:
            for i in range(random.randint(1,4)):
                fruitList.append(get_fruit())
            fruit_time=time.time()        
        if time.time()-bomb_time>bomb_spawn_time:
            for i in range(random.randint(1,2)):
                bombList.append(get_bomb())
            bomb_time=time.time()
            bomb_spawn_time=random.randint(5,10)
        if time.time()-start_time>60:
            run= False
        for val in fruitList:
            val.x+=val.vx
            val.y-=val.vy
            val.vy-=1
            if val.y>window_height:
                fruitList.remove(val)
            else:
                if val.avalable:
                    screen.blit(val.icon,val.rect)
                else:
                    screen.blit(val.half_right,val.half_right_rect)
                    screen.blit(val.half_left,val.half_left_rect)

        for val in bombList:
            val.x+=val.vx
            val.y-=val.vy
            val.vy-=2
            if val.y>window_height:
                bombList.remove(val)
            else:
                screen.blit(val.icon,val.rect)

        if len(mouseList)>5:
            mouseList.pop(0)
            hit=pygame.draw.lines(screen,(255,255,255),False,mouseList,width=3)
            for val in fruitList:
                if val.avalable==True:
                    if is_collided(val.rect,hit):
                        score+=1
                        slash.play()
                        val.avalable=False
            for val in bombList:
                if is_collided(val.rect,hit):
                    score-=10
                    explosion.play()
                    fruitList.clear()
                    bombList.remove(val)
                    screen.blit(val.half,val.rect)
        if clock:
            if time.time()-start_time>55:
                clock.play()
                clock=None

        pygame.display.update()


    screen.blit(back,(0,0))
    print_text(screen,f'SCORE:{score}',250,window_height//2-200,100,(255,255,255))
    print_text(screen,'PRESS TO PLAY',150,window_height//2,100,(255,255,255))
    print_text(screen,'AGAIN',300,window_height//2+100,100,(255,255,255))


def main_menu():
    screen=pygame.display.set_mode((window_width,window_height))
    background=pygame.image.load('Image/background.jpg')
    screen.blit(background,(0,0))
    print_text(screen,'PRESS TO PLAY',150,window_height//2,100,(255,0,0))
    run=True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(screen)
        pygame.display.update()


        
if __name__ == '__main__':
    main_menu()