from flask import Flask, request, jsonify
# from flask_pymongo import PyMongo
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests


# EXPECTED_DB = "todos"

app = Flask(__name__)
CORS(app)

# Required: MongoDB connection URI
# app.config["MONGO_URI"] = "mongodb://localhost:27017/todos"
# mongo = PyMongo(app)

# with app.app_context():
#     actual_db = mongo.db.name
#     print(actual_db)

#     if EXPECTED_DB != actual_db:
#         raise RuntimeError(
#             f"Database '{EXPECTED_DB}' does not exist. "
#         )

# @app.route("/signup", methods=["POST"])
# # def home():
# #     # Access your database via 'mongo.db'
# #     data = request.get_json()
# #     if not data or "name" not in data:
# #         return jsonify({"error": "name is required"}), 400
    
# #     res = mongo.db.user.insert_one({
# #         "name": data["name"],
# #         "username": data["username"],
# #         "password": data["password"]
# #     })
    
    
# #     users = mongo.db.user.find()
# #     result = []
# #     for i in users:
# #         i["_id"] = str(i["_id"])  # convert ObjectId to string
# #         result.append(i) 
# #     print(result)

# #     out = jsonify({
# #         "message": "User inserted successfully",
# #         "id": str(res.inserted_id),
# #         "users": result
# #     }), 201
# #     return out


@app.route("/sitefeedback", methods=["GET" , "POST"])
def get_site_feedback():
    # Implement your logic here
    # data = "https://myinterviewpractice.com/"
    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({"error": "URL is required"}), 400

    url = data["url"]
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    title = soup.title.string
    h1_tags = soup.find_all("h1")
    h1_texts = [h1.get_text(strip=True) for h1 in h1_tags]
    return jsonify({
        "title": title,
        "h1_texts": h1_texts,
        "h1_count": len(h1_tags)
    }), 200

if __name__ == "__main__":
    app.run(debug=True, port=9002, host="0.0.0.0")
