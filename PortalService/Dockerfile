FROM python:3.8-slim-buster

WORKDIR /portal

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV OM_GETORDER_URL=/api/v1/orders/
ENV OM_SUBMITORDER_URL=/api/v1/orders/submitOrder
ENV OM_PORT=5003
ENV OM_BASEURL=127.0.0.1

ENV PM_GETPRODUCT_URL=/api/v1/products
ENV PM_PORT=5002
ENV PM_BASEURL=127.0.0.1

COPY . .

CMD [ "opentelemetry-instrument", "python3", "app.py" ]

EXPOSE 5001