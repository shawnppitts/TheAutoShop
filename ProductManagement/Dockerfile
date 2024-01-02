FROM python:3.8-slim-buster

WORKDIR /product

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV DB_HOST=127.0.0.1
ENV BUCKET=db_pm
ENV COLLECTION=_default
ENV SCOPE=_default
ENV USERNAME=admin
ENV PASSWORD=TheShop2023

COPY . .

CMD [ "python3", "app.py" ]

EXPOSE 5002