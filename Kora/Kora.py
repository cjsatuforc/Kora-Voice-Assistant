import threading
import json
import random

import adsk.core, adsk.fusion, adsk.cam, traceback
from . import config
from . import globals
from .kora_utils import getUI, getApp
from .event_handlers import KoraActivatedHandler, KoraDeactivatedHandler, KoraPausedHandler, KoraResumedHandler
from .event_handlers import NLPResponseHandler, PaletteMessageHandler, PopupMessageHandler

_activateCmdDef = adsk.core.CommandDefinition.cast(None)
_deactivateCmdDef = adsk.core.CommandDefinition.cast(None)
_pauseCmdDef = adsk.core.CommandDefinition.cast(None)
_resumeCmdDef = adsk.core.CommandDefinition.cast(None)
_handlers = []

def run(context):
    try:
        global _activateCmdDef, _deactivateCmdDef, _pauseCmdDef, _resumeCmdDef, _onboarding
        random.seed()
        app = getApp()
        ui = getUI()
        # TODO: set globals.onboarding

        addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')

        # Create a new command and add it to the ADD-INS panel in the model workspace.
        _activateCmdDef = ui.commandDefinitions.addButtonDefinition('ActivateKoraCmd', 'Activate Kora', 'Activate Kora voice control for Fusion.')
        activateButtonControl = addInsPanel.controls.addCommand(_activateCmdDef)

        # Connect the command created handler to the event.
        onKoraActivated = KoraActivatedHandler()
        _activateCmdDef.commandCreated.add(onKoraActivated)
        _handlers.append(onKoraActivated)

        # Repeat above steps for the command to deactivate Kora
        _deactivateCmdDef = ui.commandDefinitions.addButtonDefinition('DeactivateKoraCmd', 'Deactivate Kora', 'Deactivate Kora voice control for Fusion.')
        deactivateButtonControl = addInsPanel.controls.addCommand(_deactivateCmdDef)
        deactivateButtonControl.isVisible = False

        onKoraDeactivated = KoraDeactivatedHandler()
        _deactivateCmdDef.commandCreated.add(onKoraDeactivated)
        _handlers.append(onKoraDeactivated)

        # Repeat for command to pause Kora.
        _pauseCmdDef = ui.commandDefinitions.addButtonDefinition('PauseKoraCmd', 'Pause Kora', 'Pause Kora voice control for Fusion.')
        pauseButtonControl = addInsPanel.controls.addCommand(_pauseCmdDef)
        pauseButtonControl.isVisible = False

        onKoraPaused = KoraPausedHandler()
        _pauseCmdDef.commandCreated.add(onKoraPaused)
        _handlers.append(onKoraPaused)

        # Repeat for command to resume Kora.
        _resumeCmdDef = ui.commandDefinitions.addButtonDefinition('ResumeKoraCmd', 'Resume Kora', 'Resume Kora voice control for Fusion.')
        resumeButtonControl = addInsPanel.controls.addCommand(_resumeCmdDef)
        resumeButtonControl.isVisible = False

        onKoraResumed = KoraResumedHandler()
        _resumeCmdDef.commandCreated.add(onKoraResumed)
        _handlers.append(onKoraResumed)

        # Register the custom events and connect the handlers.
        customEventWitResponse = app.registerCustomEvent(config.customEventIDWitResponse)
        onWitResponse = NLPResponseHandler()
        customEventWitResponse.add(onWitResponse)
        _handlers.append(onWitResponse)

        customEventPopupMessage = app.registerCustomEvent(config.customEventIDPopupMessage)
        onPopupMessage = PopupMessageHandler()
        customEventPopupMessage.add(onPopupMessage)
        _handlers.append(onPopupMessage)

        customEventPaletteMessage = app.registerCustomEvent(config.customEventIDPaletteMessage)
        onPaletteMessage = PaletteMessageHandler()
        customEventPaletteMessage.add(onPaletteMessage)
        _handlers.append(onPaletteMessage)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context): #anything that should occur when Kora stops (e.g. when editor is closed)
    try:
        if globals.koraThread:
            globals.koraThread.stop()
            globals.koraThread = None
        if globals.palette and not globals.palette.isNative:
            globals.palette.deleteMe()
        # Clean up the command.
        app = getApp()
        ui = getUI()
        addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        activateControl = addInsPanel.controls.itemById('ActivateKoraCmd')
        deactivateControl = addInsPanel.controls.itemById('DeactivateKoraCmd')
        pauseControl = addInsPanel.controls.itemById('PauseKoraCmd')
        resumeControl = addInsPanel.controls.itemById('ResumeKoraCmd')

        app.unregisterCustomEvent(config.customEventIDWitResponse)
        app.unregisterCustomEvent(config.customEventIDPopupMessage)
        app.unregisterCustomEvent(config.customEventIDPaletteMessage)

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
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
