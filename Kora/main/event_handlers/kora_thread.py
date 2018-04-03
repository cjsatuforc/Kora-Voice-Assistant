import json
import random
import threading
import traceback

from .. import config
from ..kora_utils import debugPopup, getApp
from ..modules import nlp


class KoraThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stopped = False
        self.paused = False
        self.uniqueID = str(random.randint(0, 9999))

    def run(self):
        app = getApp()

        def commandStartDetectedCallback():
            app.fireCustomEvent(config.customEventIDPaletteMessage, json.dumps({'message': 'listening'}))

        def commandEndDetectedCallback():
            app.fireCustomEvent(config.customEventIDPaletteMessage, json.dumps({'message': 'processing'}))

        try:
            app.fireCustomEvent(config.customEventIDPaletteMessage, json.dumps({'message': 'welcome'}))
            while not self.stopped:
                while not self.paused:
                    result = nlp.streamAudio(commandStartDetectedCallback,
                                             commandEndDetectedCallback)  # returns wit response json
                    debugPopup('info', 'KoraThread', 'KoraThread(' + self.uniqueID + ') exited steamAudio.')
                    if self.stopped:  # in case deactivation occurs while streamAudio is running
                        debugPopup('info', 'KoraThread',
                                   'KoraThread(' + self.uniqueID + ') encountered stop, discarding nlp result and breaking loop.')
                        break
                    elif not self.paused:
                        if 'streamingError' in result and result['streamingError']:
                            debugPopup('info', 'KoraThread', 'KoraThread(' + self.uniqueID + ') streaming error.')
                            app.fireCustomEvent(config.customEventIDPaletteMessage,
                                                json.dumps({'message': 'fatalError'}))
                        else:
                            debugPopup('info', 'KoraThread', 'KoraThread(' + self.uniqueID + ') sending WIT result.')
                            app.fireCustomEvent(config.customEventIDWitResponse, json.dumps(result))

            debugPopup('info', 'KoraThread Exit', 'KoraThread(' + self.uniqueID + ') closing.')
        except:
            debugPopup('error', 'Kora Failed', 'Failed:\n{}'.format(traceback.format_exc()))

    def stop(self):
        nlp.stop()
        self.stopped = True

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False