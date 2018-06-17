from InteractionControllerBase import InteractionControllerBase

from interactions.Curious import Curious


class InteractionController (InteractionControllerBase):

    def setup(self):
        self.registerHandler('websocket', self.onWebsocket)

    def loop(self):
        if self.interactionQueue.isEmpty():
            self.interactionQueue.add(Curious)

    def onWebsocket(self, msg):
        if msg['cmd'] == 'interaction':
            self.send("face", {
                "cmd": "face-change",
                "id": msg["id"]
            })
