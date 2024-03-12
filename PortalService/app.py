import os
import json
from dotenv import load_dotenv
import requests
from flask import Flask, request, jsonify,render_template
from prometheus_client import make_wsgi_app, Gauge, Counter, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter
)

def log(message):
  url = "https://listener.logz.io:8071?token=nAinGBdvDFnhzkvxkgypQfPHdSbtpJVD&type=autoshop"
  payload = json.dumps(message)
  headers = {
    'Content-Type': 'application/json'
  }
  response = requests.request("POST", url, headers=headers, data=payload)

app = Flask(__name__)

env_path = "./src/.env"
load_dotenv(env_path)

# For promtheus exporting
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

request_counter = Counter(
    'autoshop_request_count',
    'Autoshop Request Count',
    ['method', 'endpoint', 'status']
)

@app.route('/')
@app.route('/home')
def home():
    print("hit endpoint /home")
    # Add support for otel metrics
    autoshop_requests_counter.add(1, {"path": "/home"})
    print("metric counter +1")
    request_counter.labels('GET', '/', 200).inc(1)
    return render_template('home.html')
 
@app.route('/order',methods=['GET','POST'])
def order():
    request_counter.labels('GET', '/order', 200).inc(1)
    payload = {}
    url = "http://" + os.getenv("PM_BASEURL") + ":" + os.getenv("PM_PORT") + os.getenv("PM_GETPRODUCT_URL")
    response = requests.get(url).json()

    product_count = len(response)
    log(payload)
    
    # POST request to submit order
    if request.method == 'POST':
        request_counter.labels('POST', '/order', 200).inc(1)
        payload = {}
        data={}
        orderItems = []
        contact = {}
        for item in response:
            orderItem ={}
            if int(request.form[item['productId']]):
                orderItem["quantity"] = int(request.form[item['productId']])           
                orderItem["productName"] = item["productName"]
                orderItem["price"] = item["price"]
                orderItem["productId"] = item["productId"]
                orderItem["tax"] = item["tax"]
                orderItems.append(orderItem)

        contact["name"] = request.form["name"]
        contact["address"] = request.form["address"]
        contact["emailId"] = request.form["email"]
        contact["phone"] = request.form["mobile"]

        data["orderItems"] = orderItems
        data["contact"] = contact


        url = "http://" + os.getenv("OM_BASEURL") + ":" + os.getenv("OM_PORT") + os.getenv("OM_SUBMITORDER_URL")
        payload["message"] = f"pre submission to {url}"
        payload["payload"] = json.dumps(data)
        payload["contact"] = data["contact"]
        log(payload)

        response = requests.post(url, json=data)
        json_response = response.json()

        payload = {}
        payload["message"] = f"Order data for item"
        payload["request_path"] = url
        payload["method"] = "POST"
        payload["details"] = json_response
        log(payload)

        # POST passes details
        return render_template('orderView.html', data=response.json())
    # GET /orders loads products
    return render_template('order.html', data=response)

@app.route('/viewOrder',methods=['GET','POST'])
def viewOrder():
    request_counter.labels('GET', '/viewOrder', 200).inc(1)
    payload = {}
    if request.method == 'POST':
        request_counter.labels('POST', '/viewOrder', 200).inc(1)
        payload = {}
        payload["method"] = "POST"
        orderId = request.form['orderId']        
        url = "http://" + os.getenv("OM_BASEURL") + ":" + os.getenv("OM_PORT") + os.getenv("OM_GETORDER_URL") + orderId
        
        try:
            response = requests.get(url).json()
            print(response)
            payload["products"] = response
            log(payload)
            return render_template('orderView.html',data=response)
        except:
            payload["message"] = f"Could not find order with id: {orderId}"
            payload["status"] = 404
            payload["orderId"] = orderId
            payload["log_level"] = "ERROR"
            log(payload)
            return render_template('home.html')
    return render_template('view.html')

if __name__ == "__main__":
    exporter = OTLPMetricExporter(
        endpoint="http://logzio-k8s-telemetry-otel-collector.monitoring.svc.cluster.local:4318/v1/metrics"
    )
    otlp_reader = PeriodicExportingMetricReader(exporter)
    # console_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())

    otlp_provider = MeterProvider(metric_readers=[otlp_reader])
    # console_provider = MeterProvider(metric_readers=[console_reader])

    metrics.set_meter_provider(otlp_provider)
    # metrics.set_meter_provider(console_provider)
    # Creates a meter from the global meter provider
    meter = metrics.get_meter("autoshop.meter")

    autoshop_requests_counter = meter.create_counter(
        name="autoshop_portal",
        description="number of requests",
        unit="1"
    )
    print(autoshop_requests_counter)
    # controller = PushController(meter, collector_exporter, 10000)
    app.run(port=5001, host="0.0.0.0", debug=True)