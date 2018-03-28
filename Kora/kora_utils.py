import adsk.core, adsk.fusion, adsk.cam, traceback, json
from . import config


def debugPopup(type, title, message):
    if config.debugMode:
        getApp().fireCustomEvent(config.customEventIDPopupMessage, json.dumps({'type': type, 'title': title, 'message': message}))


def getApp():
    return adsk.core.Application.get()


def getUI():
    return adsk.core.Application.get().userInterface
