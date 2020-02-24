#!/usr/bin/python
import time
import RPi.GPIO as GPIO

VERSION = "0.1"

# Zuordnung der GPIO Pins (ggf. anpassen)
LCD_RS = 14
LCD_E  = 15
LCD_DATA4 = 18
LCD_DATA5 = 23
LCD_DATA6 = 24
LCD_DATA7 = 25

PAUSE = 0.0005

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

line1 = ""
line2 = ""
line3 = ""
line4 = ""

def push4(rs,d4,d5,d6,d7):
    GPIO.output(LCD_RS,rs);
    time.sleep(PAUSE)
    GPIO.output(LCD_E,H)
    time.sleep(PAUSE)
    GPIO.output(LCD_DATA4,d4)
    GPIO.output(LCD_DATA5,d5)
    GPIO.output(LCD_DATA6,d6)
    GPIO.output(LCD_DATA7,d7)
    time.sleep(PAUSE)
    GPIO.output(LCD_E,L)

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

def clear():
    push_ctrl(H,L,L,L,L,L,L,L)
    
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
    clear()
    
def letter(char):    
    byte = ord(char)
    if char=='ä':
        byte=225
    if char=='ö':
        byte=239
    if char=='ü':
        byte=245
    push_text(byte & 0x01 > 0,byte & 0x02 > 0,byte & 0x04 > 0,byte & 0x08 > 0,byte & 0x10 > 0,byte & 0x20 > 0,byte & 0x40 > 0,byte & 0x80 > 0)
    
def text(txt):
    for i in range(len(txt)):
        letter(txt[i])
        
def move0():
    push_ctrl(L,H,L,L,L,L,L,L)
    
def move(direction,shift,num):
    for i in range(num):
        push_ctrl(L,L,direction,shift,H,L,L,L)
        
def line(num,txt):
    global line1,line2,line3,line4
    txt = txt.ljust(16," ")[:16]
    print("<"+txt+">");
    move0()
    if (num < 1) or (num > 4):
        return
    if num == 2:
        move(L2R,L,40)
    if num == 3:
        move(L2R,L,16)
    if num == 4:
        move(L2R,L,56)
    text(txt)
    
def welcome():
    line(2,"   Willkommen!");
    time.sleep(2)
    line(1,"   Wilkommen!");
    line(2,"");
    line(3,"Raspberry Midi")
    line(4,"Sampler v. "+VERSION)
    time.sleep(2)
    clear()
    line(1,"Knopf drücken um")
    line(2,"zu Programmieren")
    
if __name__ == '__main__':
    gpio_init();
    lcd_init(TWO_LINE,EIGHT_DOTS,FOUR_BIT_INTER,L2R,SHIFT,UNDERLINE,DISABLED)
    welcome()
    
    