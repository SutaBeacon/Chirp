from InteractionControllerBase import InteractionControllerBase

from interactions.Sleepy import Sleepy


class InteractionController (InteractionControllerBase):

    def setup(self):
        self.registerHandler('websocket', self.onWebsocket)
        self.interactionQueue.add(Sleepy)

    def loop(self):
        pass

    def onWebsocket(self, msg):
        if msg['cmd'] == 'interaction':
            self.send("face", {
                "cmd": "face-change",
                "id": msg["id"]
            })
