from ...Services.interactionService import logInteraction
from ...Services.extractionService import _getFromCommand
from ... import config
from ... import Tasks as tasks
from ...Tasks.ExecutionStatusCodes import StatusCodes



# ##########################################
# #        Main Fusion Execute Function   ##
# ##########################################

##
##    * Main execute command Function
##    * Note this function is funneled through the logInteraction decorator
##
@logInteraction()
def executeCommand(command, callback=None, firePopup=None):
    thresholdConfidence = config.thresholdConfidence
    intents = _getFromCommand(command, ['intent'])
    executionStatus = StatusCodes.UNRECOGNIZED_COMMAND
    chosenAPICall = None
    #app = adsk.core.Application.get()

    if intents:
        def shouldExecute(intentName):
            confidence = None
            for key, intentData in intents.items():
                if intentData['value'] == intentName:
                    confidence = intentData['confidence']
            return not (confidence is None) and (confidence >= thresholdConfidence)

        if shouldExecute('rotate'):
            chosenAPICall = 'rotate'
            direction = _getFromCommand(command, ['rotation_quantity', 'direction', 'value'])
            magnitude = _getFromCommand(command, ['rotation_quantity', 'number', 'value'])
            units = _getFromCommand(command, ['rotation_quantity', 'units', 'value'])
            executionStatus = tasks.rotate.run(firePopup, direction, magnitude, units)
        elif shouldExecute('save'):
            chosenAPICall = 'save'
            executionStatus = tasks.save.run()
        elif shouldExecute('save_as'):
            chosenAPICall = 'save_as'
            filename = _getFromCommand(command, ['file_name', 'value'])
            executionStatus = tasks.saveAs.run(filename)
        elif shouldExecute('extrude'):
            chosenAPICall = 'extrude'
            magnitude = _getFromCommand(command, ['extrude_quantity', 'number', 'value'])
            units = _getFromCommand(command, ['extrude_quantity', 'units', 'value'])
            executionStatus = tasks.extrude.run(magnitude, units)

    returnDict = {'fusionExecutionStatus': executionStatus, 'chosenAPICall': chosenAPICall}

    if callback:
        callback(returnDict)

    return returnDict

