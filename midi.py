import rtmidi
import re
import time
import sys


patches = [
    [1,1],
    [2,1],
    [3,1],
    [4,2],
    [5,2],
    [6,3]
]

zoomout = rtmidi.MidiOut()
m5out = rtmidi.MidiOut()
available_out_ports = zoomout.get_ports()

midiin = rtmidi.MidiIn()
available_in_ports = midiin.get_ports()
print(available_out_ports)
print(available_in_ports)

zoom_index = None
uno_index = None

zoom_re = re.compile('zoom ms series', re.IGNORECASE)
uno_re = re.compile('usb uno midi', re.IGNORECASE)

while zoom_index == None or uno_re == None:
    time.sleep(1)
    if zoom_index == None:
        available_out_ports = zoomout.get_ports()
        i = 0
        for port in available_out_ports:
            if zoom_re.search(port) != None:
                zoom_index = i
                i += 1
                
    if uno_index == None:
        available_in_ports = midiin.get_ports()
        i = 0
        for port in available_in_ports:
            if uno_re.search(port):
                uno_index = i
                i = i+1

zoom_index = 2
uno_index = 1

cur_zoom_pc = -1
cur_m5_pc = -1

print("Checking GIT workflow")
print("Opening for input {}".format(available_in_ports[uno_index]))
print("Opening for output {}".format(available_out_ports[zoom_index]))
zoomout.open_port(zoom_index)
m5out.open_port(uno_index)
midiin.open_port(uno_index)

patch_change = [192, 1]
zoomout.send_message(patch_change)

class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self.cur_zoom_pc = -1
        self.cur_m5_pc = -1

    def __call__(self, event, data=None):
        message, dtime = event
        pc = message[1];
        print("pc: {}".format(pc))
        try:
            cmd = patches[pc]
            print("cmd: {}".format(cmd))
            zoom_pc = cmd[0] - 1
            if zoom_pc < 0:
                zoom_pc = 50
            m5_pc = cmd[1] - 1
            if m5_pc < 0:
                m5_pc = 24;
            
            print("Zoom: {}, M5: {}".format(zoom_pc, m5_pc))
            if self.cur_zoom_pc != zoom_pc:
                zoomout.send_message([192, zoom_pc])
                self.cur_zoom_pc = zoom_pc
                
            if self.cur_m5_pc != m5_pc:
                m5out.send_message([192, m5_pc])
                self.cur_m5_pc = m5_pc
            
        except:
            print ("Unexpected error:", sys.exc_info())
            zoomout.send_message(message)
            m5out.send_message(message)

midiin.set_callback(MidiInputHandler(available_in_ports[uno_index]))

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('')
finally:
    print('Exiting')
    zoomout.close_port()
    m5out.close_port()
    midiin.close_port()
    

    del(zoomout)
    del(m5out)
    del(midiin)


