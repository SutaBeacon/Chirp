from InteractionControllerBase import InteractionControllerBase
from Interaction import Interaction
from ConsoleLog import normal, notice


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
        self._interactions.add(TestInteraction1)

    def loop(self):
        pass

    def onWebsocket(self, msg):
        normal("Received from websocket: {}".format(msg['cmd']))
