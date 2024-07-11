FROM python:3.8-slim-buster

WORKDIR /order

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV NG_URL=/api/v1/email/sendMail
ENV NG_PORT=5004
ENV NG_BASEURL=127.0.0.1

ENV MONGO_USERNAME=${MONGO_USERNAME}
ENV MONGO_PASSWORD=${MONGO_PASSWORD}
ENV MONGO_CLUSTER=${MONGO_CLUSTER}

COPY . .

CMD [ "opentelemetry-instrument", "python3", "app.py" ]

EXPOSE 5003