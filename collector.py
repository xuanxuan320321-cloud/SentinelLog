import asyncio
import os
import redis
import time
from config import LOG_FILE_PATH, REDIS_HOST, REDIS_PORT, REDIS_CHANNEL

class LogCollector:
    def __init__(self):
        self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        self.file_path = LOG_FILE_PATH

    async def tail_file(self):
        """异步读取日志文件末尾"""
        print(f"Starting log collector on {self.file_path}...")
        
        # 如果文件不存在，先创建一个示例日志文件
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                f.write(f"[{time.ctime()}] INFO: SentinelLog Collector started.\n")

        with open(self.file_path, 'r') as f:
            # 移动到文件末尾
            f.seek(0, os.SEEK_END)
            
            while True:
                line = f.readline()
                if not line:
                    await asyncio.sleep(0.1)
                    continue
                
                # 将日志行发送到 Redis 频道
                self.redis_client.publish(REDIS_CHANNEL, line.strip())
                print(f"Collected: {line.strip()}")

async def main():
    collector = LogCollector()
    await collector.tail_file()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Collector stopped.")
