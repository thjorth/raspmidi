import rtmidi
import re
import time
import sys





#patches = [
#    [10,4],         #1     comp + slap
#    [10,4],         #2     comp + slap
#    [10,4],         #3     comp + slap
#    [10,4],         #4     comp + slap
#    [10,4],         #5     comp + slap
#    [10,4],         #6     comp + slap
#    [10,4],         #7     comp + slap
#    [10,4],         #8     comp + slap
#    [10,4],         #9     comp + slap
#    [10,5],         #10     comp + slap verb
#    [11,5],         #11     drive + slap verb
#    [12,5],         #12     heavy drive + slap verb    
#    [13,5],         #13     heavy drive, oct + slap verb
#    [14,5],         #14     heavy drive, oct, flanger + slap verb
#    [10,3],         #15     comp + particle verb
#    [11,4],         #16     drive + slap 
#    [15,4],         #17     drive, phaser + slap
#    [11,6],         #18     drive + mod delay 1/8
#    [11,2],         #19     drive + analog chorus
#    [10,24],        #20     comp + bypass     
#    [11,8],         #21     drive + mod delay
#    [12,8],         #22     heavy drive + mod delay
#    [16,5],         #23     ziggimund + slap verb
#    [11,9],         #24     drive + tremolo
#    [6,3],          #25
#    [6,3],          #27
#    [6,3],          #28
#    [6,3],          #29
#    [6,3],          #30
#    [6,3],          #31
#    [6,3],          #32
#    [6,3],          #33
#    [6,3]           #34
#]

patches = [
    [10,5],         #1    comp + slap verb
    [11,5],         #2     drive + slap verb
    [12,5],         #3     heavy drive + slap verb    
    [13,5],         #4     heavy drive, oct + slap verb
    [14,5],         #5     heavy drive, oct, flanger + slap verb
    [10,3],         #6     comp + particle verb
    [11,4],         #7     drive + slap 
    [15,4],         #8     drive, phaser + slap
    [11,6],         #9     drive + mod delay 1/8
    [11,2],         #10     drive + analog chorus
    [10,24],        #11     comp + bypass     
    [11,8],         #12     drive + mod delay
    [12,8],         #13     heavy drive + mod delay
    [16,5],         #14     ziggimund + slap verb
    [11,9],         #15     drive + tremolo
    [6,3],          #16
    [6,3],          #17
    [6,3],          #28
    [6,3],          #29
    [6,3],          #30
    [6,3],          #31
    [6,3],          #32
    [6,3],          #33
    [6,3]           #34
]


#zoomout = rtmidi.MidiOut()
zoom_drive_out = rtmidi.MidiOut()
zoom_time_out = rtmidi.MidiOut()
#m5out = rtmidi.MidiOut()
available_out_ports = zoom_drive_out.get_ports()

midiin = rtmidi.MidiIn()
available_in_ports = midiin.get_ports()
print(available_out_ports)
print(available_in_ports)

#zoom_index = None
zoom_drive_index = None
zoom_time_index = None
uno_index = None

#zoom_re = re.compile('zoom ms series.*24', re.IGNORECASE)
zoom_drive_re = re.compile('zoom ms series.*24', re.IGNORECASE)
zoom_time_re = re.compile('zoom ms series.*28', re.IGNORECASE)
uno_re = re.compile('usb uno midi', re.IGNORECASE)

while zoom_drive_index == None or zoom_time_index == None or uno_re == None:
    time.sleep(1)
    if zoom_drive_index == None:
        available_out_ports = zoom_drive_out.get_ports()
        i = 0
        for port in available_out_ports:
            print(port)
            if zoom_drive_re.search(port) != None:
                zoom_drive_index = i
            i += 1

    if zoom_time_index == None:
        available_out_ports = zoom_time_out.get_ports()
        i = 0
        for port in available_out_ports:
            print(port)
            if zoom_time_re.search(port) != None:
                zoom_time_index = i
            i += 1
        
    if uno_index == None:
        available_in_ports = midiin.get_ports()
        i = 0
        for port in available_in_ports:
            if uno_re.search(port):
                uno_index = i
            i = i+1

print("zoom_drive_index {}".format(zoom_drive_index))
print("zoom_time_index {}".format(zoom_time_index))
print("uno_index {}".format(uno_index))

zoom_drive_out.open_port(zoom_drive_index)
zoom_time_out.open_port(zoom_time_index)
#m5out.open_port(uno_index)
midiin.open_port(uno_index)

patch_change = [192, 1]
#zoomout.send_message(patch_change)

class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self.cur_zoom_pc = -1
        self.cur_zoom_drive_pc = -1
        self.cur_zoom_time_pc = -1
        self.cur_m5_pc = -1

    def __call__(self, event, data=None):
        message, dtime = event
        if message[0] == 192:
            pc = message[1];
            print("pc: {}".format(pc))
            try:
                cmd = patches[pc]
                print("cmd: {}".format(cmd))
                zoom_drive_pc = cmd[0] - 1
                if zoom_drive_pc < 0:
                    zoom_drive_pc = 50
                zoom_time_pc = cmd[1] - 1
                if zoom_time_pc < 0:
                    zoom_time_pc = 24;

                print("Zoom drive: {}, Zoom time: {}".format(zoom_drive_pc, zoom_time_pc))
                if self.cur_zoom_drive_pc != zoom_drive_pc:
                    zoom_drive_out.send_message([192, zoom_drive_pc])
                    self.cur_zoom_drive_pc = zoom_drive_pc

                if self.zoom_time_pc != zoom_time_pc:
                    zoom_time_out.send_message([192, zoom_time_pc])
                    self.cur_zoom_time_pc = zoom_time_pc

            except:
                print ("Unexpected error:", sys.exc_info())
                #zoomout.send_message(message)
                #m5out.send_message(message)

midiin.set_callback(MidiInputHandler(available_in_ports[uno_index]))

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('')
finally:
    print('Exiting')
    zoom_drive_out.close_port()
    zoom_time_out.close_port()
    #zoomout.close_port()
    #m5out.close_port()
    midiin.close_port()
    

    del(zoomout)
    del(m5out)
    del(midiin)


