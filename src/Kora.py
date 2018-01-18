import adsk.core, adsk.fusion, adsk.cam, traceback
from array import array
import struct
import json
import requests
import math
from .packages import pyaudio
from .kora_modules import nlp
from .kora_modules import fusion_execute_intent
from .kora_modules import text_to_speech
from .kora_modules import user_interface

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox('Kora has started. Not listening right now.')
        witResponse = nlp.streamAudio(ui) #returns wit response json
        ui.messageBox('Executing: ' + str(witResponse))
        executionResultCode = fusion_execute_intent.executeCommand(witResponse, ui)
        ui.messageBox('Execution Result Code: ' + str(executionResultCode))
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
    finally:
        if ui:
            ui.messageBox('Kora has ended.')
