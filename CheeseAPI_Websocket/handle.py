import asyncio, re, json
from typing import TYPE_CHECKING

from CheeseAPI import app
from CheeseLog import logger

from CheeseAPI_Websocket.websocket import websocket

if TYPE_CHECKING:
    from CheeseAPI.protocol import WebsocketProtocol

async def __websocket_connectionHandle(protocol: 'WebsocketProtocol'):
    try:
        pubsub = websocket.async_redis.pubsub()
        await pubsub.subscribe('Websocket_' + protocol.request.path)
        await pubsub.parse_response()
        while True:
            value = (await pubsub.parse_response())[2]

            if re.search(br'"type": "bytes"', value):
                span = re.search(br'"type": "bytes"', value)
                match = value[span.end():-2]
                value = json.loads(value[:span.start() + b'}'])
                value['message'] = match
            else:
                value = json.loads(value)

            if value['sid'] == '*' or protocol.request.headers['Sec-Websocket-Key']  == value or protocol.request.headers['Sec-Websocket-Key'] in value['sid']:
                if value['type'] == 'close':
                    await protocol.func[0].close()
                elif value['type'] in [ 'text', 'bytes' ]:
                    await protocol.func[0].send(value['message'])
    except asyncio.CancelledError:
        await pubsub.close()

async def _websocket_connectionHandle(protocol: 'WebsocketProtocol', app):
    logger.websocket(f'The {protocol.request.headers.get("X-Forwarded-For").split(", ")[0]} connected WEBSOCKET {protocol.request.fullPath}', f'The <cyan>{protocol.request.headers.get("X-Forwarded-For").split(", ")[0]}</cyan> connected <cyan>WEBSOCKET {protocol.request.fullPath}</cyan>')

    protocol.task = asyncio.create_task(__websocket_connectionHandle(protocol))

    await protocol.func[0].connectionHandle(**protocol.func[1])

app.handle._websocket_connectionHandle = _websocket_connectionHandle

def _websocket_disconnectionHandle(protocol: 'WebsocketProtocol', app):
    protocol.func[0].disconnectionHandle(**protocol.func[1])

    if hasattr(protocol, 'task'):
        protocol.task.cancel()

    logger.websocket(f'The {protocol.request.headers.get("X-Forwarded-For").split(", ")[0]} disconnected WEBSOCKET {protocol.request.fullPath}', f'The <cyan>{protocol.request.headers.get("X-Forwarded-For").split(", ")[0]}</cyan> disconnected <cyan>WEBSOCKET {protocol.request.fullPath}</cyan>')

app.handle._websocket_disconnectionHandle = _websocket_disconnectionHandle
