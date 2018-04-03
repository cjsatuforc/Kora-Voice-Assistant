from . import tasks
from .ExecutionStatusCodes import StatusCodes
from ..logging import logInteraction
from ... import config


@logInteraction()
def executeCommand(command, callback=None):
    thresholdConfidence = config.thresholdConfidence
    intents = _getFromCommand(command, ['intent'])
    executionStatus = StatusCodes.UNRECOGNIZED_COMMAND
    chosenAPICall = None

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
            executionStatus = tasks.rotate(direction, magnitude, units)
        elif shouldExecute('save'):
            chosenAPICall = 'save'
            executionStatus = tasks.save()
        elif shouldExecute('save_as'):
            chosenAPICall = 'save_as'
            filename = _getFromCommand(command, ['file_name', 'value'])
            executionStatus = tasks.saveAs(filename)
        elif shouldExecute('extrude'):
            text = _getFromCommand(distilledCommand, ['_text'])
            chosenAPICall = 'extrude'
            magnitude = _getFromCommand(command, ['extrude_quantity', 'number', 'value'])
            units = _getFromCommand(command, ['extrude_quantity', 'units', 'value'])
            executionStatus = tasks.extrude(text, magnitude, units)

    returnDict = {'fusionExecutionStatus': executionStatus, 'chosenAPICall': chosenAPICall}

    if callback:
        callback(returnDict)

    return returnDict

def _getFromCommand(command, searchKey):
    """
    :param command: A dictionary containing command data.
    :param searchKey: A list of keys that indicate what should be found in command.
                        Ex- searchKey=['intent'] Return the value of the first key found in command that is 'intent'
                        Ex- searchKey=['rotationQuantity', 'units'] Return the value of the first key that is 'units' that is nested inside of the value of key 'rotationQuantity'
    :return: The value of the specified key in command
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
                nextCmd = {i: nextCmd[i] for i in range(len(nextCmd))}

            res = _find(nextCmd, nextSKey)
            if not res is None:
                return res

        return None

    return _find(command, searchKey)