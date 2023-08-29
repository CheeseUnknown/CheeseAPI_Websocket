import json
from typing import List, Literal

from redis import Redis
from redis.asyncio import Redis as async_Redis
from CheeseType import IPv4, Port, NonNegativeInt
from CheeseAPI import app

class Websocket:
    def __init__(self) -> None:
        self.redis: Redis | None = None
        self.async_redis: async_Redis | None = None

    def init(self, host: IPv4 = app.server.host, port: Port = 6379, db: NonNegativeInt = 0):
        self.redis = Redis(host, port, db)
        self.async_redis = async_Redis(host = host, port = port, db = db)

    def send(self, path: str, message: str | bytes | list | dict, sid: str | List[str] | Literal['*'] = '*'):
        if not self.redis:
            raise ConnectionError('Redis has not be connected')

        if isinstance(message, bytes):
            self.redis.publish('Websocket_' + path, json.dumps({
                'sid': sid,
                'type': 'bytes',
                'message': ''
            }).encode().replace(b'"message": ""', b'"message": "' + message + b'"'))
        else:
            self.redis.publish('Websocket_' + path, json.dumps({
                'sid': sid,
                'type': 'text',
                'message': message
            }))

    async def async_send(self, path: str, message: str | bytes | list | dict, sid: str | List[str] | Literal['*'] = '*'):
        if not self.async_redis:
            raise ConnectionError('Redis has not be connected')

        if isinstance(message, bytes):
            await self.async_redis.publish(f'Websocket_{path}', json.dumps({
                'sid': sid,
                'type': 'bytes',
                'message': ''
            }).encode().replace(b'"message": ""', b'"message": "' + message + '"'))
        else:
            await self.async_redis.publish(f'Websocket_{path}', json.dumps({
                'sid': sid,
                'type': 'text',
                'message': message
            }))

    def close(self, path: str, sid: str | List[str] | Literal['*'] = '*'):
        if not self.redis:
            raise ConnectionError('Redis has not be connected')

        self.redis.publish('Websocket_' + path, json.dumps({
            'sid': sid,
            'type': 'close'
        }))

    async def async_close(self, path: str, sid: str | List[str] | Literal['*'] = '*'):
        if not self.async_redis:
            raise ConnectionError('Redis has not be connected')

        await self.async_redis.publish('Websocket_' + path, json.dumps({
            'sid': sid,
            'type': 'close'
        }))

websocket = Websocket()
