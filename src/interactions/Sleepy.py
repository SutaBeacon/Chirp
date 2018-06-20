from Interaction import Interaction
from ConsoleLog import notice
from data.phrases import snore
from data.phrases import wakeup


class Sleepy(Interaction):

    def setup(self):
        self.registerHandler('midi', self.onMidi)
        self.setInstrument(73)
        self.makeFace('Sleepy.json')

    def loop(self):
        self.sing(snore)

    def onMidi(self, msg):
        notice("Received phrase: {} at {}-{}".format(msg['notes'], msg['start'], msg['end']))
        self.sing(wakeup, self.finish)
        self.makeFace('Wakeup.json')

    def finish(self, t):
        self.terminate()
