# Dockerfile specifically for kubernetes
FROM python:3.9-slim

RUN apt update && apt install -y build-essential curl gunicorn
RUN pip install pipenv

WORKDIR /app

COPY . /app
RUN pipenv install --deploy --system
RUN pip3 install -r requirements.txt.dm
EXPOSE 80
CMD ["./startup.sh"]

