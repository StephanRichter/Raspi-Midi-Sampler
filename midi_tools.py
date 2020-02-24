#!/usr/bin/python3
import mido # sudo apt-get install python3-mido python3-rtmidi

MIDI_NAME = "VIEWCON.. MIDI 1"

midi = None

def check_midi():
    global midi
    msg = midi.poll()
    if msg is None:
        return None
    return msg

def flush():
    while midi.poll() is not None:
        pass

def midi_init():
    global midi
    midi = mido.open_input(MIDI_NAME)
    return midi
    
def read_note():
    global midi
    note = None
    while note == None:
        msg = midi.receive()
        if msg.type != 'note_on':
            continue
        if msg.velocity == 0:
            continue
        note = msg.note
        chan = msg.channel
    return (note, chan)

if __name__ == '__main__':
    midi_init()
    while True:
        print(read_note())
    

    