FROM python:3.6
ENV RUNTIME_PACKAGES="python3"
ENV BUILD_PACKAGES="build-essential python3-dev python3-pip libpq-dev"
WORKDIR /app
COPY . /app
EXPOSE 5050
RUN apt-get update && apt-get install -y $RUNTIME_PACKAGES $BUILD_PACKAGES
RUN pip3 install pipenv==8.3.1 && pipenv install --system --deploy

ENV JWT_SECRET testsecret
ENV SECURITY_USER_NAME admin
ENV SECURITY_USER_PASSWORD secret
ENV NOTIFICATION_API_KEY test_notification_api_key
ENV NOTIFICATION_TEMPLATE_ID test_notification_template_id
ENV SERVICE_ID test_service_id

ENTRYPOINT ["python3"]
CMD ["run.py"]
