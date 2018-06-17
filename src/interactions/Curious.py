from Interaction import Interaction
from ConsoleLog import notice
from MusicAnalyzer import predict
from data.phrases import question


class Curious(Interaction):

    def setup(self):
        self.registerHandler('midi', self.onMidi)
        self.setInstrument(73)

    def loop(self):
        pass

    def onMidi(self, msg):
        if msg['cmd'] == 'phrase-end':
            notice("Received phrase: {} at {}-{}".format(msg['notes'], msg['start'], msg['end']))
            p = predict(msg['notes'])
            if p[0][0] == "Call" and p[1] > 0.8:
                self.sing(question, self.finish)
                self.makeFace(0)

    def finish(self, t):
        self.terminate()
