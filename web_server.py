import asyncio
import websockets
import redis
import json
from config import REDIS_HOST, REDIS_PORT

class SentinelWebServer:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        self.connected_clients = set()

    async def register(self, websocket):
        self.connected_clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.connected_clients)}")

    async def unregister(self, websocket):
        self.connected_clients.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.connected_clients)}")

    async def ws_handler(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                # 可以在这里处理来自客户端的消息
                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def redis_listener(self):
        """监听 Redis 中的告警并广播给所有 WebSocket 客户端"""
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe('alerts')
        print("Listening for alerts in Redis...")
        
        while True:
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                alert_data = message['data']
                if self.connected_clients:
                    await asyncio.wait([client.send(alert_data) for client in self.connected_clients])
            await asyncio.sleep(0.1)

    def run(self):
        start_server = websockets.serve(self.ws_handler, self.host, self.port)
        print(f"WebSocket server started on ws://{self.host}:{self.port}")
        
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_server)
        loop.create_task(self.redis_listener())
        loop.run_forever()

if __name__ == "__main__":
    server = SentinelWebServer()
    try:
        server.run()
    except KeyboardInterrupt:
        print("Server stopped.")
