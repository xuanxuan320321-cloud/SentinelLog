import redis
import re
import json
import time
from collections import deque
from config import REDIS_HOST, REDIS_PORT, REDIS_CHANNEL, ALERT_RULES

class LogProcessor:
    def __init__(self):
        self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe(REDIS_CHANNEL)
        
        # 用于存储每个规则的匹配时间戳，以便计算阈值
        self.match_history = {rule['name']: deque() for rule in ALERT_RULES}

    def process_line(self, line):
        """根据规则处理每一行日志"""
        current_time = time.time()
        
        for rule in ALERT_RULES:
            if re.search(rule['pattern'], line, re.IGNORECASE):
                rule_name = rule['name']
                self.match_history[rule_name].append(current_time)
                
                # 清理超出时间窗口的历史记录
                while self.match_history[rule_name] and self.match_history[rule_name][0] < current_time - rule['time_window']:
                    self.match_history[rule_name].popleft()
                
                # 检查是否达到告警阈值
                if len(self.match_history[rule_name]) >= rule['threshold']:
                    alert_msg = {
                        'type': 'ALERT',
                        'rule': rule_name,
                        'message': f"Threshold reached: {len(self.match_history[rule_name])} matches in {rule['time_window']}s",
                        'log_snippet': line,
                        'timestamp': time.ctime()
                    }
                    # 发布告警到告警频道
                    self.redis_client.publish('alerts', json.dumps(alert_msg))
                    print(f"ALERT: {rule_name} triggered!")

    def run(self):
        print("Log processor started, listening for logs...")
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                line = message['data']
                self.process_line(line)

if __name__ == "__main__":
    processor = LogProcessor()
    try:
        processor.run()
    except KeyboardInterrupt:
        print("Processor stopped.")
