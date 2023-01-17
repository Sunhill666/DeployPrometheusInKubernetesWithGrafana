FROM python:3.9.15-alpine
WORKDIR /project

EXPOSE 8000

ADD . /project

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "main:app"]