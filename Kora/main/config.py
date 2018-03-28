
import os

WIT_AI_CLIENT_ACCESS_TOKEN = 'JV6WLCBDLTXIJUAOQ2MOOFBR7DUZQON7'  # Put your Client Access Token Here
thresholdConfidence = 0.79  # WIT intent confidence to proceed with execution
skipLogging = True
debugMode = True
templatesLocation = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates/')
customEventIDWitResponse = 'WitResponseEvent'
customEventIDPopupMessage = 'PopupMessageEvent'
customEventIDPaletteMessage = 'PaletteMessageEvent'
