from InteractionControllerBase import InteractionControllerBase
from Interaction import Interaction
from ConsoleLog import normal, notice
from MusicAnalyzer import similarity, predict


class TestInteraction1(Interaction):

    def setup(self):
        self.addCallback('websocket', self.onWebSocket)

    def loop(self):
        pass

    def onWebSocket(self, msg):
        notice("Received from websocket: {}".format(msg['cmd']))
        if msg['cmd'] == 'interaction':
            self.send("face", {
                "cmd": "face-change",
                "id": msg["id"]
            })


class InteractionController (InteractionControllerBase):

    def setup(self):
        self.registerHandler('websocket', self.onWebsocket)
        self.registerHandler('midi', self.onMidi)

    def loop(self):
        pass

    def onWebsocket(self, msg):
        normal("Received from websocket: {}".format(msg['cmd']))

    def onMidi(self, msg):
        if msg['cmd'] == 'phrase-end':
            notice("Received phrase: {} at {}-{}".format(msg['notes'], msg['start'], msg['end']))
        if msg['cmd'] == 'phrase':
            # normal("Similarity = {}".format(similarity([72, 76, 79, 84, 79, 76, 72], msg['notes'])))
            normal(predict(msg['notes']))
