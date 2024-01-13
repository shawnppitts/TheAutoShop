import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request
from pymongo.mongo_client import MongoClient
from flask_restx import Api, Resource, fields
from mailjet_rest import Client

app = Flask(__name__)

# env_path = "./src/.env"
# load_dotenv(env_path)
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")
MONGO_CLUSTER = os.environ.get("MONGO_CLUSTER")

senderMail = os.getenv("SENDER_MAIL")
mailjet = Client(auth=(os.getenv("API_KEY"), os.getenv("API_SECRET")), version='v3.1')
api = Api(app)

product_ns = api.namespace("api/v1/email", "Send Email")

emailInsert = api.model(
    "emailInsert",
    {
        "orderId": fields.String(required=True, description="Order ID"),
        "name": fields.String(required=True, description="Name of Customer"),
        "mailId": fields.String(required=True, description="Mail Id of customer"),
        "totalCost" : fields.Float(required=True, description="Total cost of order"),
    },
)

emailResponse = api.model(
    "emailResponse",
    {
        "id": fields.String(required=True, description="Audit for email sent"),
        "orderId": fields.String(required=True, description="Order ID"),
        "mailId": fields.String(required=True, description="Mail Id of customer"),
        "status" : fields.String(required=True, description="Email Status"),
        "deliveredAt" : fields.String(required=True, description="Time email is delivered"),
        "statusCode" : fields.Integer(required=True, description="Status code of SMTP")
    },
)


@product_ns.route("/sendMail")
class Email(Resource):
    # tag::post[]
    @product_ns.doc(
        "Send Email",
        reponses={200: "Success", 500: "Unexpected Error"},
    )
    @product_ns.expect(emailInsert, validate=True)
    @product_ns.marshal_with(emailResponse)
    def post(self):
        db = client["db_ng"]
        collection = db["emails"]
        
        reqData = request.json
        data = {
                'Messages': [
                    {
                        "From": {
                            "Email": senderMail,
                            "Name": senderMail
                        },
                        "To": [
                            {
                                "Email": reqData["mailId"],
                                "Name": reqData["name"]
                            }
                        ],
                        "Subject": "Order Confirmation from Auto Shop",
                        "TextPart": f"Your Order {reqData['orderId']} successfully placed !",
                        "HTMLPart": f"<h3>Dear {reqData['name']} , Your order {reqData['orderId']} is successfully placed and the total amount of the order is {reqData['totalCost']} . Thank you for shopping with The Auto Shop!"
                    }
                ]
            }
        response = {}
        rep = mailjet.send.create(data=data)
        if rep.status_code==200:
            response["status"] = "SUCCESS"
            response["deliveredAt"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        else:
            response["status"] = "FAILURE"
            response["deliveredAt"] = None
        id = uuid.uuid4().__str__()
        response["id"] = id
        response["mailId"] = reqData["mailId"]
        response["orderId"] = reqData["orderId"]
        response["statusCode"] = rep.status_code
        try :
            print(data)
            print(response)
            collection.insert_one(data)
            return response, 202
        except Exception as e:
            return f"Unexpected error: {e}", 500

    def get(self):
        try:
            db = client["db_ng"]
            collection = db["emails"]

            products = []
            
            for doc in collection.find({}):
                doc["_id"] = str(doc["_id"])
                products.append(doc)
            return products, 200
        except Exception as e:
            return f"Unexpected error: {e}", 500
uri = f"mongodb+srv://admin:{MONGO_PASSWORD}@{MONGO_CLUSTER}/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

if __name__ == "__main__":
    app.run(port=5004, host="0.0.0.0")