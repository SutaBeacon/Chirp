from Interaction import Interaction
from ConsoleLog import notice
from data.phrases import snore
from data.phrases import question


class Sleepy(Interaction):

    def setup(self):
        self.registerHandler('midi', self.onMidi)
        self.setInstrument(73)
        self.makeFace('sleepy.json')
        self.servoAngle(120)
        self.sing(snore)

    def loop(self):
        pass

    def onMidi(self, msg):
        notice("midi")
        # notice("Received phrase: {} at {}-{}".format(msg['notes'], msg['start'], msg['end']))
        self.sing(question, callback=self.finish)
        self.makeFace('wakeup.json')
        self.servoAngle(135)

    def finish(self, t):
        notice("quit")
        self.terminate()
