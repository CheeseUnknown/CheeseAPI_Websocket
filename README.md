# **CheeseAPI_Websocket**

## **介绍**

一款基于[CheeseAPI](https://github.com/CheeseUnknown/CheeseAPI)的升级款Websocket插件，它能够解决在多worker下websocket的通讯问题，前提是需要引入redis。

## **安装**

系统要求：Unix，例如Linux、Mac等；不支持Windows，若有需要请使用Windows的WSL运行程序。

```bash
pip install CheeseAPI_Websocket
```

## **使用**

CheeseAPI_Websocket是[CheeseAPI](https://github.com/CheeseUnknown/CheeseAPI)的一款插件，它需要依赖于[CheeseAPI](https://github.com/CheeseUnknown/CheeseAPI)才能运行。

默认情况下，它会连接到本地默认端口下的redis db0。

```python
import threading, time

from CheeseAPI import app, WebsocketClient, Response
from CheeseAPI_Websocket import websocket

app.modules.append('CheeseAPI_Websocket') # 加入模块

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

app.run()
```

请注意下列情况：

1. 若传输的数据量过大，请使用原生的send方法，以避免为redis带来过大的负担。

2. 多个不同数据源的服务器连接到同一个redis数据库，会导致websocket消息错乱。

## **Websocket**

```python
from CheeseAPI_Websocket import websocket
```

### **`websocket.host: str = 'localhost'`**

连接的redis host。

### **`websocket.port: int = 6379`**

连接的redis端口。

### **`websocket.db: int = 0`**

连接的redis数据库。

### **`websocket.send(path: str, message: str | bytes | dict | list, sid: str | List[str] | Literal['*'] = '*')`**

发送消息，支持广播。

### **`await websocket.async_send(path: str, message: str | bytes | dict | list, sid: str | List[str] | Literal['*'] = '*')`**

发送消息，支持广播。

## **`websocket.close(path: str, sid: str | List[str] | Literal['*'] = '*')`**

关闭连接，支持广播。

## **`await websocket.async_close(path: str, sid: str | List[str] | Literal['*'] = '*')`**

关闭连接，支持广播。
