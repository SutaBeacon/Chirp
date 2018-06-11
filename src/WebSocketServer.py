import asyncio
import websockets
from multiprocessing import Process, Queue
from queue import Empty

from ConsoleLog import normal, success


wsEvents = Queue()
wsCommands = Queue()


async def input_handler(websocket, path):
    while True:
        evt = await websocket.recv()
        wsEvents.put(evt)


async def output_handler(websocket, path):
    while True:
        cmd = wsCommands.get(True)
        normal("Got message:", cmd)
        await websocket.send(cmd)


class WebSocketOutServer(Process):

    def __init__(self, port):
        super(WebSocketOutServer, self).__init__()
        self.port = port

    def run(self):
        self.start_server = websockets.serve(output_handler, 'localhost', self.port)

        asyncio.get_event_loop().run_until_complete(self.start_server)
        normal("Starting WebSocket Server at", self.port)
        success("WebSocket server started.")
        loop = asyncio.get_event_loop()
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            normal("Shutting down WebSocket server.")
            loop.stop()
            loop.close()
            success("Websocket server shut down.")


class WebSocketInServer(Process):

    def __init__(self, port):
        super(WebSocketInServer, self).__init__()
        self.port = port

    def run(self):
        self.start_server = websockets.serve(input_handler, 'localhost', self.port)

        asyncio.get_event_loop().run_until_complete(self.start_server)
        normal("Starting WebSocket Server at", self.port)
        success("WebSocket server started.")
        loop = asyncio.get_event_loop()
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            normal("Shutting down WebSocket server.")
            loop.stop()
            loop.close()
            success("Websocket server shut down.")


if __name__ == '__main__':
    wsServer = WebSocketOutServer(8000)
    wsServer.start()
    wsServer.join()
