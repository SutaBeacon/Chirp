import random

from Interaction import Interaction
from data.phrases import question
from ConsoleLog import notice


class MemoryGame (Interaction):

    notes = [0, 0, 0]

    state = "init"

    currentPhrase = []

    turn = 'player'
    playerScore = 0
    chirpScore = 0

    inputCounter = 0
    noteCount = 0

    gameCount = 0

    def generatePhrase(self, src, length):
        result = []
        for i in range(length):
            result.append(random.choice(src))
        return result


    def setup(self):
        self.makeFace("happy_open.json")
        self.registerHandler('serial', self.onSerial)
        self.registerHandler('midi', self.onMidi)
        self.state = "config-1"
        self.delay(3)
        self.oniSetLED(0, 1)

    def onMidi(self, msg):
        if msg['cmd'] == 'note-on':
            notice(self.state)
            if self.state == 'config-1':
                if msg['note'] in self.notes:
                    self.makeFace("nono.json")
                else:
                    self.setOniLED(0, 2)
                    self.setOniLED(1, 1)
                    self.makeFace("hint.json")
                    self.state = 'config-2'
                    self.notes[0] = msg['note']
            
            elif self.state == 'config-2':
                if msg['note'] in self.notes:
                    self.makeFace("serious-1.json")
                else:
                    self.setOniLED(1, 2)
                    self.setOniLED(2, 1)
                    self.makeFace("hint.json")
                    self.state = 'config-3'
                    self.notes[1] = msg['note']
            
            elif self.state == 'config-3':
                if msg['note'] in self.notes:
                    self.makeFace("nono.json")
                else:
                    self.setOniLED(2, 2)
                    self.makeFace("hint.json")
                    self.delay(0.3)
                    self.notes[2] = msg['note']
                    self.makeFace('happy_open.json')
                    self.delay(1)
                    self.makeFace('serious-2.json')
                    self.setAlarm(5, self.hint)
                    self.state = 'turn'
                    self.delay(1.5)

                    self.currentPhrase = self.generatePhrase(self.notes, 5)
                    self.noteCount = 5
                    for note in self.currentPhrase:
                        self.oniMakeNote(note)
                        self.delay(1)

            elif self.state == 'turn':
                if msg['note'] == self.currentPhrase[self.inputCounter]:
                    self.inputCounter += 1
                    if self.noteCount == self.inputCounter:
                        self.inputCounter = 0
                        self.playerScore += 1
                        if self.playerScore == 2:
                            self.win('player')
                            return
                        self.oniShowPoints(self.playerScore, self.chirpScore)
                        self.delay(0.3)
                        self.makeFace('pityful.json')
                        self.delay(0.5)
                        self.makeFace('serious-1.json')


    def win(self, who):
        if who == 'player':
            self.makeFace('grumpy.json')
            pass
        elif who == 'chirp':
            self.makeFace('laugh.json')
            self.delay(0.5)
            self.makeFace('startgame.json')
            self.delay(0.5)
            self.makeFace('laugh.json')

    def hint(self):
        self.makeFace('hint.json')

                
        
