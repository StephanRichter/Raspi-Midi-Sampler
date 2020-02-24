#!/usr/bin/python3
from display_4x16 import *
from midi_tools import *

VERSION = "0.4"

def welcome():
    clear()
    line(2,"   Willkommen!");
    time.sleep(2)
    line(1,"   Wilkommen!");
    line(2,"");
    line(3," Raspberry Midi")
    line(4," Sampler v. "+VERSION)
    time.sleep(2)
    clear()
    line(1,"Knopf drücken um")
    line(2,"zu Programmieren")
    
def ready():
    flush()
    line(4,"    Bereit.");
    
def create_profile():
    clear()
    line(1,"Name für Profil:")
    line(2,"[leer]");
    line(3,"1. Note blättert")
    line(4,"2. Note wählt")
    scroll = read_note()
    name = ""
    c = 97 # start with a
    line(2,chr(c));
    note = read_note()
    while c != 0:
        while note == scroll:
            c = c+1;
            if c == 123: # go from z to Enter
                c = 0
            if c == 1: # go from Enter to number
                c = 48
            if c == 58: # go from nubers to underscore
                c = 95
            if c == 96: # go from underscore to dash
                c = 45
            if c == 46: # go from dash to ä
                c = AE
            if (c-1) == AE:
                c = OE
            if (c-1) == OE:
                c = UE
            if (c-1) == UE: # go from ä to dash
                c = 97
            goto(2,len(name)+1)
            letter(chr(c))
            note = read_note()
        if (c == 0):
            write_profile(name)
        else:
            name = name + chr(c)
            print(name)
            c = 97 # start with a
            line(2,name+chr(c));
            note = read_note()   
    
def enter_program():
    clear()
    line(1,"Programmiermodus")
    line(2,"1. Note blättert")
    line(3,"2. Note wählt")
    line(4,"Start mit Note.")
    scroll = read_note()
    line(1,"  Profil laden")
    line(2,"  Neues Profil")
    line(3,"  Profil ändern")
    line(4,"  abbrechen")
    
    selection = 1
    goto(selection,1)
    letter('~')
    note = read_note()
    while note == scroll:
        goto(selection,1)
        letter(' ')
        selection = selection+1
        if selection>4:
            selection=1
        goto(selection,1)
        letter('~')
        note = read_note()
    
    if selection == 2:
        create_profile()
    
def write_profile(name):
    clear()
    line(1,name)
    
if __name__ == '__main__':    
    gpio_init();    
    lcd_init(TWO_LINE,EIGHT_DOTS,FOUR_BIT_INTER,L2R,SHIFT,UNDERLINE,DISABLED)
    welcome()
    midi = midi_init()
    ready()
    while True:        
        if GPIO.input(BUTTON) == H:
            enter_program()            
            ready()
        msg = midi.poll()
        if (msg is not None):
            if msg.type == 'note_on':
                print(msg.note)
