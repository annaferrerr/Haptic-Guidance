# -*- coding: utf-8 -*-
"""
Control in Human-Robot Interaction Assignment 3: Toy Machine
-------------------------------------------------------------------------------
DESCRIPTION:
This program simulates a toy machine. If you wish to use the Haply device change to Haply = True.
Move the toys to the right part of the screen without touching the wall. Press 'x' to release the toys.
It is also possible to move the base of the gripper using the arrow keys.
Have fun!!
"""
import pygame
import numpy as np
from pantograph import Pantograph
from pyhapi import Board, Device, Mechanisms
from pshape import PShape
import sys, serial, glob
from serial.tools import list_ports
import time

##Select if you are using the Haply device or not
Haply = False
##initialize pygame window

pygame.init()
window = pygame.display.set_mode((800, 500))
pygame.display.set_caption('Virtual Haptic Device')

#Background
background=pygame.image.load('back_better.png')

##add text on top to debugToggle the timing and forces
font = pygame.font.Font('freesansbold.ttf', 18)

pygame.mouse.set_visible(True)  ##Hide cursor by default. 'm' toggles it

##set up the on-screen debugToggle
text = font.render('Virtual Haptic Device', True, (0, 0, 0), (255, 255, 255))
textRect = text.get_rect()
textRect.topleft = (10, 10)

xc, yc = window.get_rect().center  ##center of the screen

##initialize "real-time" clock
clock = pygame.time.Clock()
FPS = 5000  # in Hertz

##define some colors
cWhite = (255, 255, 255)
cDarkblue = (36, 90, 190)
cLightblue = (0, 176, 240)
cRed = (255, 0, 0)
cOrange = (255, 100, 0)
cYellow = (255, 255, 0)
cBlack=(0, 0, 0)
cGrey=(128, 128, 128)
cGreen = (34,139,34)

## Set number of lives

####Pseudo-haptics dynamic parameters, k/b needs to be <1
k = 0.1##Stiffness between cursor and haptic display
b = .8  ##Viscous of the pseudohaptic display

#haptic = pygame.Rect((50, 50), (100, 50))

cursor = pygame.Rect(0, 0, 5, 5)

#define the wall dimensions 
wall = pygame.Rect(600,260,20,260)

list_color = [cDarkblue,cYellow,cOrange,cLightblue,cWhite,cGrey]

#Define boxes
box1 = pygame.Rect(290, 350, 80, 65)
box1img = pygame.image.load('peluche1.png')

box2 = pygame.Rect(180, 415, 90, 60)
box2img = pygame.image.load('peluche2.png')

box3 = pygame.Rect(70, 415, 60, 60)
box3img = pygame.image.load('peluche3.png')

box4 = pygame.Rect(430, 410, 40, 55)
box4img = pygame.image.load('peluche4.png')

box5= pygame.Rect(150, 400, 20, 75)
box5img = pygame.image.load('peluche5.png')

box6= pygame.Rect(360, 380, 55, 95)
box6img = pygame.image.load('peluche6.png')

box_list=[box1,box2,box3,box4,box5,box6]
box_list_img=[box1img,box2img,box3img,box4img,box5img,box6img]

base = pygame.Rect((100, 93), (80, 60))

#define game over
game_over=pygame.Rect(250,166,300,168)
game_over_img=pygame.image.load('game_over.png')

# define the handle 
hhandle = pygame.image.load('Imagen1.png')
haptic = pygame.Rect((50, 50), (100, 50))

xh = np.array(haptic.center)

##Set the old value to 0 to avoid jumps at init
xhold = 0
xmold = 0

# USB serial microcontroller program id data:
def serial_ports():
    """ Lists serial port names """
    ports = list(serial.tools.list_ports.comports())
    result = []
    for p in ports:
        try:
            port = p.device
            s = serial.Serial(port)
            s.close()
            if p.description[0:12] == "Arduino Zero":
                result.append(port)
                print(p.description[0:12])
        except (OSError, serial.SerialException):
            pass
    return result


CW = 0
CCW = 1

haplyBoard = Board
device = Device
SimpleActuatorMech = Mechanisms
pantograph = Pantograph
robot = PShape

#########Open the connection with the arduino board#########
#port = "COM3"
port = serial_ports()#serial_ports()   ##port contains the communication port or False if no device
if port:
    print("Board found on port %s" % port)
    haplyBoard = Board("test", port, 0)
    device = Device(5, haplyBoard)
    pantograph = Pantograph()
    device.set_mechanism(pantograph)

    device.add_actuator(1, CCW, 2)
    device.add_actuator(2, CW, 1)

    device.add_encoder(1, CCW, 241, 10752, 2)
    device.add_encoder(2, CW, -61, 10752, 1)

    device.device_set_parameters()
else:
    print("No compatible device found. Running virtual environnement...")
    # sys.exit(1)

# conversion from meters to pixels
window_scale = 4
textRect = text.get_rect()
textRect.topleft= (30, 20)
# wait until the start button is pressed
run = True
while run:
    for event in pygame.event.get(): # interrupt function
        if event.type == pygame.KEYUP:
            if event.key == ord('e'): # enter the main loop after 'e' is pressed
                time_wait=pygame.time.get_ticks()
                run = False
run = True
ongoingCollision = False
fieldToggle = True
robotToggle = True
debugToggle = False

while run:
    for event in pygame.event.get():
        ##If the window is close then quit
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYUP:
            if event.key == ord('q'):  #Force to quit
                run = False
        key_input = pygame.key.get_pressed()
        if key_input[pygame.K_RIGHT]:
             base[0]+=8
        if key_input[pygame.K_LEFT]:
             base[0]-=8

    pygame.init()
    timer = pygame.time.get_ticks() - time_wait


    window.blit(background,(0,0))
    ##Set the points
    points = 0
    for i in range(len(box_list)):
        if 600 < box_list[i].center[0] < 800 and 350 < box_list[i].center[1] < 500:
            points += box_list[i][2] * box_list[i][3]
    ## Set number of lives
    lives = 3
    for i in range(len(box_list)):
        if 500 < box_list[i][0] < 550:
            if 380 < box_list[i][1] < 420:
                lives = lives - 1
                points = points - 500


    if port and haplyBoard.data_available():  ##If Haply is present
        # Waiting for the device to be available
        #########Read the motorangles from the board#########
        device.device_read_data()
        motorAngle = device.get_device_angles()

        #########Convert it into position#########
        device_position = device.get_device_position(motorAngle)
        xh = np.array(device_position) * 1e3 * window_scale
        xh[0] = np.round(-xh[0] + 300)
        xh[1] = np.round(xh[1] - 60)
        xm = xh  ##Mouse position is not used

    else:
        xh=np.array(haptic.center)
        ##Get mouse position
        cursor.center = pygame.mouse.get_pos()
        xm=np.array(cursor.center)
       # haptic = pygame.Rect(xm, (100, 50))

    fe = np.zeros(2)  ##Environment force is set to 0 initially.

    # wall
    x_wall = 600
    y_wall = 260
    
    if xh[0] > x_wall:
        if xh[1] > y_wall:
            xh[0] = x_wall
    ## Objects fall when touching the wall
    screen_y_limit = 400
    
    if xh[0] > x_wall:
        if xh[1] > y_wall:
            xh[0] = x_wall
    
    if haptic[1] > screen_y_limit:
        haptic[1] = screen_y_limit
    for i in range(len(box_list)):
        if box_list[i][1] > screen_y_limit:
            box_list[i][1] = screen_y_limit

    '''*********** !Student should fill in ***********'''
    if Haply == False:
        if port:
            fe[1] = fe[1]  ##Flips the force on the Y=axis

            ##Update the forces of the device
            device.set_device_torques(fe)
            device.device_write_torques()
            # pause for 1 millisecond
            time.sleep(0.001)
        else:
            ######### Update the positions according to the forces ########
            ##Compute simulation (here there is no inertia)
            ##If the haply is connected xm=xh and dxh = 0
            dxh = (k / b * ( xm - xh) / window_scale - fe / b)  ####replace with the valid expression that takes all the forces into account
            dxh = dxh * window_scale
            xh = np.round(xh + dxh)  ##update new positon of the end effector

    haptic.center = xh

    ######### Graphical output #########
    ##Render the haptic surface

    window.blit(background, (0, 0))
    
    pygame.draw.rect(window, cRed, wall)

    #surface green
    s_g = pygame.Surface((111,230))  # the size of your rect
    s_g.set_alpha(150)                # alpha level
    s_g.fill((34,139,34))           # this fills the entire surface
    window.blit(s_g,(620,260))    # (0,0) are the top-left coordinates


    hapt_sur=pygame.Surface((100,50))
    hapt_sur.set_alpha(0)
    hapt_sur.fill((255, 255, 255))
    window.blit(hapt_sur,(haptic.topleft[0],haptic.topleft[1]))
    window.blit(hhandle,(haptic.topleft[0],haptic.topleft[1]))
    
    for i in range(len(box_list)):
        boxes_surf=pygame.Surface((box_list[i][2],box_list[i][3]))
        boxes_surf.set_alpha(0)
        window.blit(boxes_surf, (box_list[i].topleft[0], box_list[i].topleft[1]))
        window.blit(box_list_img[i], (box_list[i].topleft[0], box_list[i].topleft[1]))


    black_rect=pygame.draw.rect(window, cGrey, base, border_radius=4)
    haptic_center=np.array(haptic.center)
    
    black_center=black_rect.center
    
    
    pygame.draw.line(window, cBlack, black_center , haptic_center,9)
    
    Ax=haptic_center[0]-black_center[0]
    Ay=haptic_center[1]-black_center[1]
    
    
    f_spring=np.array([k*Ax,k*Ay])
    fe=-f_spring
    
    pick_objects=0

    for i in range(len(box_list)):
        if haptic[1] + haptic[3] >= box_list[i][1] and haptic[0] <= box_list[i][0] and box_list[i][0] + box_list[i][2] <= haptic[0] + haptic[2]:
            pick_objects+=1
            if pick_objects<=1:
                box_list[i].center = (xh[0], xh[1] + haptic[3])

                fe[1]+=box_list[i][2]*box_list[i][3] * 0.1 # force factor can modified here

                for event in pygame.event.get():
                    if event.type == pygame.KEYUP:
                        if event.key == ord('x') :
                            while box_list[i][1] < 470-box_list[i][3]:  # height
                                box_list[i][1] += 5
                                run = True
                                # time.sleep(1)
                            else:
                                box_list[i][1] =   box_list[i][1]
        else:
            box_list[i][1]=470-box_list[i][3]
                    

    if Haply == True:
        if port:
            fe[0] =- fe[0]  ##Flips the force on the Y=axis

            ##Update the forces of the device
            device.set_device_torques(fe)
            device.device_write_torques()
            # pause for 1 millisecond
            time.sleep(0.001)
        else:
            ######### Update the positions according to the forces ########
            ##Compute simulation (here there is no inertia)
            ##If the haply is connected xm=xh and dxh = 0
            dxh = (k / b * (xm - xh) / window_scale - fe / b)  ####replace with the valid expression that takes all the forces into account
            dxh = dxh * window_scale
            xh = np.round(xh + dxh)  ##update new positon of the end effector

    haptic.center = xh

    if xh[0] > x_wall:
        if xh[1] > y_wall:
            xh[0] = x_wall

    for i in range(len(box_list)):
        if box_list[i].colliderect(wall):
            box_list[i][0] = 510

    print(fe)
   
    time_limit=40
    
    if timer/1000 > 20:
        gameover_sur=pygame.Surface((300,168))
        gameover_sur.set_alpha(0)
        gameover_sur.fill((255, 255, 255))
        window.blit(gameover_sur,(game_over.topleft[0],game_over.topleft[1]))
        window.blit(game_over_img,(game_over.topleft[0],game_over.topleft[1]))
        
    if timer/1000 > 25:
        g_over_rect = pygame.Rect((250, 166,300,168))
        pygame.draw.rect(window,(205,55,0),g_over_rect,border_radius=4)
        
        font1 = pygame.font.SysFont("Lucida Bride", 50)
        text_final=font1.render("SCORE = " + str(points),True,(0, 0, 0), (205,55,0)) 
        window.blit(text_final,(270,225))
        
    if timer/1000 > 30:
        run = False

    if lives == 0:
        gameover_sur = pygame.Surface((300, 168))
        gameover_sur.set_alpha(0)
        gameover_sur.fill((255, 255, 255))
        window.blit(gameover_sur, (game_over.topleft[0], game_over.topleft[1]))
        window.blit(game_over_img, (game_over.topleft[0], game_over.topleft[1]))

    text_lives = font.render("LIVES= " + str(lives), True, (0, 0, 0), (255, 255, 255))
    textRect2 = text_lives.get_rect()
    textRect2.topleft = (30, 45)
    window.blit(text_lives, textRect2)

    ######### Send forces to the device #########


    black_rect = pygame.draw.rect(window, cGrey, base, border_radius=4)

    text = font.render("SCORE= " + str(points) +"        Time="+ str(int(timer/1000)), True, (0, 0, 0), (255, 255, 255))
    window.blit(text, textRect)
    #window.blit(background, (0, 0))
    pygame.display.flip()
    
    ##Slow down the loop to match FPS
    clock.tick(FPS)

pygame.display.quit()
pygame.quit()