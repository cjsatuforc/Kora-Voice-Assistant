import adsk.core, adsk.fusion, adsk.cam, traceback
from .packages.pywit.wit import Wit
#from .packages import sounddevice as sd

WIT_AI_CLIENT_ACCESS_TOKEN = 'Q6QP5OFCOQRS65KEIQZO3OPD47XFLGUE'

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox('Hello World')
        from .packages import sounddevice as sd
        #from . import soundfile as sf
        """client = Wit(WIT_AI_CLIENT_ACCESS_TOKEN)
        response = client.message('please save')
        ui.messageBox(str(response))"""

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


