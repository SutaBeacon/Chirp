import json
import subprocess

from WebSocketServer import WebSocketInServer, WebSocketFaceServer, WebSocketControllerServer
from WebSocketServer import wsEvents, wsFaceCommands, wsControllerCommands
from HTTPServer import HTTPServer
from ConsoleLog import normal

wsInServer = WebSocketInServer(8000)
wsFaceServer = WebSocketFaceServer(8001)
wsControllerServer = WebSocketControllerServer(8002)
httpServer = HTTPServer(8003)

wsInServer.start()
wsFaceServer.start()
wsControllerServer.start()
httpServer.start()


while not wsInServer.ready.is_set() and not wsFaceServer.ready.is_set() and not wsControllerServer.ready.is_set():
    pass
normal("Starting browser window...")
subprocess.call(["open", httpServer.address.get()])  # open player
subprocess.call(["open", httpServer.address.get()])  # open controller

try:
    while True:
        jcmd = wsEvents.get(True)
        normal("Received", jcmd)
        cmd = json.loads(jcmd)

        if cmd['cmd'] == 'interaction':
            interactionID = cmd['id']
            normal("Changing to interaction:", interactionID)
            cmd['cmd'] = "face-change"
            wsFaceCommands.put(json.dumps(cmd))
            wsControllerCommands.put(json.dumps(cmd))
except KeyboardInterrupt:
    wsInServer.join()
    wsFaceServer.join()
    wsControllerServer.join()
    httpServer.join()
    pass
