from Interaction import Interaction
from ConsoleLog import notice
from MusicAnalyzer import predict
from data.phrases import question


class Curious(Interaction):

    def setup(self):
        self.registerHandler('websocket', self.onWebSocket)
        self.registerHandler('midi', self.onMidi)
        self.send("midi", {
            "cmd": "instrument",
            "id": 73
        })

    def loop(self):
        pass

    def onWebSocket(self, msg):
        notice("Received from websocket: {}".format(msg['cmd']))

    def onMidi(self, msg):
        if msg['cmd'] == 'phrase-end':
            notice("Received phrase: {} at {}-{}".format(msg['notes'], msg['start'], msg['end']))
            p = predict(msg['notes'])
            if p[0][0] == "Call" and p[1] > 0.8:
                self.sing(question, self.finish)
                self.send("face", {
                    "cmd": "face-change",
                    "id": 2
                })

    def finish(self, t):
        self.terminate()
