import requests
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi_pagination.ext.sqlalchemy_future import paginate
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import engine, get_db
from log import init_logging, logger, log
from paginator import Page, Params
from schemas import Notification, DingTalkMessage
from settings import WEBHOOK_URL, ACCESS_TOKEN
from utils import render_message, write_serve

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

init_logging()


@app.get("/")
@log
def root():
    return {"message": "Hello World"}


# Job
@app.post("/job/", response_model=schemas.ScrapeJob)
@log
def create_job(job: schemas.ScrapeJobCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_scrape_job(db, job)
    except SQLAlchemyError as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/job/{job_id}/", response_model=schemas.ScrapeJob)
@log
def get_job(job_id: int, db: Session = Depends(get_db)):
    db_job = crud.get_scrape_job(db, job_id)
    if db_job:
        return db_job
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job Not Found!")


@app.get("/job/", response_model=Page[schemas.ScrapeJob])
@log
def get_jobs(params: Params = Depends(), db: Session = Depends(get_db)):
    return paginate(db, select(models.ScrapeJob).order_by(models.ScrapeJob.id), params)


@app.delete("/job/{job_id}/", response_model=schemas.ScrapeJob)
@log
def delete_job(job_id: int, db: Session = Depends(get_db)):
    try:
        return crud.delete_scrape_job(db, job_id)
    except SQLAlchemyError as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Module
@app.post("/module/", response_model=schemas.ExporterModule)
@log
def create_module(module: schemas.ExporterModuleCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_blackbox_module(db, module)
    except SQLAlchemyError as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/module/{module_id}/", response_model=schemas.ExporterModule)
@log
def get_module(module_id: int, db: Session = Depends(get_db)):
    db_module = crud.get_blackbox_module(db, module_id)
    if db_module:
        return db_module
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module Not Found!")


@app.get("/module/", response_model=Page[schemas.ExporterModule])
@log
def get_modules(params: Params = Depends(), db: Session = Depends(get_db)):
    return paginate(db, select(models.ExporterModule).order_by(models.ExporterModule.id), params)


@app.delete("/module/{module_id}/", response_model=schemas.ExporterModule)
@log
def delete_module(module_id: int, db: Session = Depends(get_db)):
    try:
        return crud.delete_blackbox_module(db, module_id)
    except SQLAlchemyError as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Rule
@app.post("/rule/", response_model=schemas.AlertRule)
@log
def create_rule(rule: schemas.AlertRuleCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_alert_rule(db, rule)
    except SQLAlchemyError as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/rule/{rule_id}/", response_model=schemas.AlertRule)
@log
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    db_rule = crud.get_alert_rule(db, rule_id)
    if db_rule:
        return db_rule
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule Not Found!")


@app.get("/rule/", response_model=Page[schemas.AlertRule])
@log
def get_rules(params: Params = Depends(), db: Session = Depends(get_db)):
    return paginate(db, select(models.AlertRule).order_by(models.AlertRule.id), params)


@app.delete("/rule/{rule_id}/", response_model=schemas.AlertRule)
@log
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    try:
        return crud.delete_alert_rule(db, rule_id)
    except SQLAlchemyError as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# RuleGroup
@app.post("/rule-group/", response_model=schemas.AlterGroup)
@log
def create_rule_group(rule_group: schemas.AlterGroupCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_alert_group(db, rule_group)
    except SQLAlchemyError as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/rule-group/{rule_group_id}/", response_model=schemas.AlterGroup)
@log
def get_rule_group(rule_group_id: int, db: Session = Depends(get_db)):
    db_rule_group = crud.get_alert_group(db, rule_group_id)
    if db_rule_group:
        return db_rule_group
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule Group Not Found!")


@app.get("/rule-group/", response_model=Page[schemas.AlterGroup])
@log
def get_rule_groups(params: Params = Depends(), db: Session = Depends(get_db)):
    return paginate(db, select(models.AlterGroup).order_by(models.AlterGroup.id), params)


@app.delete("/rule-group/{rule_group_id}/", response_model=schemas.AlterGroup)
@log
def delete_rule_group(rule_group_id: int, db: Session = Depends(get_db)):
    try:
        return crud.delete_alert_group(db, rule_group_id)
    except SQLAlchemyError as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# http_sd_config
@app.get("/serve/")
@log
def http_sd_config(db: Session = Depends(get_db)):
    ret = list()
    for i in db.scalars(select(models.ScrapeJob).order_by(models.ScrapeJob.id)):
        ret.append(schemas.HttpSdConfig(targets=[j for j in i.target], labels={"module": i.module.name}))
    return ret


@app.get("/start/")
@log
def gen_serve(db: Session = Depends(get_db)):
    if write_serve(db):
        logger.info("服务生成成功")
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "服务生成成功"})
    logger.error("服务生成失败")
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "服务生成失败"})


# WebHook
@app.post("/webhook")
@log
def webhook(notification: Notification):
    logger.info("告警原始信息：")
    logger.info(notification.dict())
    markdown = render_message(notification)
    message = DingTalkMessage(markdown=markdown)
    logger.info("钉钉告警信息：")
    logger.info(message.dict(by_alias=True))
    payload = {
        "access_token": ACCESS_TOKEN
    }
    response = requests.post(url=WEBHOOK_URL, json=message.dict(by_alias=True), params=payload)
    logger.info("响应信息：")
    logger.info(response.json())
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook Error!")
    logger.info("-" * 40)
    return message.dict()


@app.get("/ping")
@log
def healthy():
    return {"message": "pong"}
