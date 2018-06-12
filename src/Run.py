import json
import subprocess
from queue import Empty

from WebSocketServer import WebSocketInServer
from WebSocketServer import WebSocketFaceServer, WebSocketControllerServer
from WebSocketServer import wsEvents, wsFaceCommands, wsControllerCommands
from HTTPServer import HTTPServer
from ConsoleLog import normal
from InteractionController import InteractionController

wsInServer = WebSocketInServer(8000)
wsFaceServer = WebSocketFaceServer(8001)
wsControllerServer = WebSocketControllerServer(8002)
httpServer = HTTPServer(8003)

interactionController = InteractionController()

wsInServer.start()
wsFaceServer.start()
wsControllerServer.start()
httpServer.start()
interactionController.start()


while not wsInServer.ready.is_set() and not wsFaceServer.ready.is_set() and not wsControllerServer.ready.is_set():
    pass
normal("Starting browser window...")
subprocess.call(["open", httpServer.address.get()])  # open player
subprocess.call(["open", httpServer.address.get()])  # open controller


def CheckWebsocketEvents(interactionController):
    try:
        evt = wsEvents.get(False)
        evt = json.loads(evt)
        evt["src"] = "websocket"
        interactionController.message(evt)
    except Empty:
        pass


def CheckSerialEvents(interactionController):
    pass


def DispatchCommands(interactionController):

    def _dispatch(cmd):
        if cmd['dest'] == 'face':
            wsFaceCommands.put(cmd['content'])
        elif cmd['dest'] == 'controller':
            wsControllerCommands.put(cmd['content'])

    while True:
        try:
            cmd = interactionController.commands.get(False)
            _dispatch(cmd)
        except Empty:
            break


try:
    while True:
        CheckWebsocketEvents(interactionController)
        CheckSerialEvents(interactionController)

        DispatchCommands(interactionController)

except KeyboardInterrupt:
    interactionController.terminate()
    wsInServer.join()
    wsFaceServer.join()
    wsControllerServer.join()
    httpServer.join()
    pass
