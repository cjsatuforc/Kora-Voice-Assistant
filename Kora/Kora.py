import adsk.core, adsk.fusion, adsk.cam, traceback
import threading
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

_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_activateCmdDef = adsk.core.CommandDefinition.cast(None)
_deactivateCmdDef = adsk.core.CommandDefinition.cast(None)
_koraThread = None
handlers = []   #keeps handlers in scope
customEventIDWitResponse = 'WitResponseEvent'
customEventIDPopupMessage = 'PopupMessageEvent'


def run(context):
    global _app, _ui, _activateCmdDef, _deactivateCmdDef
    try:
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        addInsPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')

        # Create a new command and add it to the ADD-INS panel in the model workspace.
        _activateCmdDef = _ui.commandDefinitions.addButtonDefinition('ActivateKoraCmd', 'Activate Kora', 'Activate Kora voice control for Fusion.')
        activateButtonControl = addInsPanel.controls.addCommand(_activateCmdDef)

        # Connect the command created handler to the event.
        onKoraActivated = KoraActivatedHandler()
        _activateCmdDef.commandCreated.add(onKoraActivated)
        handlers.append(onKoraActivated)

        #Repeat above steps to the command to deactivate Kora
        _deactivateCmdDef = _ui.commandDefinitions.addButtonDefinition('DeactivateKoraCmd', 'Deactivate Kora','Deactivate Kora voice control for Fusion.')
        deactivateButtonControl = addInsPanel.controls.addCommand(_deactivateCmdDef)
        deactivateButtonControl.isVisible = False

        onKoraDeactivated = KoraDeactivatedHandler()
        _deactivateCmdDef.commandCreated.add(onKoraDeactivated)
        handlers.append(onKoraDeactivated)

        # Register the custom event and connect the handler.
        customEventWitResponse = _app.registerCustomEvent(customEventIDWitResponse)
        onWitResponse = WitResponseHandler()
        customEventWitResponse.add(onWitResponse)
        handlers.append(onWitResponse)

        customEventPopupMessage = _app.registerCustomEvent(customEventIDPopupMessage)
        onPopupMessage = PopupMessageHandler()
        customEventPopupMessage.add(onPopupMessage)
        handlers.append(onPopupMessage)

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context): #anything that should occur when Kora stops (e.g. when editor is closed)
    try:
        _ui.messageBox('Kora add-in has been stopped.')
        # Clean up the command.
        addInsPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        activateControl = addInsPanel.controls.itemById('ActivateKoraCmd')
        deactivateControl = addInsPanel.controls.itemById('DeactivateKoraCmd')

        if activateControl:
            activateControl.deleteMe()
        if _activateCmdDef:
            _activateCmdDef.deleteMe()
        if deactivateControl:
            deactivateControl.deleteMe()
        if _deactivateCmdDef:
            _deactivateCmdDef.deleteMe()
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class KoraThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.stopped = False

    def run(self):
        _app.fireCustomEvent(customEventIDPopupMessage, json.dumps({'type': 'info', 'title': 'Kora', 'message': 'Kora\'s Thread is Running'}))
        try:
            while not self.stopped:
                witResponse = nlp.streamAudio() #returns wit response json
                if not self.stopped:    #in case deactivation occurs while streamAudio is running
                    _app.fireCustomEvent(customEventIDWitResponse, json.dumps(witResponse))
        except:
            _app.fireCustomEvent(customEventIDPopupMessage, json.dumps({'type': 'error', 'title': 'Kora Failed', 'message': 'Failed:\n{}'.format(traceback.format_exc())}))
        
    def stop(self):
        self.stopped = True

# ############################
# #        Handlers          #
# ############################

class KoraActivatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
        self.alreadyNotified = False

    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            inputs = eventArgs.command.commandInputs
            if not self.alreadyNotified:
                # Connect a handler to the command destroyed event.
                onKoraDestroyed = KoraDestroyedHandler()
                inputs.command.destroy.add(onKoraDestroyed)
                handlers.append(onKoraDestroyed)

            #Toggle visible command in UI
            addInsPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
            activateControl = addInsPanel.controls.itemById('ActivateKoraCmd')
            deactivateControl = addInsPanel.controls.itemById('DeactivateKoraCmd')
            if activateControl:
                activateControl.isVisible = False
            if deactivateControl:
                deactivateControl.isVisible = True

            #Start Kora
            global _koraThread
            _koraThread = KoraThread()
            _koraThread.start()

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class KoraDeactivatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

            global _koraThread
            if _koraThread:
                _ui.messageBox("Deactivating Kora")
                _koraThread.stop()
                _koraThread = None

            #Toggle visible command in UI
            addInsPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
            activateControl = addInsPanel.controls.itemById('ActivateKoraCmd')
            deactivateControl = addInsPanel.controls.itemById('DeactivateKoraCmd')
            if activateControl:
                activateControl.isVisible = True
            if deactivateControl:
                deactivateControl.isVisible = False

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class KoraDestroyedHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            _app.unregisterCustomEvent(customEventIDWitResponse)
            _app.unregisterCustomEvent(customEventIDPopupMessage)
            if _koraThread:
                _koraThread.stop()

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class WitResponseHandler(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            eventArgs = adsk.core.CustomEventArgs.cast(args)
            witResponse = json.loads(eventArgs.additionalInfo)
            _ui.messageBox(str(witResponse))
            executionResultCode = fusion_execute_intent.executeCommand(witResponse)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class PopupMessageHandler(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            global _ui
            eventArgs = adsk.core.CustomEventArgs.cast(args)
            messageInfo = json.loads(eventArgs.additionalInfo)
            if messageInfo['type'] == 'info':
                 _ui.messageBox(messageInfo['title'], messageInfo['message'])
            elif messageInfo['type'] == 'error':
                _ui.messageBox(messageInfo['title'], messageInfo['message'])
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))