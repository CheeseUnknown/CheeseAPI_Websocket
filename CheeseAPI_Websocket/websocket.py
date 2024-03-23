import json
from typing import List, Literal

from redis import Redis
from redis.asyncio import Redis as async_Redis
from CheeseAPI import app

class Websocket:
    def __init__(self) -> None:
        self.redis: Redis | None = None
        self.async_redis: async_Redis | None = None

    def init(self, host: str = app.server.host, port: int = 6379, db: int = 0):
        self.redis = Redis(host, port, db)
        self.async_redis = async_Redis(host = host, port = port, db = db)

    def send(self, path: str, message: str | bytes | dict | list, sid: str | List[str] | Literal['*'] = '*'):
        if isinstance(message, bytes):
            self.redis.publish('Websocket_' + path, json.dumps({
                'sid': sid,
                'type': 'bytes',
                'message': ''
            }).encode().replace(b'"message": ""', b'"message": "' + message + b'"'))
        elif isinstance(message, str):
            self.redis.publish('Websocket_' + path, json.dumps({
                'sid': sid,
                'type': 'text',
                'message': message
            }))
        else:
            self.redis.publish('Websocket_' + path, json.dumps({
                'sid': sid,
                'type': 'json',
                'message': message
            }))

    async def async_send(self, path: str, message: str | bytes | dict | list, sid: str | List[str] | Literal['*'] = '*'):
        if isinstance(message, bytes):
            await self.async_redis.publish(f'Websocket_{path}', json.dumps({
                'sid': sid,
                'type': 'bytes',
                'message': ''
            }).encode().replace(b'"message": ""', b'"message": "' + message + '"'))
        elif isinstance(message, str):
            await self.async_redis.publish(f'Websocket_{path}', json.dumps({
                'sid': sid,
                'type': 'text',
                'message': message
            }))
        else:
            await self.async_redis.publish(f'Websocket_{path}', json.dumps({
                'sid': sid,
                'type': 'json',
                'message': message
            }))

    def close(self, path: str, sid: str | List[str] | Literal['*'] = '*'):
        self.redis.publish('Websocket_' + path, json.dumps({
            'sid': sid,
            'type': 'close'
        }))

    async def async_close(self, path: str, sid: str | List[str] | Literal['*'] = '*'):
        await self.async_redis.publish('Websocket_' + path, json.dumps({
            'sid': sid,
            'type': 'close'
        }))

websocket = Websocket()
