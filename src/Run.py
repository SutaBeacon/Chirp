import json
import subprocess

from WebSocketServer import WebSocketInServer, WebSocketOutServer, wsEvents, wsCommands
from HTTPServer import HTTPServer
from ConsoleLog import normal, success

wsInServer = WebSocketInServer(8000)
wsOutServer = WebSocketOutServer(8001)
httpServer = HTTPServer(8002)

wsInServer.start()
wsOutServer.start()
httpServer.start()

normal("Starting browser window...")
subprocess.call(["open", httpServer.address.get()])

try:
    while True:
        cmd = wsEvents.get(True)
        success(cmd)
        cmd = json.loads(cmd)

        if cmd['cmd'] == 'interaction':
            interactionID = cmd['id']
            normal("Changing to interaction:", interactionID)
        # wsCommands.put(cmd)
except KeyboardInterrupt:
    wsInServer.join()
    wsOutServer.join()
    httpServer.join()
    pass
