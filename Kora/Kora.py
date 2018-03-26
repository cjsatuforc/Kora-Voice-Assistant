import threading
from array import array
import struct
import json
import requests
import math
import sys
import random

import adsk.core, adsk.fusion, adsk.cam, traceback
from .packages import pyaudio
from .kora_modules import nlp
from .kora_modules import fusion_execute_intent
from .kora_modules import text_to_speech
from .kora_modules import user_interface

_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_activateCmdDef = adsk.core.CommandDefinition.cast(None)
_deactivateCmdDef = adsk.core.CommandDefinition.cast(None)
_pauseCmdDef = adsk.core.CommandDefinition.cast(None)
_resumeCmdDef = adsk.core.CommandDefinition.cast(None)
_koraThread = None
_onboarding = None
_koraPaused = False
_debug = True
palette = None
_templatesLocation = './templates/'
handlers = []   #keeps handlers in scope
customEventIDWitResponse = 'WitResponseEvent'
customEventIDPopupMessage = 'PopupMessageEvent'
customEventIDPaletteMessage = 'PaletteMessageEvent'

# #################################
# #        Add-In Main          # #
# #################################

def run(context):
    try:
        global _app, _ui, _activateCmdDef, _deactivateCmdDef, _pauseCmdDef, _resumeCmdDef, _onboarding
        random.seed()
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        _onboarding = True

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

        # Pause.
        _pauseCmdDef = _ui.commandDefinitions.addButtonDefinition('PauseKoraCmd', 'Pause Kora', 'Pause Kora voice control for Fusion.')
        pauseButtonControl = addInsPanel.controls.addCommand(_pauseCmdDef)
        pauseButtonControl.isVisible = False

        onKoraPaused = KoraPausedHandler()
        _pauseCmdDef.commandCreated.add(onKoraPaused)
        handlers.append(onKoraPaused)

        _resumeCmdDef = _ui.commandDefinitions.addButtonDefinition('ResumeKoraCmd', 'Resume Kora', 'Resume Kora voice control for Fusion.')
        resumeButtonControl = addInsPanel.controls.addCommand(_resumeCmdDef)
        resumeButtonControl.isVisible = False

        onKoraResumed = KoraResumedHandler()
        _resumeCmdDef.commandCreated.add(onKoraResumed)
        handlers.append(onKoraResumed)

        # Register the custom event and connect the handler.
        customEventWitResponse = _app.registerCustomEvent(customEventIDWitResponse)
        onWitResponse = NLPResponseHandler()
        customEventWitResponse.add(onWitResponse)
        handlers.append(onWitResponse)

        customEventPopupMessage = _app.registerCustomEvent(customEventIDPopupMessage)
        onPopupMessage = PopupMessageHandler()
        customEventPopupMessage.add(onPopupMessage)
        handlers.append(onPopupMessage)

        customEventPaletteMessage = _app.registerCustomEvent(customEventIDPaletteMessage)
        onPaletteMessage = PaletteMessageHandler()
        customEventPaletteMessage.add(onPaletteMessage)
        handlers.append(onPaletteMessage)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context): #anything that should occur when Kora stops (e.g. when editor is closed)
    try:
        global _koraThread
        if _koraThread:
            _koraThread.stop()
            _koraThread = None
        if palette and not palette.isNative:
            palette.deleteMe()
        # Clean up the command.
        addInsPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        activateControl = addInsPanel.controls.itemById('ActivateKoraCmd')
        deactivateControl = addInsPanel.controls.itemById('DeactivateKoraCmd')
        pauseControl = addInsPanel.controls.itemById('PauseKoraCmd')
        resumeControl = addInsPanel.controls.itemById('ResumeKoraCmd')

        _app.unregisterCustomEvent(customEventIDWitResponse)
        _app.unregisterCustomEvent(customEventIDPopupMessage)
        _app.unregisterCustomEvent(customEventIDPaletteMessage)

        if activateControl:
            activateControl.deleteMe()
        if _activateCmdDef:
            _activateCmdDef.deleteMe()
        if deactivateControl:
            deactivateControl.deleteMe()
        if _deactivateCmdDef:
            _deactivateCmdDef.deleteMe()
        if pauseControl:
            pauseControl.deleteMe()
        if _pauseCmdDef:
            _pauseCmdDef.deleteMe()
        if resumeControl:
            resumeControl.deleteMe()
        if _resumeCmdDef:
            _resumeCmdDef.deleteMe()
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def goToNextOnboarding():
    if palette:
        palette.htmlFileURL = './template2.html'
    else:
        _ui.messageBox('palette does not exist, cannot go to next')

def debugPopup(type, title, message):
    if _debug:
        _app.fireCustomEvent(customEventIDPopupMessage, json.dumps({'type': type, 'title': title, 'message': message}))

class PaletteHTMLHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            _ui.messageBox('made it to here')
            htmlArgs = adsk.core.HTMLEventArgs.cast(args)
            data = json.loads(htmlArgs.data)
            if 1: #_onboarding and htmlArgs.action == 'next':
                goToNextOnboarding()
            _ui.messageBox('finished with handler')
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# ######################################
# #        Main Kora Thread          # #
# ######################################

class KoraThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stopped = False
        self.uniqueID = str(random.randint(0, 9999))

    def run(self):
        debugPopup('info', 'KoraThread Start', 'KoraThread(' + self.uniqueID + ') starting.')
        def commandStartDetectedCallback():
            _app.fireCustomEvent(customEventIDPaletteMessage, json.dumps({'message': 'listening'}))
        def commandEndDetectedCallback():
            _app.fireCustomEvent(customEventIDPaletteMessage, json.dumps({'message': 'processing'}))
        uID = self.uniqueID
        def fireMessage(message):
            debugPopup('info', 'NLP StreamAudio', 'KoraThread(' + uID + '): ' + message)
        try:
            _app.fireCustomEvent(customEventIDPaletteMessage, json.dumps({'message': 'welcome'}))
            while not self.stopped:
                while not _koraPaused:
                    result = nlp.streamAudio(fireMessage, commandStartDetectedCallback, commandEndDetectedCallback) #returns wit response json
                    debugPopup('info', 'KoraThread', 'KoraThread(' + self.uniqueID + ') exited steamAudio.')
                    if self.stopped:    #in case deactivation occurs while streamAudio is running
                        debugPopup('info', 'KoraThread', 'KoraThread(' + self.uniqueID + ') encountered stop, discarding nlp result and breaking loop.')
                        break
                    elif not _koraPaused:
                        if 'streamingError' in result and result['streamingError']:
                            debugPopup('info', 'KoraThread', 'KoraThread(' + self.uniqueID + ') streaming error.')
                            _app.fireCustomEvent(customEventIDPaletteMessage, json.dumps({'message': 'fatalError'}))
                        else:
                            debugPopup('info', 'KoraThread', 'KoraThread(' + self.uniqueID + ') sending WIT result.')
                            _app.fireCustomEvent(customEventIDWitResponse, json.dumps(result))

            debugPopup('info', 'KoraThread Exit', 'KoraThread(' + self.uniqueID + ') closing.')
        except:
            debugPopup('error', 'Kora Failed', 'Failed:\n{}'.format(traceback.format_exc()))
        
    def stop(self):
        nlp.stop()
        self.stopped = True


# ##########################################
# #        Kora Thread Handlers          # #
# ##########################################


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
            pauseControl = addInsPanel.controls.itemById('PauseKoraCmd')
            if activateControl:
                activateControl.isVisible = False
            if deactivateControl:
                deactivateControl.isVisible = True
            if pauseControl:
                pauseControl.isVisible = True

            global palette
            palette = _ui.palettes.itemById('myPalette')
            if not palette:
                palette = _ui.palettes.add('myPalette', 'Kora', _templatesLocation + 'initializing.html', True, False, False, 300, 200)
                onPaletteHTMLEvent = PaletteHTMLHandler()
                palette.incomingFromHTML.add(onPaletteHTMLEvent)
                handlers.append(onPaletteHTMLEvent)
            else:
                palette.isVisible = True

            palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateLeft

            #palette.sendInfoToHTML('setContent', 'Blah blah blah testing setContent.')

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
                _koraThread.stop()
                _koraThread = None

            #Toggle visible command in UI
            addInsPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
            activateControl = addInsPanel.controls.itemById('ActivateKoraCmd')
            deactivateControl = addInsPanel.controls.itemById('DeactivateKoraCmd')
            pauseControl = addInsPanel.controls.itemById('PauseKoraCmd')
            resumeControl = addInsPanel.controls.itemById('ResumeKoraCmd')
            if activateControl:
                activateControl.isVisible = True
            if deactivateControl:
                deactivateControl.isVisible = False
            if pauseControl:
                pauseControl.isVisible = False
            if resumeControl:
                resumeControl.isVisible = False

            global palette
            if palette and not palette.isNative:
                palette.deleteMe()
                palette = None

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class KoraPausedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global _koraPaused
        _koraPaused = True
        nlp.stop()
        addInsPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        pauseControl = addInsPanel.controls.itemById('PauseKoraCmd')
        resumeControl = addInsPanel.controls.itemById('ResumeKoraCmd')
        if pauseControl:
            pauseControl.isVisible = False
        if resumeControl:
            resumeControl.isVisible = True

class KoraResumedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global _koraPaused
        _koraPaused = False
        addInsPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        pauseControl = addInsPanel.controls.itemById('PauseKoraCmd')
        resumeControl = addInsPanel.controls.itemById('ResumeKoraCmd')
        if pauseControl:
            pauseControl.isVisible = True
        if resumeControl:
            resumeControl.isVisible = False

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

# #####################################
# #        Module Handlers          # #
# #####################################
 

class NLPResponseHandler(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            eventArgs = adsk.core.CustomEventArgs.cast(args)
            nlpResponse = json.loads(eventArgs.additionalInfo)

            #get userID
            nlpResponse['user'] = _app.userId
            debugPopup('info', 'NLP Response', str(nlpResponse))
            executionResult = fusion_execute_intent.executeCommand(nlpResponse, firePopup=debugPopup)
            _app.fireCustomEvent(customEventIDPaletteMessage, json.dumps({'message': executionResult['fusionExecutionStatus']}))
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
                _ui.messageBox("INFO: " + messageInfo['message'], messageInfo['title'])
            elif messageInfo['type'] == 'error':
                _ui.messageBox("ERROR: " + messageInfo['message'], messageInfo['title'])
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class PaletteMessageHandler(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            global _ui, palette
            eventArgs = adsk.core.CustomEventArgs.cast(args)
            messageInfo = json.loads(eventArgs.additionalInfo)
            newTemplate = ''
            if messageInfo['message'] == 'listening':
                newTemplate = _templatesLocation + 'listening.html'
            elif messageInfo['message'] == 'processing':
                newTemplate = _templatesLocation + 'processing.html'
            elif messageInfo['message'] == 'success':
                newTemplate = _templatesLocation + 'success.html'
            elif messageInfo['message'] == 'fatalError' or messageInfo['message'] == 'nonfatalError':
                newTemplate = _templatesLocation + 'error.html'
            elif messageInfo['message'] == 'unrecognizedCommand':
                newTemplate = _templatesLocation + 'unrecognizedCommand.html'
            elif messageInfo['message'] == 'userAbort':
                newTemplate = _templatesLocation + 'userAbort.html'
            elif messageInfo['message'] == 'welcome':
                newTemplate = _templatesLocation + 'welcome.html'
            else:
                _ui.messageBox('did not find template for: ' + messageInfo['message'])

            if palette and newTemplate:
                palette.htmlFileURL = newTemplate
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
