import rtmidi
import re
import time

midiout = rtmidi.MidiOut()
available_out_ports = midiout.get_ports()

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
        available_out_ports = midiout.get_ports()
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

print("Opening for input {}".format(available_in_ports[uno_index]))
print("Opening for output {}".format(available_out_ports[zoom_index]))
midiout.open_port(zoom_index)
midiin.open_port(uno_index)



patch_change = [192, 1]
midiout.send_message(patch_change)

class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port

    def __call__(self, event, data=None):
        message, dtime = event
        midiout.send_message(message)
        print("{}".format(message))

midiin.set_callback(MidiInputHandler(available_in_ports[uno_index]))

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('')
finally:
    print('Exiting')
    midiout.close_port()
    midiin.close_port()

    del(midiout)
    del(midiin)


