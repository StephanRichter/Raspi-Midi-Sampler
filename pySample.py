#!/usr/bin/python3
from display_4x16 import *
from midi_tools import *
import os,_thread

VERSION = "0.11"
profile = None
ARR = chr(127)
ENTER = chr(0)
 
def ready():
    global profile
    if profile is not None:
        set_line(1,profile['name'])
    flush()
    set_line(4,"    Bereit.");
    
def assign(wave):
    global profile
    clear()    
    set_line(1,"Note spielen, um")
    set_line(2,wave)
    set_line(3,"zuzuweisen")
    flush()
    note,channel = read_note()
    clear()
    set_line(1,profile['name'])
    set_line(2,wave)
    set_line(3,"zugewiesen zu:")
    set_line(4,"Note "+str(note)+" / Ch "+str(channel))
    if channel in profile['notes']:
        profile['notes'][channel][note]=wave            
    else:
        profile['notes'][channel]={note:wave}
    save_profile()
    time.sleep(2)
    clear()
    set_line(1,profile['name'])
 
def create_profile():
    name = read_name("Name für Profil:")
    if name is not None:
        write_profile(name+".prf")
        load_profile(name+".prf")
            
def delete_profile():
    global profile
    if profile is None:
        name = select_profile()
        load_profile(name)
    if profile is None: # es wurde kein Profil geladen
        return
    selection = select_from(profile['name']+"...",['...behalten','...behalten','löschen'])
    clear()
    set_line(1,profile['name'])
    if selection == 'löschen':
        os.remove(profile['name'])        
        set_line(2,'gelöscht!')
        profile = None
    else:
        set_line(2,'nicht gelöscht.')        
    
def enter_program():
    clear()
    set_line(1,"Programmiermodus")
    set_line(2,"1. Note blättert")
    set_line(3,"2. Note wählt")
    set_line(4,"Start mit Note.")
    scroll,channel = read_note()
    selection = select_from('Programmiermodus',['Profil laden','Neues Profil','Profil ändern','Profil löschen','Wave importieren','Abbrechen'])
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
    if selection == 'Wave importieren':
        import_wave()
def load_profile(name):
    global profile
    if name is None:
        profile = None
        return
    profile = {'name':name,'notes':{}}
    
    file = open(name,'r')
    for line in file:
        data = line.split(" ",2)        
        wave = data.pop().strip()
        note = int(data.pop())
        channel = int(data.pop())
        if channel in profile['notes']:
            profile['notes'][channel][note]=wave
        else:
            profile['notes'][channel]={note:wave}
    file.close()
    clear()
    set_line(2,'Profil geladen.')
    
def playing(filename):
    set_line(2,filename)
    set_line(3,'wird gespielt')
    set_line(4,' ')
    
def play_wav(filename):
    _thread.start_new_thread(playing,(filename,))
    os.system('aplay '+filename)
    clear()
    
def read_name(title):    
    selection = select_from(title,['abcdefghijklmn','opqrstuvwxyzäö','ü-_0123456789'])
    name = ""
    while True:
        l = len(selection)
        if l>1:
            l=l//2
            if len(name)>0:                
                selection = select_from(title,[selection[0:l],selection[l:],ARR+'/'+ENTER])
            else:
                selection = select_from(title,[selection[0:l],selection[l:]])
                
            if selection == ARR+'/'+ENTER:
                selection = select_from(title,['übernehmen','rückgängig'])
            if selection == 'übernehmen':
                return name
            if selection == 'rückgängig':
                name = name[:-1]
                title = name
                selection = select_from(title,['abcdefghijklmn','opqrstuvwxyzäö','ü-_0123456789'])
        else:
            name = name+selection
            title = name
            selection = select_from(title,['abcdefghijklmn','opqrstuvwxyzäö','ü-_0123456789'])
            
def save_profile():
    global profile    
    if profile is None:
        return
    file = open(profile['name'],'w')
    if 'notes' in profile:
        samples = profile['notes']
        for channel,notes in samples.items():
            for note,wave in notes.items():
                file.write(str(channel)+' '+str(note)+' '+wave+"\n")
    file.close()

def select_from(title,names):
    count = len(names)
    selection = 1
    offset = 0
    clear()
    set_line(1,title)
    for i in range(3):
        if (i+offset<count):
            set_line(i+2," "+names[i+offset])
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
                    set_line(i+2," "+names[i+offset])
        if selection > offset+3:
            offset = offset+1
            for i in range(3):
                if (i+offset<count):
                    set_line(i+2," "+names[i+offset])
        goto(selection-offset+1,1)
        letter('~')
        note,channel = read_note()
    return names[selection-1]
        
def select_profile():
    profiles = glob.glob("*.prf")
    if (len(profiles) == 0):
        clear()
        set_line(1,'Keine Profile')
        set_line(2,'gefunden!')
        return
    profiles.sort()
    return select_from('Profil wählen:',profiles)    
    
def select_wave():
    global profile
    clear()
    if profile is None:
        name = select_profile()
        load_profile(name)

    waves = glob.glob("*.wav")
    if (len(waves) == 0):
        set_line(1,"Keine Wave-Datei")
        set_line(2,"gefunden. Aktion")
        set_line(3,"abgebrochen...")
        time.sleep(3)
        return None
    
    waves.sort()
    return select_from('WAV-Datei wählen:',waves)

def welcome():
    clear()
    set_line(1,"   Willkommen!");
    set_line(2,"");
    set_line(3," Raspberry Midi")
    set_line(4,"Sampler v. "+VERSION)
    time.sleep(2)
    set_line(3,' ')
    set_line(4,"Initialisiere...")
    
def write_profile(name):
    file = open(name,'a')
    file.write('test')
    file.close()
    clear()
    set_line(1,name)
    set_line(2,'erzeugt.')
    
if __name__ == '__main__':
    os.chdir('profiles')
    gpio_init();    
    lcd_init(TWO_LINE,EIGHT_DOTS,FOUR_BIT_INTER,L2R,SHIFT,UNDERLINE,DISABLED)
    welcome()
    reset_usb('0a92')
    midi = midi_init()
    ready()
    while True:        
        if (GPIO.input(BUTTON) == H) or (profile is None):
            enter_program()            
            ready()
        msg = midi.poll()
        if (msg is not None):
            if msg.type == 'note_on':
                channel = msg.channel
                note = msg.note
                print("Note "+str(channel)+'/'+str(note)+" gespielt")
                if (profile is not None) and (channel in profile['notes']) and (note in profile['notes'][channel]):
                    play_wav(profile['notes'][channel][note])
                    clear()
                    ready()