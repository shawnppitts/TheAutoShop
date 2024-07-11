FROM python:3.8-slim-buster

WORKDIR /product

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV MONGO_USERNAME=${MONGO_USERNAME}
ENV MONGO_PASSWORD=${MONGO_PASSWORD}
ENV MONGO_CLUSTER=${MONGO_CLUSTER}

COPY . .

CMD [ "opentelemetry-instrument", "python3", "app.py" ]

EXPOSE 5002