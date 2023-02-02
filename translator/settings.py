import os

env = os.getenv('APP_ENV', 'dev')

WEBHOOK_URL = "https://oapi.dingtalk.com/robot/send"

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
ACCESS_TOKEN = os.getenv("DINGTALK_ACCESS_TOKEN")
