from InteractionControllerBase import InteractionControllerBase
from ConsoleLog import normal, notice
from interactions.InitiateGame import InitiateGame


class InteractionController (InteractionControllerBase):

    def setup(self):
        self.registerHandler('websocket', self.onWebsocket)
        self.registerHandler('midi', self.onMidi)
        self.interactionQueue.add(InitiateGame)
        # self.setAlarm(1.0, self.test)

    def test(self, t):
        notice("asdfasdfasdf", t)
        self.setAlarm(1.0, self.test)

    def onWebsocket(self, msg):
        if msg['cmd'] == 'animation':
            self.send("face", {
                "cmd": "face-change",
                "id": msg["id"]
            })
        elif msg['cmd'] == 'face-finished':
            normal(msg['id'])

    def onMidi(self, msg):
        if msg['cmd'] == 'phrase-end':
            notice(msg)
