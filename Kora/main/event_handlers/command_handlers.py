import traceback

import adsk.cam
import adsk.core
import adsk.fusion

from .. import config, globals
from ..kora_utils import getApp, getUI
from ..modules import nlp
from .kora_thread import KoraThread

_handlers = []

class KoraActivatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
        self.alreadyNotified = False

    def notify(self, args):
        try:
            ui = getUI()
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            inputs = eventArgs.command.commandInputs
            if not self.alreadyNotified:
                # Connect a handler to the command destroyed event.
                onKoraDestroyed = KoraDestroyedHandler()
                inputs.command.destroy.add(onKoraDestroyed)
                _handlers.append(onKoraDestroyed)

            # Toggle visible command in UI
            addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
            activateControl = addInsPanel.controls.itemById('ActivateKoraCmd')
            deactivateControl = addInsPanel.controls.itemById('DeactivateKoraCmd')
            pauseControl = addInsPanel.controls.itemById('PauseKoraCmd')
            if activateControl:
                activateControl.isVisible = False
            if deactivateControl:
                deactivateControl.isVisible = True
            if pauseControl:
                pauseControl.isVisible = True

            globals.palette = ui.palettes.itemById('myPalette')
            if not globals.palette:
                globals.palette = ui.palettes.add('myPalette', 'Kora', config.templatesLocation + 'initializing.html', True,
                                                  False, False, 300, 200)
                """onPaletteHTMLEvent = PaletteHTMLHandler()
                globals.palette.incomingFromHTML.add(onPaletteHTMLEvent)
                globals.handlers.append(onPaletteHTMLEvent)"""
            else:
                globals.palette.isVisible = True

            globals.palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateLeft

            # globals.palette.sendInfoToHTML('setContent', 'Blah blah blah testing setContent.')

            # Start Kora
            globals.koraThread = KoraThread()
            globals.koraThread.start()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class KoraDeactivatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            ui = getUI()
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

            if globals.koraThread:
                globals.koraThread.stop()
                globals.koraThread = None

            # Toggle visible command in UI
            addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
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

            if globals.palette and not globals.palette.isNative:
                globals.palette.deleteMe()
                globals.palette = None
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class KoraPausedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        # TODO: Wrap in try/except with error logging
        ui = getUI()
        if globals.koraThread:
            globals.koraThread.pause()
        nlp.stop()
        addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
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
        # TODO: Wrap in try/except with error logging
        ui = getUI()
        if globals.koraThread:
            globals.koraThread.resume()
        addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
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
            app = getApp()
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            app.unregisterCustomEvent(config.customEventIDWitResponse)
            app.unregisterCustomEvent(config.customEventIDPopupMessage)
            app.unregisterCustomEvent(config.customEventIDPaletteMessage)

            if globals.koraThread:
                globals.koraThread.stop()
                globals.koraThread = None
        except:
            ui = getUI()
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
