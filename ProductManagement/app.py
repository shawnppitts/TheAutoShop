import os
import uuid
from datetime import datetime
from dotenv import load_dotenv,find_dotenv
from pymongo.mongo_client import MongoClient
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields

app = Flask(__name__)

# env_path = "./src/.env"
# load_dotenv(env_path)
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")
MONGO_CLUSTER = os.environ.get("MONGO_CLUSTER")

api = Api(app)
product_ns = api.namespace("api/v1/products", "CRUD operations for Product")

productInsert = api.model(
    "ProductInsert",
    {
        "productName": fields.String(required=True, description="Product Name"),
        "productId": fields.String(required=True, description="Product's Unique ID"),
        "price": fields.Float(required=True, description="Product Price"),
        "tax": fields.Float(required=True, description="Product tax percentage"),
        "description": fields.String(required=False, description="Description of product"),
        "status": fields.String(required=True, description="Product Status"),
        "url" : fields.String(required=True, description="Image Url of the Product")
    },
)

product = api.model(
    "Product",
    {
        "id": fields.String(required=True, description="Product's system generated Id"),
        "productName": fields.String(required=True, description="Product Name"),
        "productId": fields.String(required=True, description="Product's Unique ID"),
        "price": fields.Float(required=True, description="Product Price"),
        "tax": fields.Float(required=True, description="Product tax percentage"),
        "description": fields.String(required=False, description="Description of product"),
        "status": fields.String(required=True, description="Product Status"),
        "url" : fields.String(required=True, description="Image Url of the Product"),
        "createdAt" : fields.String(required=True, description="Time product is created")
    },
)

@product_ns.route("")
class Products(Resource):
    # tag::post[]
    @product_ns.doc(
        "Create Product",
        reponses={201: "Created", 409: "Key alreay exists", 500: "Unexpected Error"},
    )
    @product_ns.expect(productInsert, validate=True)
    @product_ns.marshal_with(product)
    def post(self):
        try:
            db = client["db_pm"]
            collection = db["products"]

            data = request.json
            id = uuid.uuid4().__str__()
            data["id"] = id
            data["createdAt"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            collection.insert_one(data)
            return data, 201
        except Exception as e:
            return f"Unexpected error: {e}", 500

    @product_ns.doc(
        "Find Products",
        reponses={200: "found", 500: "Unexpected Error"},
        params={
            "status": "Product is ACTIVE/INACTIVE"
        },
    )
    def get(self):
        try:
            db = client["db_pm"]
            collection = db["products"]

            products = []
            
            for doc in collection.find({}):
                doc["_id"] = str(doc["_id"])
                products.append(doc)
            return products, 200
        except Exception as e:
            return f"Unexpected error: {e}", 500

@product_ns.route("/<productId>")
class ProductId(Resource):
    @product_ns.doc(
        "Get Profile",
        reponses={200: "Document Found", 404: "Document Not Found", 500: "Unexpected Error"},
    )
    def get(self, productId):
        try:
            db = client.db_pm
            collection = client.products
            
            for doc in collection.find():
                print(doc)
            return 200
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
    app.run(port=5002, host="0.0.0.0")