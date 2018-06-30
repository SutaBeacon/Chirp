from Interaction import Interaction
from ConsoleLog import notice
from data.phrases import snore
from data.phrases import wakeup


class Sleepy(Interaction):

    def setup(self):
        self.registerHandler('midi', self.onMidi)
        self.setInstrument(73)
        self.makeFace('happy_open.json')
        self.servoAngle(120)
        self.sing(snore)

    def loop(self):
        pass

    def onMidi(self, msg):
        notice("midi")
        # notice("Received phrase: {} at {}-{}".format(msg['notes'], msg['start'], msg['end']))
        self.makeFace('hungry.json')
        self.servoAngle(135)
        self.delay(10)
        self.makeFace('eating.json')
        self.delay(15)
        self.makeFace('laugh.json')
        self.terminate()

    def finish(self, t):
        self.terminate()
