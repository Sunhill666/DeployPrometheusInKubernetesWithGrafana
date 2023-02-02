from enum import Enum
from typing import List

from sqlalchemy import Column, String, JSON, Enum as SQLEnum, Text, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from database import Base


class ProberEnum(str, Enum):
    http = "http"


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class IPProtocol(str, Enum):
    ip4 = "ip4"
    ip6 = "ip6"


class ExporterModule(Base):
    __tablename__ = "exporter_modules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    jobs: Mapped[List["ScrapeJob"]] = relationship(back_populates="module")
    name = Column(String, unique=True, index=True)
    timeout = Column(String)

    prober = Column(SQLEnum(ProberEnum))
    method = Column(SQLEnum(HTTPMethod))
    headers = Column(JSON, nullable=True)
    body = Column(JSON, nullable=True)
    preferred_ip_protocol = Column(SQLEnum(IPProtocol))


class ScrapeJob(Base):
    __tablename__ = "scrape_configs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("exporter_modules.id"))
    module: Mapped["ExporterModule"] = relationship(back_populates="jobs")
    target = Column(JSON)


class AlterGroup(Base):
    __tablename__ = "alert_groups"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    rules: Mapped[List["AlertRule"]] = relationship(back_populates="group")


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("alert_groups.id"))
    group: Mapped["AlterGroup"] = relationship(back_populates="rules")
    name = Column(String)
    expr = Column(Text, unique=True)
    alert_for = Column(String)
    labels = Column(JSON)
    annotations = Column(JSON)
