# **CheeseAPI_Websocket**

## **介绍**

一款基于[CheeseAPI](https://github.com/CheeseUnknown/CheeseAPI)的升级款Websocket插件，它能够解决在多worker下websocket的通讯问题，前提是需要引入redis。

## **安装**

目前仅保证支持3.11及以上的python。

```bash
pip install CheeseAPI_Websocket
```

对应CheeseAPI版本：

| 版本 | CheeseAPI版本 |
| - | - |
| 1.0.3 | 1.3.* |
| 1.0.2 | 1.2.* |
| 1.0.1 | 1.1.* |
| 1.0.0 | 1.0.* |

## **使用**

CheeseAPI_Websocket是[CheeseAPI](https://github.com/CheeseUnknown/CheeseAPI)的一款插件，它需要依赖于[CheeseAPI](https://github.com/CheeseUnknown/CheeseAPI)才能运行。

```python
import threading, time

from CheeseAPI import app, WebsocketClient, Response
from CheeseAPI_Websocket import websocket

app.modules.append('CheeseAPI_Websocket') # 加入模块

websocket.init() # 初始化redis连接

@app.route.websocket('/')
class Test(WebsocketClient):
    ...

# 创建一个线程，在非协程环境下发送Websocket
@app.handle.server_afterStartingHandle
def test():
    def test0():
        while True:
            websocket.send('/', '你好')
            time.sleep(1)
threading.Thread(target = test, daemon = True).start()

# 在协程环境下发送Websocket
@app.route.post('/websocket')
async def test1():
    await websocket.async_send('/', '世界')
    return Response()

if __name__ == '__main__':
    app.run()
```

若传输的数据量过大，请使用原生的send方法，以避免为redis带来过大的负担。

## **Websocket**

```python
from CheeseAPI_Websocket import websocket
```

### **`websocket.init(host: IPv4 = app.server.host, port: Port = 6379, db: NonNegativeInt = 0)`**

初始化redis连接。

### **`websocket.send(path: str, message: str | bytes | dict | list, sid: str | List[str] | Literal['*'] = '*')`**

发送消息，支持广播。

### **`await websocket.async_send(path: str, message: str | bytes | dict | list, sid: str | List[str] | Literal['*'] = '*')`**

发送消息，支持广播。

## **`websocket.close(path: str, sid: str | List[str] | Literal['*'] = '*')`**

关闭连接，支持广播。

## **`await websocket.async_close(path: str, sid: str | List[str] | Literal['*'] = '*')`**

关闭连接，支持广播。
