import random

from Interaction import Interaction
from data.phrases import question
from ConsoleLog import notice


class MemoryGame (Interaction):

    errorRate = 0.3

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
        self.registerHandler('midi', self.onMidi)
        self.state = "config-1"
        self.oniSetLED(0, 1)
        self.delay(3)

    def onMidi(self, msg):
        if msg['cmd'] == 'note-on':
            notice(self.state)
            if self.state == 'config-1':
                if msg['note'] in self.notes:
                    self.makeFace("nono.json")
                else:
                    self.oniSetLED(0, 2)
                    self.oniSetLED(1, 1)
                    self.makeFace("hint.json")
                    self.state = 'config-2'
                    self.notes[0] = msg['note']
            
            elif self.state == 'config-2':
                if msg['note'] in self.notes:
                    self.makeFace("serious-1.json")
                else:
                    self.oniSetLED(1, 2)
                    self.oniSetLED(2, 1)
                    self.makeFace("hint.json")
                    self.state = 'config-3'
                    self.notes[1] = msg['note']
            
            elif self.state == 'config-3':
                if msg['note'] in self.notes:
                    self.makeFace("nono.json")
                else:
                    self.oniSetLED(2, 2)
                    self.makeFace("hint.json")
                    self.delay(0.3)
                    self.notes[2] = msg['note']
                    self.makeFace('happy_open.json')
                    self.delay(1)
                    self.makeFace('serious-2.json')
                    self.setAlarm(5, self.hint)
                    self.state = 'playing'
                    self.delay(1.5)

                    self.currentPhrase = self.generatePhrase(self.notes, 5)
                    self.noteCount = 5
                    for note in self.currentPhrase:
                        self.oniMakeNote(note)
                        self.delay(1)

            elif self.state == 'playing':
                if msg['note'] == self.currentPhrase[self.inputCounter]:
                    # player correctly inputs a note
                    self.inputCounter += 1
                    if self.noteCount == self.inputCounter:
                        # player gets a point
                        self.inputCounter = 0
                        self.playerScore += 1
                        if self.playerScore == 2:
                            # player wins!
                            self.win('player')
                            return
                        self.oniShowPoints(self.playerScore, self.chirpScore)
                        # chirp is not happy about this
                        self.delay(0.3)
                        self.makeFace('pityful.json')
                        self.delay(0.5)
                        self.makeFace('serious-1.json')
                        # chirp's turn
                        self.delay(1)

                        mistake = False
                        for note in self.currentPhrase:
                            if random.random() < self.errorRate:
                                # chirp "decides" to make a mistake
                                self.makeFace('laugh.json')
                                n = random.choice(self.notes)
                                while n == note:
                                    n = random.choice(self.notes)
                                self.makeNote(n, 600, callback=self.serious)
                                self.delay(1)
                                # The mistake is made
                                mistake = True 
                                break
                            else:
                                self.makeFace('laugh.json')
                                self.makeNote(note, 600, callback=self.serious)
                                self.delay(1)
                        
                        if mistake:
                            # a mistake was made!
                            self.oniFail()
                            self.makeFace('pityful.json')
                            self.delay(0.5)
                            self.makeFace('nono.json')
                            self.delay(1.5)
                            self.makeFace('serious-1.json')
                        else:
                            self.oniSuccess()
                            self.makeFace('laugh.json')
                            self.delay(1.5)
                            self.chirpScore += 1
                            if self.chirpScore == 2:
                                # chirp wins!
                                self.win('chirp')
                                return
                    self.oniShowPoints(self.playerScore, self.chirpScore)
                                
                else:
                    # player fails
                    self.oniFail()
                    self.makeFace('laugh.json')
                    self.delay(1.5)

                        
    def singSequence(self, seq):
        for note in seq:
            self.makeFace('laugh.json')
            self.makeNote(note, 600, callback=self.serious)
            
    def oniFail(self):
        self.oniMakeNote(50)
        self.oniSetAllLED(1)
        self.delay(0.2)
        self.oniSetAllLED(0)
        self.delay(0.2)
        self.oniSetAllLED(1)
        self.delay(0.2)
        self.oniSetAllLED(0)
        self.delay(0.2)

    def oniSuccess(self):
        self.oniMakeNote(60)
        self.oniSetAllLED(1)
        self.delay(0.2)
        self.oniSetAllLED(0)
        self.delay(0.2)
        self.oniSetAllLED(1)
        self.delay(0.2)
        self.oniMakeNote(67)
        self.oniSetAllLED(0)
        self.delay(0.2)

    def win(self, who):
        if who == 'player':
            self.servoAngle(140)
            self.makeFace('grumpy.json')
            self.delay(0.8)
            self.servoAngle(150)
            self.delay(1)
            pass
        elif who == 'chirp':
            self.makeFace('laugh.json')
            self.delay(0.7)
            self.makeFace('startgame.json')
            self.delay(0.5)
            self.makeFace('laugh.json')
        self.terminate()

    def hint(self):
        self.makeFace('hint.json')

    def serious(self):
        self.faceFace('serious-1.json')

                
