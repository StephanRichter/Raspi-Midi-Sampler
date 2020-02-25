#!/usr/bin/python3
import time
import RPi.GPIO as GPIO

# Zuordnung der GPIO Pins (ggf. anpassen)
LCD_RS = 14
LCD_E  = 15
LCD_DATA4 = 18
LCD_DATA5 = 23
LCD_DATA6 = 24
LCD_DATA7 = 25
BUTTON = 8

PAUSE1 = 0.0005
PAUSE2 = 0.0005

L = GPIO.LOW
H = GPIO.HIGH

# Intruktionen gemäß https://www.sprut.de/electronic/lcd/ aufgebaut

# display modes
ONE_LINE = L
TWO_LINE = H

# 5x11 or 5x8?
EIGHT_DOTS = L
ELEVEN_DOTS = H

# interface type
FOUR_BIT_INTER = L
EIGHT_BIT_INTER = H

# left-to-right or right-to-left?
L2R = H
R2L = L

# move display content on write?
SHIFT = L
NO_SHIFT = H

# cursor type
BLOCK = H
UNDERLINE = L

# enable/disable cursor
ENABLED = H
DISABLED = L

# codes for special characters
AE = 225
OE = 239
UE = 245

line1 = ""
line2 = ""
line3 = ""
line4 = ""

def push4(rs,d4,d5,d6,d7):
    GPIO.output(LCD_RS,rs);
    #time.sleep(PAUSE1)
    GPIO.output(LCD_E,H)
    time.sleep(PAUSE1)
    GPIO.output(LCD_DATA4,d4)
    GPIO.output(LCD_DATA5,d5)
    GPIO.output(LCD_DATA6,d6)
    GPIO.output(LCD_DATA7,d7)
    time.sleep(PAUSE2)
    GPIO.output(LCD_E,L)
    time.sleep(PAUSE1)

def push_text(d0,d1,d2,d3,d4,d5,d6,d7):
    push4(H,d4,d5,d6,d7)
    push4(H,d0,d1,d2,d3)
    
def push_ctrl(d0,d1,d2,d3,d4,d5,d6,d7):
    push4(L,d4,d5,d6,d7)
    push4(L,d0,d1,d2,d3)
    

def gpio_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LCD_E, GPIO.OUT)
    GPIO.setup(LCD_RS, GPIO.OUT)
    GPIO.setup(LCD_DATA4, GPIO.OUT)
    GPIO.setup(LCD_DATA5, GPIO.OUT)
    GPIO.setup(LCD_DATA6, GPIO.OUT)
    GPIO.setup(LCD_DATA7, GPIO.OUT)
    GPIO.output(LCD_E,L);
    GPIO.setup(BUTTON,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

def clear():
    push_ctrl(H,L,L,L,L,L,L,L)

def add_enter_symbol():
    push_ctrl(L,L,L,L,L,L,H,L) # CG-Adresse 0 setzen
    push_text(H,L,L,L,L,L,L,L)
    push_ctrl(H,L,L,L,L,L,H,L) # CG-Adresse 1 setzen
    push_text(H,L,L,L,L,L,L,L)
    push_ctrl(L,H,L,L,L,L,H,L) # CG-Adresse 2 setzen
    push_text(H,L,L,L,L,L,L,L)
    push_ctrl(H,H,L,L,L,L,H,L) # CG-Adresse 3 setzen
    push_text(H,L,H,L,L,L,L,L)
    push_ctrl(L,L,H,L,L,L,H,L) # CG-Adresse 4 setzen
    push_text(H,L,L,H,L,L,L,L)
    push_ctrl(H,L,H,L,L,L,H,L) # CG-Adresse 5 setzen
    push_text(H,H,H,H,H,L,L,L)
    push_ctrl(L,H,H,L,L,L,H,L) # CG-Adresse 6 setzen
    push_text(L,L,L,H,L,L,L,L)
    push_ctrl(H,H,H,L,L,L,H,L) # CG-Adresse 7 setzen
    push_text(L,L,H,L,L,L,L,L)

    
def lcd_init(lines,dots_per_line,bits,direction,shift,cursor_type,cursor_on):
    time.sleep(0.015)
    push_ctrl(H,H,L,L,H,H,L,L) # interface auf 8 bit setzen
    time.sleep(0.200)
    push_ctrl(L,H,L,L,H,H,L,L) # interface auf 4 bit setzen
    time.sleep(0.100)
    push_ctrl(L,L,dots_per_line,lines,bits,H,L,L) # Function Set / Frundeinstellungen
    time.sleep(0.100)
    push_ctrl(shift,direction,H,L,L,L,L,L) # Entry Mode Set / Schreibmodus
    time.sleep(0.100)
    push_ctrl(cursor_type,cursor_on,H,H,L,L,L,L) # Display mode
    time.sleep(0.100)
    add_enter_symbol()
    clear()
    
def letter(char):    
    byte = ord(char)
    if char=='ä':
        byte=AE
    if char=='ö':
        byte=OE
    if char=='ü':
        byte=UE
    push_text(byte & 0x01 > 0,byte & 0x02 > 0,byte & 0x04 > 0,byte & 0x08 > 0,byte & 0x10 > 0,byte & 0x20 > 0,byte & 0x40 > 0,byte & 0x80 > 0)
    
def text(txt):
    for i in range(len(txt)):
        letter(txt[i])
        
def move0():
    push_ctrl(L,H,L,L,L,L,L,L)
    
def move(direction,shift,num):
    for i in range(num):
        push_ctrl(L,L,direction,shift,H,L,L,L)

def goto(line,column):
    if (line > 4) or (line < 1) or (column < 1) or (column > 16):
        return
    move0()
    if line == 2:
        move(L2R,L,40)
    if line == 3:
        move(L2R,L,16)
    if line == 4:
        move(L2R,L,56)
    if (column>1):
        move(L2R,L,column-1)
    
        
def line(num,txt):
    global line1,line2,line3,line4
    txt = txt.ljust(16," ")[:16]
    goto(num,1)
    text(txt)
    
if __name__ == '__main__':
    gpio_init();
    lcd_init(TWO_LINE,EIGHT_DOTS,FOUR_BIT_INTER,L2R,SHIFT,UNDERLINE,DISABLED)
    line(1,"If you can see")
    line(2,"this, your setup")
    line(3,"seems to be ok!")
    line(4,"      -- Stephan");