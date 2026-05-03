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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        return jsonify({"error": "Failed to fetch the website"}), 500
     # -------------------------
    # Accessibility Checks
    # -------------------------
    issues = {
        "missing_alt": 0,
        "missing_labels": 0,
        "multiple_h1": 0,
        "empty_links": 0,
    }
    # missing Alt Text
    image_alt = soup.find_all("img", alt=False)
    issues["missing_alt"] = len(image_alt)
    
    # Inputs without labels
    inputs = soup.find_all("input")
    for input_tag in inputs:
        if not input_tag.get("aria-label") and not input_tag.get("id") or not soup.find("label", {"for": input_tag.get("id")}):
            issues["missing_labels"] += 1

    # Multiple H1 Tags
    
    h1_tags = soup.find_all("h1")
    h1_texts = [h1.get_text(strip=True) for h1 in h1_tags]
    if len(h1_tags) > 1:
        issues["multiple_h1"] = len(h1_tags) - 1

    # Site Title
    if soup.title:
        title = soup.title.string.strip()
    else:
        title = "No Title Found"
    

    # Empty links
    links = soup.find_all("a")
    for link in links:
        text = link.get_text(strip=True)
        aria = link.get("aria-label")

        img = link.find("img")
        img_alt = img.get("alt") if img else None

        if not text and not aria and not img_alt:
            issues["empty_links"] += 1
    
    weights = {
        "missing_alt": 5,       # moderate
        "missing_labels": 8,    # critical
        "multiple_h1": 3,       # minor
        "site_title": 2,        # minor
        "empty_links": 4        # moderate
    }

    total_penalty = sum(issues[key] * weights[key] for key in issues)

    score = max(0, 100 - total_penalty)

    # Severity breakdown (for charts)
    severity = {
        "critical": issues["missing_labels"],
        "moderate": issues["missing_alt"] + issues["empty_links"],
        "minor": issues["multiple_h1"]
    }

    return jsonify({
        "title": title,
        "score": score,
        "issues": issues,
        "severity": severity,
        "h1_count": len(h1_tags),
        "h1_texts": h1_texts
    }), 200

if __name__ == "__main__":
    app.run(debug=True, port=9002, host="0.0.0.0")
