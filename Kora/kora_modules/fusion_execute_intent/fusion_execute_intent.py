from ...Services.interactionService import logInteraction
from ...Services.extractionService import _getFromCommand
from ... import config
from ... import Tasks as tasks
import adsk.core, adsk.fusion, adsk.cam, traceback


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
    thresholdConfidence = config.thresholdConfidence
    intents = _getFromCommand(distilledCommand, ['intent'])
    executionStatus = executionStatusCodes.UNRECOGNIZED_COMMAND
    chosenAPICall = None
    app = adsk.core.Application.get()
    ui = app.userInterface

    def shouldExecute(intentName):
        confidence = None
        for key, intentData in intents.items():
            if intentData['value'] == intentName:
                confidence = intentData['confidence']
        return not (confidence is None) and (confidence >= thresholdConfidence)

    if shouldExecute('rotate'):
        chosenAPICall = 'rotate'
        executionStatus = tasks.rotate.run(_getFromCommand(distilledCommand, ['rotation_quantity', 'direction', 'value']),
                _getFromCommand(distilledCommand, ['rotation_quantity', 'number', 'value']),
                _getFromCommand(distilledCommand, ['rotation_quantity', 'units', 'value'])
                )

    elif shouldExecute('save'):
        chosenAPICall = 'save'
        executionStatus = tasks.save.run()

    elif shouldExecute('save_as'):
        chosenAPICall = 'save_as'
        executionStatus = tasks.saveAs.run(_getFromCommand(distilledCommand, ['file_name', 'value']) )

    elif shouldExecute('extrude'):
        chosenAPICall = 'extrude'

        negate = False;
        text = _getFromCommand(distilledCommand, ['_text'])
        if text and "push down" in text or "negative" in text:
            negate = True

        executionStatus = tasks.extrude.run(_getFromCommand(distilledCommand, ['extrude_quantity', 'number', 'value']),
                _getFromCommand(distilledCommand, ['extrude_quantity', 'units', 'value']),
                negate)

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

