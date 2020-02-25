#!/usr/bin/python3
from display_4x16 import *
from midi_tools import *
import os

VERSION = "0.8"
profile = None

 
def ready():
    global profile
    if profile is not None:
        line(1,"Profil geladen:")
        line(2,profile)
    line(4,"    Bereit.");
    
def assign(wave):
    global profile
    clear()    
    line(1,"Note spielen, um")
    line(2,wave)
    line(3,"zuzuweisen")
    flush()
    note,channel = read_note()
    clear()
    line(1,profile)
    line(2,wave)
    line(3,"zugewiesen zu:")
    line(4,"Note "+str(note)+" / Ch "+str(channel))
    time.sleep(3)   
 
def create_profile():
    read_name("Name für Profil:")
    clear()
    line(1,"Name für Profil:")
    line(2,"[leer]");
    line(3,"1. Note blättert")
    line(4,"2. Note wählt")
    scroll,channel = read_note()
    name = ""
    c = 97 # start with a
    line(2,chr(c));
    note,channel = read_note()
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
            note,channel = read_note()
        if (c == 0):
            write_profile(name+".prf")
            load_profile(name+".prf")
        else:
            name = name + chr(c)
            c = 97 # start with a
            line(2,name+chr(c));
            note,channel = read_note()
            
def delete_profile():
    global profile
    if profile is None:
        name = select_profile()
        load_profile(name)
    if profile is None: # es wurde kein Profil geladen
        return
    selection = select_from(profile+"...",['...behalten','...behalten','löschen'])
    if selection == 'löschen':
        os.remove(profile)
        profile = None
    
def enter_program():
    clear()
    line(1,"Programmiermodus")
    line(2,"1. Note blättert")
    line(3,"2. Note wählt")
    line(4,"Start mit Note.")
    scroll,channel = read_note()
    selection = select_from('Programmiermodus',['Profil laden','Neues Profil','Profil ändern','Profil löschen','Abbrechen'])
    if selection == 'Profil laden':
        name = select_profile()
        if name is not None:
            load_profile(name)
    if selection == 'Profil löschen':
        delete_profile()
    if selection == 'Neues Profil':
        create_profile()
    if selection == 'Profil ändern':
        wav = select_wave()
        if wav is not None:
            assign(wav)
    clear()
        
def load_profile(name):
    global profile
    if name is None:
        profile = None
        return
    profile = name

def select_from(title,names):
    count = len(names)
    selection = 1
    offset = 0
    clear()
    line(1,title)
    for i in range(3):
        if (i+offset<count):
            line(i+2," "+names[i+offset])
    scroll,channel = read_note()
    goto(selection+1,1)
    letter('~')
    note,channel = read_note()
    while note == scroll:
        goto(selection+1,1)
        letter(' ')
        selection = selection +1
        if selection > count:
            selection = 1
            offset = 0
            for i in range(3):
                if (i+offset<count):
                    line(i+2," "+names[i+offset])
        if selection > offset+3:
            offset = offset+1
            for i in range(3):
                if (i+offset<count):
                    line(i+2," "+names[i+offset])
        goto(selection-offset+1,1)
        letter('~')
        note,channel = read_note()
    return names[selection-1]
        
def select_profile():
    profiles = glob.glob("*.prf")
    if (len(profiles) == 0):
        return
    profiles.sort()
    return select_from('Profil wählen:',profiles)
    
    
def select_wave():
    global profile
    clear()
    if profile is None:
        select_profile()

    waves = glob.glob("*.wav")
    if (len(waves) == 0):
        line(1,"Keine Wave-Datei")
        line(2,"gefunden. Aktion")
        line(3,"abgebrochen...")
        time.sleep(3)
        return None
    
    waves.sort()
    return select_from('WAV-Datei wählen:',waves)

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
    line(4,"Initialisiere...")
    
def write_profile(name):
    file = open(name,'a')
    file.write('test')
    file.close()
    clear()
    line(1,name)
    line(2,'erzeugt.')
    

    
if __name__ == '__main__':
    os.chdir('profiles')
    gpio_init();    
    lcd_init(TWO_LINE,EIGHT_DOTS,FOUR_BIT_INTER,L2R,SHIFT,UNDERLINE,DISABLED)
    welcome()
    reset_usb('0a92')
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
