import json
from typing import List, Literal

from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from CheeseAPI import app

class Websocket:
    def __init__(self) -> None:
        self.host: str = 'localhost'
        self.port: int = 6379
        self.db: int = 0

        self._redis: Redis | None = None
        self._async_redis: AsyncRedis | None = None

        app.signal.server_beforeStarting.connect(self._init)

    def _init(self):
        self._redis = Redis(self.host, self.port, self.db)
        self._async_redis = AsyncRedis(host = self.host, port = self.port, db = self.db)

    def send(self, path: str, message: str | bytes | dict | list, sid: str | List[str] | Literal['*'] = '*'):
        if isinstance(message, bytes):
            self._redis.publish('Websocket_' + path, json.dumps({
                'sid': sid,
                'type': 'bytes',
                'message': ''
            }).encode().replace(b'"message": ""', b'"message": "' + message + b'"'))
        elif isinstance(message, str):
            self._redis.publish('Websocket_' + path, json.dumps({
                'sid': sid,
                'type': 'text',
                'message': message
            }))
        else:
            self._redis.publish('Websocket_' + path, json.dumps({
                'sid': sid,
                'type': 'json',
                'message': message
            }))

    async def async_send(self, path: str, message: str | bytes | dict | list, sid: str | List[str] | Literal['*'] = '*'):
        if isinstance(message, bytes):
            await self._async_redis.publish(f'Websocket_{path}', json.dumps({
                'sid': sid,
                'type': 'bytes',
                'message': ''
            }).encode().replace(b'"message": ""', b'"message": "' + message + '"'))
        elif isinstance(message, str):
            await self._async_redis.publish(f'Websocket_{path}', json.dumps({
                'sid': sid,
                'type': 'text',
                'message': message
            }))
        else:
            await self._async_redis.publish(f'Websocket_{path}', json.dumps({
                'sid': sid,
                'type': 'json',
                'message': message
            }))

    def close(self, path: str, sid: str | List[str] | Literal['*'] = '*'):
        self._redis.publish('Websocket_' + path, json.dumps({
            'sid': sid,
            'type': 'close'
        }))

    async def async_close(self, path: str, sid: str | List[str] | Literal['*'] = '*'):
        await self._async_redis.publish('Websocket_' + path, json.dumps({
            'sid': sid,
            'type': 'close'
        }))

websocket = Websocket()
