import adsk.core, adsk.fusion, adsk.cam, traceback, json

from .. import config
from ..kora_utils import getUI, debugPopup

class PaletteHTMLHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            ui = getUI()
            ui.messageBox('made it to here')
            htmlArgs = adsk.core.HTMLEventArgs.cast(args)
            data = json.loads(htmlArgs.data)
            if 1: #_onboarding and htmlArgs.action == 'next':
                self.goToNextOnboarding()
            ui.messageBox('finished with handler')
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def goToNextOnboarding(self):
        if globals.palette:
            globals.palette.htmlFileURL = config.templatesLocation + 'template2.html'
        else:
            debugPopup('info', 'goToNextOnboarding','globals.palette does not exist, cannot go to next')