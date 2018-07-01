from Interaction import Interaction
from ConsoleLog import notice
from data.phrases import snore
from data.phrases import question


class Sleepy(Interaction):

    def setup(self):
        self.registerHandler('midi', self.onMidi)
        self.setInstrument(73)
        self.makeFace('sleepy.json')
        for i in range(10):
            self.servoAngle(150-i)
            self.delay(0.06)
        self.delay(0.5)
        for i in range(10):
            self.servoAngle(140-i)
            self.delay(0.06)
        self.delay(0.5)
        for i in range(10):
            self.servoAngle(130-i)
            self.delay(0.06)

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
