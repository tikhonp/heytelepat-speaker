import websockets
import asyncio
import json


async def f():
    url = 'ws://127.0.0.1:8000/ws/speakerapi/init/checkauth/'

    try:
        async with websockets.connect(url) as ws:
            await ws.send(json.dumps({"token": "SSyWoMO0B9xUvh71k4re4Q"}))
            msg = await ws.recv()
            return msg
    except websockets.exceptions.ConnectionClosedError:
        return None

m = asyncio.get_event_loop().run_until_complete(f())
print(m)
