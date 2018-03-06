import adsk.core, adsk.fusion, adsk.cam, traceback
from . import saveAs

##
##    * Executes a regular save operation
##    * Note You must use the SaveAs method the first time a document is saved
##
def _save():
    # Put here to avoid circular dependencies. If put in global space, import error
    from ..kora_modules.fusion_execute_intent import executionStatusCodes
    try:
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        doc = _app.activeDocument
        
        #if this is first save, must save as first        
        if not doc.isSaved:
            fileName = _ui.inputBox('You haven\'t saved this file yet, what would you like to name it?', 'Name Your File', 'myDraft')
            if fileName[1]: #second arg is True if box cancelled, false if submitted
                return executionStatusCodes.USER_ABORT
            else:
                return saveAs.run(fileName[0], True)

        #been saved as before, so just save new version
        elif not doc.save("1"):
            return executionStatusCodes.NONFATAL_ERROR

        #normal save() worked. Return success
        return executionStatusCodes.SUCCESS
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        return executionStatusCodes.FATAL_ERROR

def run():
	return _save()