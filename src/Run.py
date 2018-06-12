import json
import subprocess

from WebSocketServer import WebSocketInServer, WebSocketOutServer
from WebSocketServer import wsEvents, wsCommands
from HTTPServer import HTTPServer
from ConsoleLog import normal

wsInServer = WebSocketInServer(8000)
wsOutServer = WebSocketOutServer(8001)
httpServer = HTTPServer(8002)

wsInServer.start()
wsOutServer.start()
httpServer.start()

normal("Starting browser window...")
while not wsInServer.ready.is_set() and not wsOutServer.ready.is_set():
    pass
subprocess.call(["open", httpServer.address.get()])

try:
    while True:
        jcmd = wsEvents.get(True)
        normal("Received", jcmd)
        cmd = json.loads(jcmd)

        if cmd['cmd'] == 'interaction':
            interactionID = cmd['id']
            normal("Changing to interaction:", interactionID)
        wsCommands.put(jcmd)
except KeyboardInterrupt:
    wsInServer.join()
    wsOutServer.join()
    httpServer.join()
    pass
