FROM python:3.10-alpine

RUN apk update \
    && apk add --no-cache build-base ffmpeg \
    && pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt
COPY . /app

CMD ["python3", "consumer.py"]
