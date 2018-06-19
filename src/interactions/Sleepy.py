from Interaction import Interaction
from MusicAnalyzer import predict
from data.phrases import angry
from data.phrases import question


class Sleepy(Interaction):

    def setup(self):
        self.registerHandler('midi', self.onMidi)
        self.makeFace("Happy.json")

    def onMidi(self, msg):
        if msg['cmd'] == 'phrase-end':
            p = predict(msg['notes'])
            if p[0][0] == 'Wake Up' and p[1] > 0.6:
                self.sing(angry, self.finish)
                self.makeFace(2)
            elif p[0][0] == "Call" and p[1] > 0.8:
                self.sing(question, self.finish)
                self.makeFace(0)
            elif p[0][0] == "Play" and p[1] > 0.8:
                self.sing(question, self.finish)
                self.makeFace(1)

    def finish(self, t):
        self.terminate()
