import os
from typing import Dict

import requests
from fastapi import FastAPI, HTTPException
from starlette import status

from models import Notification, DingTalkMessage
from log_config import init_logging, logger

app = FastAPI()

init_logging()

ACCESS_TOKEN = os.getenv("DINGTALK_ACCESS_TOKEN")

WEBHOOK_URL = "https://oapi.dingtalk.com/robot/send"


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/webhook")
async def webhook(notification: Notification):
    logger.info("-" * 40)
    logger.info("收到告警")
    logger.info("告警原始信息：")
    logger.info(notification.dict())
    markdown = render_message(notification)
    logger.info(markdown)
    message = DingTalkMessage(markdown=markdown)
    logger.info("钉钉告警信息：")
    logger.info(message.dict())
    payload = {
        "access_token": ACCESS_TOKEN
    }
    response = requests.post(url=WEBHOOK_URL, json=message.dict(), params=payload)
    logger.info("响应信息：")
    logger.info(response.json())
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook Error!")
    logger.info("-" * 40)
    return message.dict()


def render_message(notification: Notification) -> Dict[str, str]:
    alert_status = "已解决" if notification.status == "resolved" else "告警"
    title = f"{alert_status}：{notification.group_labels.get('alertname')}"
    group_label = [i.strip(" ").replace('"', '')
                   for i in notification.group_key[notification.group_key.index(':') + 2: -1].split(',')]
    text = f"**[{alert_status}]**\n\n**通知组**：\n"
    for i in group_label:
        key, val = i.split('=')[0], i.split('=')[1]
        text += f"- **{key}**: {val}\n"
    text += "\n**通知内容**：\n\n"
    for alert in notification.alerts:
        text += f"{alert.annotations.get('summary')} \n> {alert.annotations.get('description')}\n> \n"
        text += f"> **开始时间**：{alert.start_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
    return {"title": title, "text": text}


@app.get("/ping")
async def healthy():
    return {"message": "pong"}
