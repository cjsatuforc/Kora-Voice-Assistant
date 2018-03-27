import adsk.core, adsk.fusion, adsk.cam, traceback

from ..ExecutionStatusCodes import StatusCodes

#TODO: Ask Jeremy why this needs to be global.
targetSaveFolder = None


##
##    * Saves a file by a given name
##    * If this is the first save as operation of this session, then
##      we need to get the current project's dataFolder.    
##
def _saveAs(fileName, commingFromSave=False):
    # Put here to avoid circular dependencies. If put in global space, import error
    try:
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # NO target folder for save. Need To get it
        global targetSaveFolder
        if not targetSaveFolder:
            targetSaveFolder = _app.data.activeProject.rootFolder
         
        def toCamel(s):
            if not isinstance(s, str):
                s = str(s)
            ret = ''.join(x for x in s.title() if not x.isspace()) 
            return ret[0].lower() + ret[1:]

        if not fileName:
            return StatusCodes.NONFATAL_ERROR

        #if name was entered by user from input, then save name as is
        saveName = fileName if commingFromSave else toCamel(fileName)

        doc = _app.activeDocument
        if not doc.saveAs(saveName, targetSaveFolder, '', ''): #been saved as before, so just save new version
            return StatusCodes.NONFATAL_ERROR
       
        return StatusCodes.SUCCESS
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))    
        return StatusCodes.FATAL_ERROR

def run(fileName, commingFromSave=False):
	return _saveAs(fileName, commingFromSave)