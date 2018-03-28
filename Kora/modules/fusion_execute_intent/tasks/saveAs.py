import adsk.core, adsk.fusion, adsk.cam, traceback

from ..ExecutionStatusCodes import StatusCodes
from ....kora_utils import getApp, debugPopup

def saveAs(fileName, commingFromSave=False):
    targetSaveFolder = None
    try:
        _app = getApp()

        # NO target folder for save. Need To get it
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
        debugPopup('error', 'saveAs', 'Failed:\n{}'.format(traceback.format_exc()))
        return StatusCodes.FATAL_ERROR
