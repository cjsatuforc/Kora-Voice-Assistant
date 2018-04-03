from array import array
import struct
import sys
import json
import requests
import math
import time

from ...packages import pyaudio
from ... import config
from ...Services.extractionService import _getFromCommand

THRESHOLD = .05
CHUNK_SIZE = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
SHORT_NORMALIZE = (1.0 / 32768.0)
WIT_AI_CLIENT_ACCESS_TOKEN = config.WIT_AI_CLIENT_ACCESS_TOKEN

userStoppedTalkingTime = None
stopped = False


def streamAudio(fireMessage, onSpeechDetectedCallback=None, onSpeechEndCallback=None):
    """
    :param onSpeechDetectedCallback:
    :param onSpeechEndCallback:
    :return:
    """
    try:
        # Returns True to keep listening if there is no intent key or if
        # there is and the confidence is below threshold
        def shouldKeepListening(resp):
            confidence = _getFromCommand(resp, ['entities', 'intent', 'confidence'])
            if (confidence == None or confidence <= config.thresholdConfidence):
                return True
            return False

        pAudio = pyaudio.PyAudio()
        stream = pAudio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                             input=True, frames_per_buffer=CHUNK_SIZE)
        headers = {'Authorization': 'Bearer ' + WIT_AI_CLIENT_ACCESS_TOKEN,
                   'Content-Type': 'audio/raw; encoding=signed-integer; bits=16;' +
                                   ' rate=8000; endian=little', 'Transfer-Encoding': 'chunked'}
        url = 'https://api.wit.ai/speech'

        postResponse = None
        keepListening = True
        while(keepListening):
            postResponse = requests.post(url, headers=headers, data=_gen(fireMessage, stream, onSpeechDetectedCallback, onSpeechEndCallback))
            try:
                returnResponse = postResponse.json()
                keepListening = shouldKeepListening(returnResponse)
            except:
                continue

        endTime = time.time()
        stream.stop_stream()
        stream.close()
        pAudio.terminate()
        returnResponse = postResponse.json()
        returnResponse['witDelay'] = endTime - userStoppedTalkingTime

        """#capture the elapsed time for wit
        witStreamTime = postResponse.elapsed.total_seconds()
        returnResponse = postResponse.json()
        returnResponse['witStreamTime'] = witStreamTime"""

        global stopped
        stopped = False
        return returnResponse
    except:
        global stopped
        stopped = False
        return {'streamingError': True}

##########################################################################
##########################################################################
##########################################################################
##########################################################################

def stop():
    global stopped
    stopped = True


# Returns if the RMS of block is less than the threshold
def _is_silent(block):
    """
    :param block:
    :return:
    """
    count = len(block) / 2
    form = "%dh" % (count)
    shorts = struct.unpack(form, block)
    sum_squares = 0.0

    for sample in shorts:
        n = sample * SHORT_NORMALIZE
        sum_squares += n * n

    rms_value = math.sqrt(sum_squares / count)
    return rms_value, rms_value <= THRESHOLD


# Returns as many (up to returnNum) blocks as it can.
def _returnUpTo(iterator, values, returnNum):
    """
    :param iterator:
    :param values:
    :param returnNum:
    :return:
    """
    if iterator + returnNum < len(values):
        return (iterator + returnNum,
                b"".join(values[iterator:iterator + returnNum]))

    else:
        temp = len(values) - iterator
        return (iterator + temp + 1, b"".join(values[iterator:iterator + temp]))


# Python generator- yields roughly 512k to generator.
def _gen(fireMessage, stream, onSpeechDetectedCallback, onSpeechEndCallback):
    """
    :param stream:
    :return:
    """
    fireMessage("Inside _gen.")
    num_silent = 0
    snd_started = False
    counter = 0
    i = 0
    data = []

    while not stopped:
        rms_data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        snd_data = array('i', rms_data)
        for d in snd_data:
            data.append(struct.pack('<i', d))
        rms, silent = _is_silent(rms_data)
        if silent and snd_started:
            num_silent += 1

        elif not silent and not snd_started:
            if onSpeechDetectedCallback:
                onSpeechDetectedCallback()
            i = len(data) - CHUNK_SIZE * 2  # Set the counter back a few seconds
            if i < 0:  # so we can hear the start of speech.
                i = 0
            snd_started = True

        elif not silent and snd_started and not i >= len(data):
            i, temp = _returnUpTo(i, data, 1024)
            yield temp
            num_silent = 0

        if snd_started and num_silent > 10:
            global userStoppedTalkingTime
            userStoppedTalkingTime = time.time()
            break

        if counter > 75:  # Slightly less than 10 seconds.
            break

        if snd_started:
            counter = counter + 1

    if not stopped:
        if onSpeechEndCallback:
            onSpeechEndCallback()

        # Yield the rest of the data.
        # print "Pre-streamed " + str(i) + " of " + str(len(data)) + "."
        while (i < len(data)):
            i, temp = _returnUpTo(i, data, 512)
            yield temp
