import adsk.core, adsk.fusion, adsk.cam, traceback
from array import array
import struct
import json
import requests
import math

def executeCommand(command, ui, callback=None):
    distilledCommand = _distillCommand(command)
    thresholdConfidence = 0.79
    intents = _getFromCommand(distilledCommand, ['intent'])
    executionStatus = executionStatusCodes.UNRECOGNIZED_COMMAND

    def shouldExecute(intentName):
        confidence = None
        for key, intentData in intents.items():
            if intentData['value'] == intentName:
                confidence = intentData['confidence']
        return not confidence is None and confidence >= thresholdConfidence

    if shouldExecute('rotate'):
        executionStatus = _rotate(_getFromCommand(distilledCommand, ['rotation_quantity', 'direction', 'value']),
                _getFromCommand(distilledCommand, ['rotation_quantity', 'number', 'value']),
                _getFromCommand(distilledCommand, ['rotation_quantity', 'units', 'value']), ui
                )
    if shouldExecute('save'):
        executionStatus = _save(_getFromCommand(distilledCommand, ['file_name']))

    if callback:
        callback(executionStatus)

    return executionStatus

class executionStatusCodes(object):
    FATAL_ERROR = 1 #For runtime errors/exceptions
    NONFATAL_ERROR = 2 #For non-exception errors that make it so that execution can't be completed
    UNRECOGNIZED_COMMAND = 3 #Didn't recognize intent of command
    SUCCESS = 4

##########################################################################
##########################################################################
##########################################################################
##########################################################################

def _rotate(direction, magnitude=None, units='degrees', ui=None):
    if not direction:
        return executionStatusCodes.NONFATAL_ERROR
    if units == 'degrees':
        if magnitude == None:
            magnitude = math.pi / 2.0
        else:
            magnitude = math.radians(magnitude)
        units = 'radians'
    elif magnitude == None:
        magnitude = math.pi / 2.0

    app = adsk.core.Application.get()
    camera = app.activeViewport.camera
    rotationMatrix = adsk.core.Matrix3D.create()

    #TODO: I've been messing around with how to make rotation work properly and am almost there.
    #TODO: Will continue to work on it with new method of not actually rotating but moving camera which in turn rotates object. -Austin
    if direction == 'left' or direction == 'right':
        axisOfRotation = camera.eye.asVector()
        if direction == 'right':
            axisOfRotation.scaleBy(-1.0)
        translationVector = camera.upVector
        rotationMatrix.setToRotation(math.pi / 2.0, axisOfRotation, camera.target)
        translationVector.transformBy(rotationMatrix)
        magnitude = abs(magnitude) / math.pi
        translationVector.scaleBy(magnitude*100)
        newPos = camera.eye.asVector()
        newPos.add(translationVector)
        camera.eye = newPos.asPoint()
        """if direction == 'left':
            axisOfRotation = camera.upVector
            axisOfRotation.y *= -1.0
        elif direction == 'right':
            axisOfRotation = camera.upVector
        rotationMatrix.setToRotation(magnitude, axisOfRotation, camera.target)
        newPos = camera.eye.asVector()
        newPos.transformBy(rotationMatrix)
        camera.eye = newPos.asPoint()"""
    else:
        if magnitude < 0:
            direction = 'up' if direction == 'down' or direction == 'downward' else 'down'
        magnitude = abs(magnitude) / math.pi
        if direction == 'down' or direction == 'downward':
            magnitude *= -1.0
        translationVector = camera.upVector
        translationVector.scaleBy(magnitude*100)
        newPos = camera.eye.asVector()
        newPos.add(translationVector)
        camera.eye = newPos.asPoint()
        """axisOfRotation = camera.eye.asVector()
        axisOfRotation.normalize()
        axisRotationMatrix = adsk.core.Matrix3D.create()
        if direction == 'up' or direction == 'upward':
            subAxis = camera.upVector
            axisOfRotation.y *= -1.0
        else:
            subAxis = camera.upVector
        axisRotationMatrix.setToRotation(math.pi / 2.0, subAxis, camera.target)
        axisOfRotation.transformBy(axisRotationMatrix)"""



    app.activeViewport.camera = camera

    return executionStatusCodes.SUCCESS

def _save(fileName=None):
    if fileName:
        pass #TODO: Call FusionDocument.saveAs method from API
    else:
        pass #TODO: Call FusionDocument.save method from API

    return executionStatusCodes.SUCCESS

##########################################################################
##########################################################################
##########################################################################
##########################################################################

def _distillCommand(command):
    """
    :param command: The Wit.ai intent JSON object.
    :param callback: Callback function of form callback(int) where int is an integer status value
    :return: A modified version of command that has been reformatted for easier access to relevant data.
    """
    return command

def _getFromCommand(distilledCommand, searchKey):
    """
    :param distilledCommand: A dictionary containing command data.
    :param searchKey: A list of keys that indicate what should be found in command.
                        Ex- searchKey=['intent'] Return the value of the first key found in distilledCommand that is 'intent'
                        Ex- searchKey=['rotationQuantity', 'units'] Return the value of the first key that is 'units' that is nested inside of the value of key 'rotationQuantity'
    :return: The value of the specified key in distilledCommand
    """

    if not isinstance(searchKey, list):
        searchKey = [searchKey]

    def _find(cmd, sKey):
        if not sKey:
            if isinstance(cmd, dict) and 'value' in cmd:
                return cmd['value']
            return cmd
        elif not isinstance(cmd, dict):
            return None

        for key, value in cmd.items():
            nextCmd = value
            if key == sKey[0]:
                nextSKey = sKey[1:]
            else:
                nextSKey = sKey

            if isinstance(nextCmd, list):
                nextCmd = {i:nextCmd[i] for i in range(len(nextCmd))}

            res = _find(nextCmd, nextSKey)
            if not res is None:
                return res

        return None

    return _find(distilledCommand, searchKey)
