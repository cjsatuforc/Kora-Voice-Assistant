import traceback

from ....kora_utils import getApp, getUI
from . import saveAs
from ..ExecutionStatusCodes import StatusCodes


def save():
    try:
        app = getApp()
        ui = getUI()

        doc = app.activeDocument

        if not doc.isSaved:  # if this is first save, must save as first
            fileName = ui.inputBox('You haven\'t saved this file yet, what would you like to name it?', 'Name Your File', 'myDraft')
            if fileName[1]:  # second arg is True if box cancelled, false if submitted
                return StatusCodes.USER_ABORT
            else:
                return saveAs(fileName[0], True)
        elif not doc.save("1"):
            return StatusCodes.NONFATAL_ERROR

        return StatusCodes.SUCCESS
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        return StatusCodes.FATAL_ERROR
