import websockets
import asyncio
import time

async def consumer_handler(websocket, path):
    print("consumer")
    while True:
        message = await websocket.recv()
        print(message)

async def producer_handler(websocket, path):
    print("producer")
    while True:
        message = "hello"
        await websocket.send(message)
        time.sleep(1)

async def handler(websocket, path):
    consumer_task = asyncio.ensure_future(
        consumer_handler(websocket, path))
    producer_task = asyncio.ensure_future(
        producer_handler(websocket, path))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()

asyncio.get_event_loop().run_until_complete(
    websockets.serve(handler, 'localhost', 8765))
asyncio.get_event_loop().run_forever()
