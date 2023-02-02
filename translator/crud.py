from typing import Optional, Type

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
import schemas


def get_scrape_job(db: Session, job_id: int) -> Optional[Type[models.ScrapeJob]]:
    db_obj = db.get(models.ScrapeJob, job_id)
    if db_obj:
        return db_obj
    else:
        return None


def create_scrape_job(db: Session, job: schemas.ScrapeJobCreate) -> models.ScrapeJob:
    db_obj = models.ScrapeJob(**job.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_scrape_job(db: Session, job_id: int) -> Type[models.ScrapeJob]:
    db_obj = get_scrape_job(db, job_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
        db.flush()
        return db_obj
    raise IntegrityError(f"delete failed, job {job_id} not found")


def get_blackbox_module(db: Session, module_id: int) -> Optional[Type[models.ExporterModule]]:
    db_obj = db.get(models.ExporterModule, module_id)
    if db_obj:
        return db_obj
    else:
        return None


def create_blackbox_module(db: Session, module: schemas.ExporterModuleCreate) -> models.ExporterModule:
    db_obj = models.ExporterModule(**module.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_blackbox_module(db: Session, module_id: int) -> Type[models.ExporterModule]:
    db_obj = get_blackbox_module(db, module_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
        db.flush()
        return db_obj
    raise IntegrityError(f"delete failed, module {module_id} not found")


def get_alert_rule(db: Session, rule_id: int) -> Optional[Type[models.ExporterModule]]:
    db_obj = db.get(models.AlertRule, rule_id)
    if db_obj:
        return db_obj
    else:
        return None


def create_alert_rule(db: Session, alert: schemas.AlertRuleCreate) -> models.AlertRule:
    stmt = select(models.AlertRule).filter_by(group_id=alert.group_id, expr=alert.expr)
    if db.execute(stmt).first():
        raise IntegrityError(f"Rule {alert.expr} already in group {alert.group_id}!")
    db_obj = models.AlertRule(**alert.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_alert_rule(db: Session, rule_id: int) -> Type[models.ExporterModule]:
    db_obj = get_alert_rule(db, rule_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
        db.flush()
        return db_obj
    raise IntegrityError(f"delete failed, rule {rule_id} not found")


def get_alert_group(db: Session, group_id: int) -> Optional[Type[models.AlterGroup]]:
    db_obj = db.get(models.AlterGroup, group_id)
    if db_obj:
        return db_obj
    else:
        return None


def create_alert_group(db: Session, alert: schemas.AlterGroupCreate) -> models.AlterGroup:
    db_obj = models.AlterGroup(**alert.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_alert_group(db: Session, group_id: int) -> Type[models.AlterGroup]:
    db_obj = get_alert_rule(db, group_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
        db.flush()
        return db_obj
    raise IntegrityError(f"delete failed, group {group_id} not found")
