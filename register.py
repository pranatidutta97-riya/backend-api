from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
import requests


EXPECTED_DB = "pms"  # Change this to your expected database name

app = Flask(__name__)
CORS(app)

app.config["MONGO_URI"] = "mongodb://localhost:27017/pms"  # Change this to your MongoDB URI
mongo = PyMongo(app)

with app.app_context():
    actual_db = mongo.db.name
    print(actual_db)

    if EXPECTED_DB != actual_db:
        raise RuntimeError(
            f"Database '{EXPECTED_DB}' does not exist. "
        )

@app.route("/signup", methods=["POST" , "GET"])
def home():
    # Access your database via 'mongo.db'
    error = []
    data = request.get_json()
    if not data.get("username", "").strip() or not data.get("email", "").strip() or not data.get("password", "").strip():
        error.append("All fields are required")

    if error:
        return jsonify({"errors": error}), 400

    # Check if user already exists
    existing_user = mongo.db.employee.find_one({"username": data["username"]})
    if existing_user:
        # return jsonify({"error": "Username already exists"}), 400
        error.append("Username already exists")
    
    if error:
        return jsonify({"errors": error}), 400
    
    res = mongo.db.employee.insert_one({
        "username": data["username"],
        "email": data["email"],
        "password": data["password"]
    })
    
    
    employee = mongo.db.employee.find()
    result = []
    
    for i in employee:
        i["_id"] = str(i["_id"])  # convert ObjectId to string
        result.append(i) 
    print(result)
    
    
    out = jsonify({
        "message": "User inserted successfully",
        "id": str(res.inserted_id),
        "employees": result
    }), 201
    return out

@app.route("/signin", methods=["POST" , "GET"])
def signin():
    udata = request.get_json()
    
    user = mongo.db.employee.find_one({"email": udata["email"], "password": udata["password"]})
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    user["_id"] = str(user["_id"])
    return jsonify({"message": "Signin successful", "user": user}), 200

if __name__ == "__main__":
    app.run(debug=True, port=9003, host="0.0.0.0")
