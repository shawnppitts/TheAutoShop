import os
import json
from dotenv import load_dotenv
import requests
from flask import Flask, request, jsonify,render_template
from prometheus_client import make_wsgi_app, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware

import sys
sys.path.append('../common/')
import logger as logger

app = Flask(__name__)

env_path = "./src/.env"
load_dotenv(env_path)

# For promtheus exporting
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@app.route('/')
@app.route('/home')
def home():  
    return render_template('home.html')
 
@app.route('/order',methods=['GET','POST'])
def order():
    log = {}
    url = "http://" + os.getenv("PM_BASEURL") + ":" + os.getenv("PM_PORT") + os.getenv("PM_GETPRODUCT_URL")
    response = requests.get(url).json()
    product_count = len(response)

    product_gauge = Gauge('product_count', 'Count of products')
    product_gauge.set(product_count)
    
    # POST request to submit order
    if request.method == 'POST':

        log = {}
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
        response = requests.post(url, json=data)
        json_response = response.json()

        log["message"] = f"Order data for item"
        log["request_path"] = url
        log["method"] = "POST"
        log["details"] = json_response
        logger.log(log)

        # POST passes details
        return render_template('orderView.html', data=response.json())
    # GET /orders loads products
    return render_template('order.html', data=response)

@app.route('/viewOrder',methods=['GET','POST'])
def viewOrder():
    log = {}
    if request.method == 'POST':
        log = {}
        log["method"] = "POST"
        orderId = request.form['orderId']        
        url = "http://" + os.getenv("OM_BASEURL") + ":" + os.getenv("OM_PORT") + os.getenv("OM_GETORDER_URL") + orderId
        
        try:
            response = requests.get(url).json()
            print(response)
            log["products"] = response
            logger.log(log)
            return render_template('orderView.html',data=response)
        except:
            log["message"] = f"Could not find order with id: {orderId}"
            log["status"] = 404
            log["orderId"] = orderId
            logger.log(log)
            return render_template('home.html')
    return render_template('view.html')

if __name__ == "__main__":
    app.run(port=5001, host="0.0.0.0")