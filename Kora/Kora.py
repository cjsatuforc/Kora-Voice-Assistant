import random
import traceback

import adsk.core, adsk.cam, adsk.fusion

from .main import config, globals
from .main.event_handlers import KoraActivatedHandler, KoraDeactivatedHandler, KoraPausedHandler, KoraResumedHandler
from .main.event_handlers import NLPResponseHandler, PaletteMessageHandler, PopupMessageHandler
from .main.kora_utils import getUI, getApp

_registeredCommands = []
_registeredCustomEvents = []

def run(context):
    try:
        random.seed()

        # TODO: set globals.onboarding

        commands = [
            {'id': 'ActivateKoraCmd', 'label': 'Activate Kora', 'tooltip': 'Activate Kora voice control for Fusion.', 'handler': KoraActivatedHandler(), 'visible': True},
            {'id': 'DeactivateKoraCmd', 'label': 'Deactivate Kora', 'tooltip': 'Deactivate Kora voice control for Fusion.', 'handler': KoraDeactivatedHandler(), 'visible': False},
            {'id': 'PauseKoraCmd', 'label': 'Pause Kora', 'tooltip': 'Pause Kora voice control for Fusion.', 'handler': KoraPausedHandler(), 'visible': False},
            {'id': 'ResumeKoraCmd', 'label': 'Resume Kora', 'tooltip': 'Resume Kora voice control for Fusion.', 'handler': KoraResumedHandler(), 'visible': False},
        ]

        customEvents = [
            {'id': config.customEventIDWitResponse, 'handler': NLPResponseHandler()},
            {'id': config.customEventIDPopupMessage, 'handler': PopupMessageHandler()},
            {'id': config.customEventIDPaletteMessage, 'handler': PaletteMessageHandler()}
        ]

        registerCommands(commands)
        registerCustomEvents(customEvents)
    except:
        ui = getUI()
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    ui = None
    try:
        if globals.koraThread:
            globals.koraThread.stop()
            globals.koraThread = None
        if globals.palette and not globals.palette.isNative:
            globals.palette.deleteMe()

        global _registeredCommands, _registeredCustomEvents
        app = getApp()
        ui = getUI()
        addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')

        for command in _registeredCommands:
            buttonControl = addInsPanel.controls.itemById(command['id'])
            if buttonControl:
                buttonControl.deleteMe()
            if command['definition']:
                command['definition'].deleteMe()

        _registeredCommands = []

        for event in _registeredCustomEvents:
            app.unregisterCustomEvent(event['id'])

        _registeredCustomEvents = []
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def registerCommands(commands):
    ui = getUI()
    addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')

    for command in commands:
        cmdDef = ui.commandDefinitions.addButtonDefinition(command['id'], command['label'], command['tooltip'])
        buttonControl = addInsPanel.controls.addCommand(cmdDef)
        buttonControl.isVisible = command['visible']
        cmdDef.commandCreated.add(command['handler'])
        _registeredCommands.append({'id': command['id'], 'definition': cmdDef, 'handler': command['handler']})  #Need to include handler so that it stays in scope.


def registerCustomEvents(customEvents):
    app = getApp()

    for event in customEvents:
        eventObj = app.registerCustomEvent(event['id'])
        eventObj.add(event['handler'])
        _registeredCustomEvents.append({'id': event['id'], 'handler': event['handler']})
