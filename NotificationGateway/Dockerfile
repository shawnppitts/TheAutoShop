FROM python:3.8-slim-buster

WORKDIR /notification

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV API_KEY=e28e5ab6ef8c76b52efb915bc1dd8e6c
ENV API_SECRET=1e1cc18c3de46c8ab8f70ba1bb7e3087
ENV SENDER_MAIL=theautoshopapp@gmail.com

ENV MONGO_USERNAME=admin
ENV MONGO_PASSWORD=0gDB80h5iYxTFMnF
ENV MONGO_CLUSTER=autoshop.8tnzb06.mongodb.net

COPY . .

CMD [ "opentelemetry-instrument", "python3", "app.py" ]

EXPOSE 5004