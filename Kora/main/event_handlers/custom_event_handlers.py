import json
import traceback

import adsk.cam
import adsk.core
import adsk.fusion

from .. import config, globals
from ..kora_utils import debugPopup, getApp, getUI
from ..modules import fusion_execute_intent


class NLPResponseHandler(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            app = getApp()
            eventArgs = adsk.core.CustomEventArgs.cast(args)
            nlpResponse = json.loads(eventArgs.additionalInfo)

            nlpResponse['user'] = app.userId
            debugPopup('info', 'NLP Response', str(nlpResponse))
            executionResult = fusion_execute_intent.executeCommand(nlpResponse)
            app.fireCustomEvent(config.customEventIDPaletteMessage, json.dumps({'message': executionResult['fusionExecutionStatus']}))
        except:
            _ui = getUI()
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class PopupMessageHandler(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            _ui = getUI()
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
            _ui = getUI()
            eventArgs = adsk.core.CustomEventArgs.cast(args)
            messageInfo = json.loads(eventArgs.additionalInfo)
            newTemplate = ''
            if messageInfo['message'] == 'listening':
                newTemplate = config.templatesLocation + 'listening.html'
            elif messageInfo['message'] == 'processing':
                newTemplate = config.templatesLocation + 'processing.html'
            elif messageInfo['message'] == 'success':
                newTemplate = config.templatesLocation + 'success.html'
            elif messageInfo['message'] == 'fatalError' or messageInfo['message'] == 'nonfatalError':
                newTemplate = config.templatesLocation + 'error.html'
            elif messageInfo['message'] == 'unrecognizedCommand':
                newTemplate = config.templatesLocation + 'unrecognizedCommand.html'
            elif messageInfo['message'] == 'userAbort':
                newTemplate = config.templatesLocation + 'userAbort.html'
            elif messageInfo['message'] == 'welcome':
                newTemplate = config.templatesLocation + 'welcome.html'
            else:
                _ui.messageBox('did not find template for: ' + messageInfo['message'])

            if globals.palette and newTemplate:
                globals.palette.htmlFileURL = newTemplate
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
