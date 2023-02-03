import json
import os
from typing import Dict

import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from schemas import Notification

MODULE_TEMPLATE = """  {name}:
    prober: {prober}
    timeout: {timeout}
    http:
      method: {method}
      preferred_ip_protocol: {preferred_ip_protocol}
      headers:
        {headers}
      body:
        {body}
"""

ALERT_RULE_TEMPLATE = """  - name: {group_name}
    rules:
      - alert: {alert_name}
        expr: {expr}
        for: {alert_for}
        labels:
          {labels}
        annotations:
          {annotations}

"""


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


def write_serve(db: Session) -> bool:
    MODULE_PATH = os.path.join(os.getcwd(), "modules")
    RULE_PATH = os.path.join(os.getcwd(), 'rules')

    if not os.path.exists(MODULE_PATH):
        os.makedirs(MODULE_PATH)
    if not os.path.exists(RULE_PATH):
        os.makedirs(RULE_PATH)

    """
    Blackbox Exporter Module 生成
    """

    with open(os.path.join(MODULE_PATH, 'blackbox.yaml'), mode='w+', encoding='UTF-8') as module_file:
        module_file.write("module:\n")
        for module in db.scalars(select(models.ExporterModule).order_by(models.ExporterModule.id)):
            headers = f""
            for index, (k, v) in enumerate(module.headers.items()):
                if index > 0:
                    headers += f"                    {k}: {v}\n"
                else:
                    headers += f"{k}: {v}\n"
            headers = headers.rstrip('\n')
            json_format = f"'{json.dumps(module.body)}'"
            for_write = MODULE_TEMPLATE.format(
                name=module.name,
                prober=module.prober,
                timeout=module.timeout,
                method=module.method,
                preferred_ip_protocol=module.preferred_ip_protocol,
                headers=headers,
                body=json_format
            )
            module_file.write(for_write)

    """
    Prometheus Alert Rules 生成
    """

    with open(os.path.join(RULE_PATH, "custom-rule.yaml"), mode='w+', encoding='UTF-8') as rule_file:
        rule_file.write("groups:\n")
        for group in db.scalars(select(models.AlterGroup).order_by(models.AlterGroup.id)):
            for rule in group.rules:

                labels = f""
                for index, (k, v) in enumerate(rule.labels.items()):
                    if index > 0:
                        labels += f"          {k}: {v}\n"
                    else:
                        labels += f"{k}: {v}\n"
                labels = labels.rstrip('\n')

                annotations = f""
                for index, (k, v) in enumerate(rule.annotations.items()):
                    if index > 0:
                        annotations += f"          {k}: {v}\n"
                    else:
                        annotations += f"{k}: {v}\n"
                annotations = annotations.rstrip('\n')

                for_write = ALERT_RULE_TEMPLATE.format(
                    group_name=group.name,
                    alert_name=rule.name,
                    expr=rule.expr,
                    alert_for=rule.alert_for,
                    labels=labels,
                    annotations=annotations
                )
                rule_file.write(for_write)

    # 热加载配置
    prometheus_reload_url = os.getenv('prometheus_service').join("/-/reload")
    blackbox_reload_url = os.getenv('blackbox_service').join("/-/reload")
    if requests.post(prometheus_reload_url).status_code == 200 and \
            requests.post(blackbox_reload_url).status_code == 200:
        return True
    return False
