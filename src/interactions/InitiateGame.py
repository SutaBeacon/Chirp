from Interaction import Interaction
from data.phrases import question


class InitiateGame (Interaction):

    def setup(self):
        # TODO: 换上真正的音乐和脸
        self.message = None

        print("startgame")
        self.setOniLED(0, 1, 1)
        self.makeFace("startgame.json")
        self.sing(question, callback=self.findFace)     # Start Gane Sound

    def findFace(self, t):
        self.makeFace("happy_open.json")
        print("happyclosed")
        self.sing(question, callback=self.foundFace)    # Happy sound 

    def foundFace(self, t):
        print("sin game theme song")
        self.sing(question, callback=self.confirmGame)  # Game theme song

    def confirmGame(self, t):
        pass

    def loop(self):
        if self.message == "yes":
            self.sing(question, callback=self.end)
            self.makeFace("happy_closed.json")
        elif self.message == "no":
            self.sing(question, callback=self.end)
            self.makeFace("pitiful.json")

    def end(self, t):
        self.terminate()