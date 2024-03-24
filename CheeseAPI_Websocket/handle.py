import asyncio, re, json, types
from typing import TYPE_CHECKING

from CheeseAPI import app
from CheeseAPI.handle import Handle
from CheeseLog import logger

from CheeseAPI_Websocket.websocket import websocket

if TYPE_CHECKING:
    from CheeseAPI.protocol import WebsocketProtocol

async def _websocket_connection(protocol: 'WebsocketProtocol'):
    try:
        pubsub = websocket.async_redis.pubsub()
        await pubsub.subscribe('Websocket_' + protocol.request.path)
        await pubsub.parse_response()
        while True:
            value = (await pubsub.parse_response())[2]

            if re.search(br'"type": "bytes"', value):
                span = re.search(br'"message": "', value)
                match = value[span.end():-2]
                value = json.loads(value[:span.start() - 2] + b'}')
                value['message'] = match
            else:
                value = json.loads(value)

            if value['sid'] == '*' or protocol.request.headers['Sec-Websocket-Key']  == value['sid'] or protocol.request.headers['Sec-Websocket-Key'] in value['sid']:
                if value['type'] == 'close':
                    await protocol.server.close()
                elif value['type'] in [ 'text', 'bytes' ]:
                    await protocol.server.send(value['message'])
                elif value['type'] == 'json':
                    await protocol.server.send(json.dumps(value['message']))
    except asyncio.CancelledError:
        await pubsub.close()

async def websocket_connection(self: 'Handle', protocol: 'WebsocketProtocol'):
    for text in self._app._text.websocket_connection(protocol):
        logger.websocket(text[0], text[1])
    protocol.task = asyncio.create_task(_websocket_connection(protocol))

app._handle.websocket_connection = types.MethodType(websocket_connection, app._handle)

async def websocket_disconnection(self: 'Handle', protocol: 'WebsocketProtocol'):
    protocol.task.cancel()

    await protocol.server.disconnection(**{
        'request': protocol.request,
        **protocol.kwargs
    })

    for text in self._app._text.websocket_disconnection(protocol):
        logger.websocket(text[0], text[1])

app._handle.websocket_disconnection = types.MethodType(websocket_disconnection, app._handle)
