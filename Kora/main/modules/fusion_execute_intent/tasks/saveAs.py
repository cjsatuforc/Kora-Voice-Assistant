import traceback

from ....kora_utils import getApp, debugPopup
from ..ExecutionStatusCodes import StatusCodes


<<<<<<< HEAD:Kora/Tasks/saveAs.py
##
##    * Saves a file by a given name
##    * If this is the first save as operation of this session, then
##      we need to get the current project's dataFolder.    
##
def _saveAs(fileName, commingFromSave=False):
    # Put here to avoid circular dependencies. If put in global space, import error
=======
def saveAs(fileName, commingFromSave=False):
    targetSaveFolder = None
>>>>>>> 7df36a68ba2d402dd7d68dfb1e27b26b3a5417e7:Kora/main/modules/fusion_execute_intent/tasks/saveAs.py
    try:
        _app = getApp()

<<<<<<< HEAD:Kora/Tasks/saveAs.py
        targetSaveFolder = _app.data.activeProject.rootFolder
=======
        # NO target folder for save. Need To get it
        if not targetSaveFolder:
            targetSaveFolder = _app.data.activeProject.rootFolder
>>>>>>> 7df36a68ba2d402dd7d68dfb1e27b26b3a5417e7:Kora/main/modules/fusion_execute_intent/tasks/saveAs.py
         
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
        debugPopup('error', 'saveAs', 'Failed:\n{}'.format(traceback.format_exc()))
        return StatusCodes.FATAL_ERROR
