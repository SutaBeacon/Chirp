import asyncio
import websockets
from multiprocessing import Process, Queue, Event

from ConsoleLog import normal, success, warning


wsEvents = Queue()
wsFaceCommands = Queue()
wsControllerCommands = Queue()


async def input_handler(websocket, path):
    normal("Incoming connection established.")
    while True:
        try:
            evt = await websocket.recv()
        except websockets.ConnectionClosed:
            warning("Incoming connection closed.")
            break
        wsEvents.put(evt)


async def face_handler(websocket, path):
    normal("Outgoing connection established.")
    while True:
        cmd = wsFaceCommands.get(True)
        try:
            await websocket.send(cmd)
        except websockets.ConnectionClosed:
            warning("Outgoing connection closed.")
            break


async def controller_handler(websocket, path):
    normal("Outgoing connection established.")
    while True:
        cmd = wsControllerCommands.get(True)
        try:
            await websocket.send(cmd)
        except websockets.ConnectionClosed:
            warning("Outgoing connection closed.")
            break


class WebSocketControllerServer(Process):

    ready = Event()

    def __init__(self, port):
        super(WebSocketControllerServer, self).__init__()
        self.port = port
        self.ready.clear()

    def run(self):
        self.start_server = websockets.serve(controller_handler, '0.0.0.0', self.port)

        asyncio.get_event_loop().run_until_complete(self.start_server)
        normal("Outgoing websocket server started at", self.port)
        loop = asyncio.get_event_loop()
        try:
            self.ready.set()
            loop.run_forever()
        except KeyboardInterrupt:
            loop.stop()
            loop.close()
            normal("Outgoing websocket server shut down.")


class WebSocketFaceServer(Process):

    ready = Event()

    def __init__(self, port):
        super(WebSocketFaceServer, self).__init__()
        self.port = port
        self.ready.clear()

    def run(self):
        self.start_server = websockets.serve(face_handler, '0.0.0.0', self.port)

        asyncio.get_event_loop().run_until_complete(self.start_server)
        normal("Outgoing websocket server started at", self.port)
        loop = asyncio.get_event_loop()
        try:
            self.ready.set()
            loop.run_forever()
        except KeyboardInterrupt:
            loop.stop()
            loop.close()
            normal("Outgoing websocket server shut down.")


class WebSocketInServer(Process):

    ready = Event()

    def __init__(self, port):
        super(WebSocketInServer, self).__init__()
        self.port = port
        self.ready.clear()

    def run(self):
        self.start_server = websockets.serve(input_handler, '0.0.0.0', self.port)

        asyncio.get_event_loop().run_until_complete(self.start_server)
        normal("Outgoing websocket server started at", self.port)
        loop = asyncio.get_event_loop()
        try:
            self.ready.set()
            loop.run_forever()
        except KeyboardInterrupt:
            loop.stop()
            loop.close()
            normal("Incoming websocket server shut down.")



if __name__ == '__main__':
    wsServer = WebSocketInServer(8765)
    wsServer.start()
    wsServer.join()
