from datetime import datetime
from typing import List, Dict

from pydantic import BaseModel, Field


class Alert(BaseModel):
    status: str
    labels: Dict[str, str] = dict()
    annotations: Dict[str, str] = dict()
    start_at: datetime = Field(alias="startsAt")
    end_at: datetime = Field(alias="endsAt")
    generator_url: str = Field(alias="generatorURL")
    fingerprint: str


class Notification(BaseModel):
    version: str
    receiver: str
    status: str
    truncated_alerts: int = Field(alias="truncatedAlerts", default=0)
    group_key: str = Field(alias="groupKey")
    alerts: List[Alert] = list()
    group_labels: Dict[str, str] = Field(alias="groupLabels")
    common_labels: Dict[str, str] = Field(alias="commonLabels")
    common_annotations: Dict[str, str] = Field(alias="commonAnnotations")
    external_url: str = Field(alias="externalURL")


class DingTalkMessage(BaseModel):
    msgtype: str = "markdown"
    markdown: Dict[str, str]
