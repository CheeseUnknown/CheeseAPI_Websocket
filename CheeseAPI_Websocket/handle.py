import asyncio, re, json
from typing import TYPE_CHECKING

from CheeseAPI import app, async_doFunc
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
                match = re.search(br'"message": ".*"', value).group()[9:-1]
                value = json.loads(value.replace(br', "message": "' + match + br'"', b''))
                value['message'] = match
            else:
                value = json.loads(value)

            if value['sid'] == '*' or protocol.request.header['Sec-Websocket-Key']  == value or protocol.request.header['Sec-Websocket-Key'] in value['sid']:
                if value['type'] == 'close':
                    await protocol.func[0].close()
                elif value['type'] in [ 'text', 'bytes' ]:
                    await protocol.func[0].send(value['message'])
    except asyncio.CancelledError:
        await pubsub.close()

async def _websocket_connectionHandle(protocol: 'WebsocketProtocol', app):
    logger.websocket(f'The {protocol.request.header.get("X-Forwarded-For").split(", ")[0]} connected WEBSOCKET {protocol.request.fullPath}', f'The <cyan>{protocol.request.header.get("X-Forwarded-For").split(", ")[0]}</cyan> connected <cyan>WEBSOCKET {protocol.request.fullPath}</cyan>')

    protocol.task = asyncio.create_task(__websocket_connectionHandle(protocol))

    await async_doFunc(protocol.func[0].connectionHandle, protocol.func[1])

app.handle._websocket_connectionHandle = _websocket_connectionHandle

async def _websocket_disconnectionHandle(protocol: 'WebsocketProtocol', app):
    await async_doFunc(protocol.func[0].disconnectionHandle, protocol.func[1])

    protocol.task.cancel()

    logger.websocket(f'The {protocol.request.header.get("X-Forwarded-For").split(", ")[0]} disconnected WEBSOCKET {protocol.request.fullPath}', f'The <cyan>{protocol.request.header.get("X-Forwarded-For").split(", ")[0]}</cyan> disconnected <cyan>WEBSOCKET {protocol.request.fullPath}</cyan>')

app.handle._websocket_disconnectionHandle = _websocket_disconnectionHandle
