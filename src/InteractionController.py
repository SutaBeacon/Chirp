from InteractionControllerBase import InteractionControllerBase
from ConsoleLog import normal, notice
from interactions.InitiateGame import InitiateGame
from interactions.Sleepy import Sleepy
from interactions.MemoryGame import MemoryGame
from interactions.Duet import Duet


class InteractionController (InteractionControllerBase):

    def setup(self):
        self.registerHandler('websocket', self.onWebsocket)
        self.registerHandler('midi', self.onMidi)
        self.interactionQueue.add(Sleepy)
        self.interactionQueue.add(Duet)
        # self.interactionQueue.add(R)
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
        elif msg['cmd'] == 'interaction':
            if msg['id'] == 0:
                self.interactionQueue.clear()
                self.interactionQueue.add(Sleepy)
            elif msg['id'] == 1:
                self.interactionQueue.clear()
                self.interactionQueue.add(Duet)
            elif msg['id'] == 2:
                self.interactionQueue.clear()
                self.interactionQueue.add(MemoryGame)

    def onMidi(self, msg):
        if msg['cmd'] == 'phrase-end':
            notice(msg)
