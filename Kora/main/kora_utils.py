import adsk.cam
import adsk.core
import adsk.fusion
import json

from . import config


def debugPopup(type, title, message):
    if config.debugMode:
        getApp().fireCustomEvent(config.customEventIDPopupMessage, json.dumps({'type': type, 'title': title, 'message': message}))


def getApp():
    return adsk.core.Application.get()


def getUI():
    return adsk.core.Application.get().userInterface
