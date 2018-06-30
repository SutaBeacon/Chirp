from Interaction import Interaction
from data.phrases import question


class MemoryGame (Interaction):

    notes = [0, 0, 0]

    state = "init"

    currentSequence = []


    def setup(self):
        self.registerHandler('serial', self.onSerial)
        self.registerHandler('midi', self.onMidi)
        self.state = "config-1"
        self.blinkOniLED(0)

    def loop(self):
        if self.message == "yes":
            self.sing(question, callback=self.end)
            self.makeFace("happy_closed.json")
        elif self.message == "no"::
            self.sing(question, callback=self.end)
            self.makeFace("pitiful.json")

    def onSerial(self, msg):
        self.terminate()

    def onMidi(self, msg):
        if self.state == 'config-1':
            if msg['note'] in self.notes:
                self.makeFace("nono.json")
            else:
                self.state = 'config-2'
                self.notes[0] = msg['note']
        
        elif self.state == 'config-2':
            if msg['note'] in self.notes:
                self.makeFace("nono.json")
            else:
                self.state = 'config-3'
                self.notes[1] = msg['note']
        
        elif self.state == 'config-3':
            if msg['note'] in self.notes:
                self.makeFace("nono.json")
            else:
                self.state = 'game-start'
                self.notes[2] = msg['note']
                self.makeFace('serious-2.json')
        
