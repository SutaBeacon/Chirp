from Interaction import Interaction
from data.phrases import question


class InitiateGame (Interaction):

    def setup(self):
        # TODO: 换上真正的音乐和脸
        self.registerHandler("findFace", self.findFace)
        self.registerHandler("foundFace", self.foundFace)

        self.makeFace("Happy.json")
        self.sing(question, callback=self.findFace)

    def findFace(self, t):
        self.makeFace("Happy.json")
        self.sing(question, callback=self.foundFace)

    def foundFace(self, t):
        print("Done")
        self.terminate()