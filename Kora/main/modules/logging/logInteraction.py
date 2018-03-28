import time
import traceback
from functools import wraps

from ...kora_utils import debugPopup
from . import mongoSetup as mongoSetup
from .interaction import Interaction
from ... import config

mongoSetup.globalInit()  # connecting to db

def logInteraction():
    def decorator(executeFusion):
        @wraps(executeFusion)
        def wrapper(*args, **kwargs):
            try:
                if config.skipLogging:
                    executeResponse = executeFusion(*args, **kwargs)
                else:
                    # extract the dictionary from *args
                    argToFusion = args[0]

                    # get new Interaction object
                    newInteraction = Interaction()

                    if 'user' in argToFusion:
                        newInteraction.user = argToFusion['user']
                        del argToFusion['user']  # take it out to store pure witResponse

                    # Gather the time it took wit to respond
                    totalExecuteTime = 0
                    if 'witDelay' in argToFusion:
                        totalExecuteTime += float(argToFusion['witDelay'])
                        del argToFusion['witDelay']  # take it out to store pure witResponse

                    # Store the wit response free of added JSON
                    newInteraction.witResponse = argToFusion

                    # Time Fuison execute command
                    before = time.time()

                    executeResponse = executeFusion(*args, **kwargs)

                    after = time.time()

                    # Store total execution time
                    totalExecuteTime += float(after - before)
                    newInteraction.execTime = totalExecuteTime

                    # Extract from executeResponse
                    if 'chosenAPICall' in executeResponse:
                        newInteraction.chosenAPICall = executeResponse['chosenAPICall']
                    if 'fusionExecutionStatus' in executeResponse:
                        newInteraction.fusionExecutionStatus = executeResponse['fusionExecutionStatus']

                    try:
                        newInteraction.save()
                    except:
                        # TODO: Replace with logging function.
                        debugPopup('error', 'logInteraction', 'InteractionService Failed to Save'.format(traceback.format_exc()))

                # return the execution status like originally
                return executeResponse
            except:
                return {'fusionExecutionStatus': 'nonfatalError'}

        return wrapper

    return decorator
