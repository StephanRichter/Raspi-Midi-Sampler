#!/usr/bin/python3
from display_4x16 import *
from midi_tools import *
import os
from shutil import copy

VERSION = "1.1"
profile = None
ARR = chr(127)
ENTER = chr(0)
 
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
    if name is None:
        clear()
        return
    name = name+'.prf'
    file = open(name,'a')
    file.close()
    clear()
    set_line(1,name)
    set_line(2,'erzeugt.')
    load_profile(name)
            
def delete_profile():
    global profile
    name = None
    if profile is None:
        name = select_profile()
    else:
        name = profile['name']
    if name is None: # es wurde kein Profil geladen
        return
    selection = select_from(name+"...",['...behalten','...behalten','löschen'])
    clear()
    set_line(1,name)
    if selection == 'löschen':
        os.remove(name)        
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
    selection = select_from('Programmiermodus',['Profil laden','Profil ändern','Neues Profil','Verwaltung','Abbrechen'])
    if selection == 'Profil laden':
        name = select_profile()
        if name is not None:
            load_profile(name)
        return
    if selection == 'Profil ändern':
        wav = select_wave()
        if wav is not None:
            assign(wav)
        return
    if selection == 'Neues Profil':
        create_profile()
        return
    if selection == 'Verwaltung':
        management()
        return
    clear()
    
def filter_waves(entries):
    result=[]
    for entry in entries:
        if os.path.isdir(entry) or (entry[-4:]=='.wav'):
            result.append(entry)
    result.sort()
    return result
    
def import_wave():
    profile_dir = os.getcwd()
    os.chdir('/media')
    selection = None;
    while True:
        entries = glob.glob('*')
        entries = filter_waves(entries)
        if os.getcwd() == '/media':
            entries.append('abbrechen')
        else:
            entries.append('..')

        selection = select_from('Quelle wählen:',entries)
        if selection == 'abbrechen':
            os.chdir(profile_dir)
            return
        if selection[-4:]=='.wav':
            break
        os.chdir(selection)
        print(os.getcwd())
    source_dir = os.getcwd()
    os.chdir(profile_dir)
    clear()
    set_line(1,selection)
    set_line(2,'wird kopiert...')
    copy(source_dir+'/'+selection,profile_dir)
    set_line(2,'importiert.')
    time.sleep(2)
    set_line(2,' ')
        
def load_profile(name):
    global profile
    if name is None:
        profile = None
        return
    profile = {'name':name,'notes':{}}    
    file = open(name,'r')
    for line in file:
        line=line.strip()
        if not line:
            continue
        data = line.split(" ",2)        
        wave = data.pop()
        note = int(data.pop())
        channel = int(data.pop())
        if channel in profile['notes']:
            profile['notes'][channel][note]=wave
        else:
            profile['notes'][channel]={note:wave}
    file.close()
    clear()
    set_line(2,'Profil geladen.')
    
def management():
    global profile
    selection = select_from('Verwaltung',['Profil löschen','Wave-Import','Stick auswerfen'])
    if selection == 'Profil löschen':
        delete_profile()
        return
    if selection == 'Wave-Import':
        import_wave()
        return
    if selection == 'Stick auswerfen':
        unmount()
    
def play_wav(filename):
    os.system('aplay '+filename)
    
def read_name(title):
    name = ""
    selection = select_from(title,['a-z','äöu / -_ / 0-9','abbrechen'])
    while True:
        third = 'abbrechen'
        if len(name)>0:
            third = 'Optionen'
        
        if selection == 'a-z':
            selection = select_from(title,['abcdefghijklm','nopqrstuvwxyz',third])
        if selection == 'äöu / -_ / 0-9':
            selection = select_from(title,['0123456789','äöü-_',third])
        if selection == 'Optionen':
            selection = select_from(title,['Zeichen löschen','übernehmen',third])
        if selection == 'abbrechen':
            return None
        if selection == 'übernehmen':
            return name
        if selection == 'Zeichen löschen':
            name = name[:-1]
            title = name
            if len(name)==0:
                third = 'abbrechen'
            selection = select_from(title,['a-z','äöu / -_ / 0-9',third])
            continue
        
        l = len(selection)
        if l>1:
            l=l//2
            selection = select_from(title,[selection[0:l],selection[l:],third])
            continue

        name = name+selection
        title = name
        if len(name)>0:
            third = 'Optionen'
        selection = select_from(title,['a-z','äöu / -_ / 0-9',third])
            
def ready():
    global profile
    if profile is not None:
        set_line(1,profile['name'])
    flush()
    set_line(4,"    Bereit.");

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
        time.sleep(1)
        return
    profiles.sort()
    return select_from('Profil wählen:',profiles)    
    
def select_wave():
    global profile
    clear()
    if profile is None:
        name = select_profile()
        load_profile(name)
    if profile is None:
        return None

    waves = glob.glob("*.wav")
    if (len(waves) == 0):
        set_line(1,"Keine Wave-Datei")
        set_line(2,"gefunden. Aktion")
        set_line(3,"abgebrochen...")
        time.sleep(3)
        return None
    
    waves.sort()
    return select_from('WAV-Datei wählen:',waves)
             
def unmount():
    list = open('/proc/mounts','r')
    devices=[] 
    for line in list:
        if 'usb' in line:
            parts = line.split()
            for part in parts:
                if 'media' in part:
                    devices.append(part)
    if not devices:
        clear()
        set_line(1,'Keine Sticks')
        set_line(2,'gefunden')
        time.sleep(1)
        return
    device = select_from('Stick wählen:',devices)
    if device is None:
        return

    os.system('sync')
    os.system('sudo umount '+device)

    mounted = False
    for line in list:
        if device in line:
            mounted = True

    if mounted:
        set_line(1,device)
        set_line(2,'konnte nicht')
        set_line(3,'ausgehängt')
        set_line(4,'werden!')
    else:
        set_line(1,device)
        set_line(2,'ausgehängt.')
        set_line(3,'Stick kann nun')
        set_line(4,'entfernt werden.')
    time.sleep(2)    
    clear()

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
    file.close()
    clear()
    set_line(1,name)
    set_line(2,'erzeugt.')
    
if __name__ == '__main__':
    print('Raspberry Midi Sampler starting.')
    os.chdir('profiles')
    gpio_init();    
    lcd_init(TWO_LINE,EIGHT_DOTS,FOUR_BIT_INTER,L2R,SHIFT,UNDERLINE,DISABLED)
    welcome()
    reset_usb('0a92')
    midi = midi_init()
    ready()
    while True:        
        if (GPIO.input(BUTTON) == H) or (profile is None):
#            lcd_init(TWO_LINE,EIGHT_DOTS,FOUR_BIT_INTER,L2R,SHIFT,UNDERLINE,DISABLED)
            enter_program()            
            ready()
        msg = midi.poll()
        if (msg is not None):
            if msg.type == 'note_on':
                channel = msg.channel
                note = msg.note
                if (profile is not None) and (channel in profile['notes']) and (note in profile['notes'][channel]):
                    play_wav(profile['notes'][channel][note])
                    flush()
