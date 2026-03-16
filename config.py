# SentinelLog Configuration File

# Path to the log file to monitor
LOG_FILE_PATH = '/var/log/syslog'  # Change this to your target log file

# Redis Connection Settings
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_CHANNEL = 'log_stream'

# Alert Rules Configuration
# pattern: Regex to match in log lines
# threshold: Number of matches to trigger an alert
# time_window: Time window in seconds for the threshold
ALERT_RULES = [
    {
        'name': 'Critical Error Alert',
        'pattern': r'CRITICAL|FATAL|EMERGENCY',
        'threshold': 1,
        'time_window': 60
    },
    {
        'name': 'High Frequency Error',
        'pattern': r'ERROR',
        'threshold': 10,
        'time_window': 60
    },
    {
        'name': 'Authentication Failure',
        'pattern': r'failed password|authentication failure',
        'threshold': 3,
        'time_window': 300
    }
]

# Web Server Settings
WEB_SERVER_HOST = '0.0.0.0'
WEB_SERVER_PORT = 8080
