import adsk.core, adsk.fusion, adsk.cam, traceback
from array import array
import struct
import json
import requests
import math
from .packages import pyaudio

THRESHOLD = .05
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 8000
SHORT_NORMALIZE = (1.0/32768.0)
WIT_AI_CLIENT_ACCESS_TOKEN = 'Q6QP5OFCOQRS65KEIQZO3OPD47XFLGUE'

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox('Hello World')

        ui.messageBox(str(streamAudio(ui)))

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def streamAudio(ui):
    pAudio = pyaudio.PyAudio()
    stream = pAudio.open(format=FORMAT, channels=1, rate=RATE,
                    input=True, output=True,
                    frames_per_buffer=CHUNK_SIZE)

    headers = {'Authorization': 'Bearer ' + WIT_AI_CLIENT_ACCESS_TOKEN,
               'Content-Type': 'audio/raw; encoding=signed-integer; bits=16;' +
                               ' rate=8000; endian=little', 'Transfer-Encoding': 'chunked'}
    url = 'https://api.wit.ai/speech'

    postResponse = requests.post(url, headers=headers, data=gen(stream, ui))
    stream.stop_stream()
    stream.close()
    pAudio.terminate()
    return postResponse.text

    """response = postResponse.json()

    for entity in response[u'entities']:
        if entity == 'intent':
            print entity + str(": ") + str(response['entities'][entity][0]['value'])
        elif entity == 'rotation_quantity':
            print 'direction: ' + str(response['entities'][entity][0]['entities']['direction'][0]['value'])
            print 'magnitude: ' + str(response['entities'][entity][0]['entities']['number'][0]['value'])
            print 'units: ' + str(response['entities'][entity][0]['entities']['units'][0]['value'])
    """

# Returns if the RMS of block is less than the threshold
def is_silent(block):
    count = len(block)/2
    form = "%dh" % (count)
    shorts = struct.unpack(form, block)
    sum_squares = 0.0

    for sample in shorts:
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    rms_value = math.sqrt(sum_squares / count)
    return rms_value, rms_value <= THRESHOLD


# Returns as many (up to returnNum) blocks as it can.
def returnUpTo(iterator, values, returnNum):
    if iterator+returnNum < len(values):
        return (iterator + returnNum,
                "".join(values[iterator:iterator + returnNum]))

    else:
        temp = len(values) - iterator
        return (iterator + temp + 1, "".join(values[iterator:iterator + temp]))


# Python generator- yields roughly 512k to generator.
def gen(stream, ui):
    num_silent = 0
    snd_started = False
    counter = 0
    #print "Microphone on!"
    ui.messageBox("Microphone on!")
    i = 0
    data = []

    while 1:
        rms_data = stream.read(CHUNK_SIZE)
        snd_data = array('i', rms_data)
        for d in snd_data:
            data.append(struct.pack('<i', d))

        rms, silent = is_silent(rms_data)

        if silent and snd_started:
            num_silent += 1

        elif not silent and not snd_started:
            i = len(data) - CHUNK_SIZE*2  # Set the counter back a few seconds
            if i < 0:                     # so we can hear the start of speech.
                i = 0
            snd_started = True
            #print "TRIGGER at " + str(rms) + " rms."

        elif not silent and snd_started and not i >= len(data):
            i, temp = returnUpTo(i, data, 1024)
            yield temp
            num_silent = 0

        if snd_started and num_silent > 10:
            #print "Stop Trigger"
            ui.messageBox("Stop Trigger")
            break

        if counter > 75:  # Slightly less than 10 seconds.
            ui.messageBox("Timeout, Stop Trigger")
            #print "Timeout, Stop Trigger"
            break

        if snd_started:
            counter = counter + 1

    # Yield the rest of the data.
    #print "Pre-streamed " + str(i) + " of " + str(len(data)) + "."
    while (i < len(data)):
        i, temp = returnUpTo(i, data, 512)
        yield temp
    #print "Swapping to thinking."
