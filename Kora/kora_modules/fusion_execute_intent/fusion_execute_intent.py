from array import array
import struct
import json
import requests
import math

import adsk.core, adsk.fusion, adsk.cam, traceback
from ...Services.interactionService import logInteraction


_app = adsk.core.Application.get()
_ui = _app.userInterface
targetSaveFolder = None

# ##########################################
# #        Main Fusion Execute Function   ##
# ##########################################

##
##    * Main execute command Function
##    * Note this function is funneled through the logInteraction decorator
##
@logInteraction()
def executeCommand(command, callback=None):
    distilledCommand = _distillCommand(command)
    thresholdConfidence = 0.79
    intents = _getFromCommand(distilledCommand, ['intent'])
    executionStatus = executionStatusCodes.UNRECOGNIZED_COMMAND
    chosenAPICall = None

    def shouldExecute(intentName):
        confidence = None
        for key, intentData in intents.items():
            if intentData['value'] == intentName:
                confidence = intentData['confidence']
        return not (confidence is None) and (confidence >= thresholdConfidence)

    if shouldExecute('rotate'):
        chosenAPICall = 'rotate'
        executionStatus = _rotate(_getFromCommand(distilledCommand, ['rotation_quantity', 'direction', 'value']),
                _getFromCommand(distilledCommand, ['rotation_quantity', 'number', 'value']),
                _getFromCommand(distilledCommand, ['rotation_quantity', 'units', 'value'])
                )
    elif shouldExecute('save'):
        chosenAPICall = 'save'
        executionStatus = _save()

    elif shouldExecute('save_as'):
        chosenAPICall = 'save_as'
        executionStatus = _save_as(_getFromCommand(distilledCommand, ['file_name', 'value']) )

    # return to logInteraction decorator
    returnDict = {'fusionExecutionStatus': executionStatus, 'chosenAPICall': chosenAPICall}

    if callback:
        callback(returnDict)

    return returnDict

class executionStatusCodes(object):
    FATAL_ERROR = 1 #For runtime errors/exceptions
    NONFATAL_ERROR = 2 #For non-exception errors that make it so that execution can't be completed
    UNRECOGNIZED_COMMAND = 3 #Didn't recognize intent of command
    USER_ABORT = 4 #User aborted command
    SUCCESS = 5








# ###################################
# #        API Execute Functions   ##
# ###################################

##
##    * Executes a regular save operation
##    * Note You must use the SaveAs method the first time a document is saved
##
def _save():
    try:
        global _app, _ui
        doc = _app.activeDocument
        
        #if this is first save, must save as first        
        if not doc.isSaved:
            fileName = _ui.inputBox('You haven\'t saved this file yet, what would you like to name it?', 'Name Your File', 'myDraft')
            if fileName[1]: #second arg is True if box cancelled, false if submitted
                return executionStatusCodes.USER_ABORT
            else:
                return _save_as(fileName[0], True)

        #been saved as before, so just save new version
        elif not doc.save("1"):
            return executionStatusCodes.NONFATAL_ERROR

        #normal save() worked. Return success
        return executionStatusCodes.SUCCESS
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        return executionStatusCodes.FATAL_ERROR
##
##    * Saves a file by a given name
##    * If this is the first save as operation of this session, then
##      we need to get the current project's dataFolder.    
##
def _save_as(fileName, commingFromSave=False):
    try:   
        #NO target folder for save. Need To get it
        global targetSaveFolder
        if not targetSaveFolder:
            targetSaveFolder = _app.data.activeProject.rootFolder
         
        def toCamel(s):
            if not isinstance(s, str):
                s = str(s)
            # _ui.messageBox("in toCamel: " + s)
            ret = ''.join(x for x in s.title() if not x.isspace()) 
            return ret[0].lower() + ret[1:]

        if not fileName:
            return executionStatusCodes.NONFATAL_ERROR

        #if name was entered by user from input, then save name as is
        saveName = fileName if commingFromSave else toCamel(fileName)

        global _app
        doc = _app.activeDocument
        if not doc.saveAs(saveName, targetSaveFolder, '', ''): #been saved as before, so just save new version
            return executionStatusCodes.NONFATAL_ERROR
       
        return executionStatusCodes.SUCCESS
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))    
        return executionStatusCodes.FATAL_ERROR


##
##   * Rotates the camera <magnitude> units in the <direction>
##
def _rotate(direction, magnitude=None, units='degrees'):
    global _app

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

    camera = _app.activeViewport.camera
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



    _app.activeViewport.camera = camera

    return executionStatusCodes.SUCCESS





# #######################################
# #        JSON Extraction Functions   ##
# #######################################
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
