FROM python:3.8-slim-buster

WORKDIR /product

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV MONGO_USERNAME=admin
ENV MONGO_PASSWORD=0gDB80h5iYxTFMnF
ENV MONGO_CLUSTER=autoshop.8tnzb06.mongodb.net

COPY . .

CMD [ "opentelemetry-instrument", "python3", "app.py" ]

EXPOSE 5002