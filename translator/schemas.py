from datetime import datetime
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field

from models import ProberEnum, HTTPMethod, IPProtocol


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
    msg_type: str = Field(default="markdown", alias="msgtype")
    markdown: Dict[str, str]

    class Config:
        allow_population_by_field_name = True


class ExporterModuleCreate(BaseModel):
    name: str
    timeout: str

    prober: ProberEnum = ProberEnum.http
    method: HTTPMethod = HTTPMethod.GET
    headers: Optional[Dict[str, Any]]
    body: Optional[Dict[str, Any]]
    preferred_ip_protocol: IPProtocol = IPProtocol.ip4


class ExporterModule(BaseModel):
    id: int
    name: str
    timeout: str

    prober: ProberEnum = ProberEnum.http
    method: HTTPMethod = HTTPMethod.GET
    headers: Optional[Dict[str, Any]]
    body: Optional[Dict[str, Any]]
    preferred_ip_protocol: IPProtocol = IPProtocol.ip4

    class Config:
        orm_mode = True


class ScrapeJobCreate(BaseModel):
    target: List[str]
    # ExporterModule ID
    module_id: int


class ScrapeJob(BaseModel):
    id: int
    target: List[str]
    # ExporterModule ID
    module: ExporterModule

    class Config:
        orm_mode = True


class AlertRuleCreate(BaseModel):
    group_id: int
    name: str
    expr: str
    alert_for: str
    labels: Dict[str, Any]
    annotations: Dict[str, Any]


class AlertRule(BaseModel):
    id: int
    group_id: int
    name: str
    expr: str
    alert_for: str
    labels: Dict[str, Any]
    annotations: Dict[str, Any]

    class Config:
        orm_mode = True


class AlterGroupCreate(BaseModel):
    name: str


class AlterGroup(BaseModel):
    id: int
    name: str
    rules: List[AlertRule]

    class Config:
        orm_mode = True


class HttpSdConfig(BaseModel):
    targets: List[str]
    labels: Dict[str, str]
