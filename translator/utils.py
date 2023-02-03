from typing import Dict

from sqlalchemy.orm import Session

from translator.schemas import Notification


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


def write_serve(db: Session, namespace: str) -> bool:
    """
    Blackbox Exporter Module 生成
    """
    return True
