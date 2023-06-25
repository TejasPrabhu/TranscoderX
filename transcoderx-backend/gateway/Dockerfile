FROM python:3.10-alpine

RUN apk update \
    && apk add --no-cache build-base \
    && pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt
COPY . /app

EXPOSE 8080
ENV FLASK_APP=server.py
ENV FLASK_ENV=development
# CMD ["gunicorn", "-b", "0.0.0.0:8080", "--log-level", "debug", "--capture-output", "server:server"]
# CMD ["python3", "server.py"]
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080", "--debugger", "--reload"]



