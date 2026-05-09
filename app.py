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
        # Structure
        "missing_title": 0,
        "missing_lang": 0,
        "multiple_h1": 0,
        "missing_h1": 0,
        "skipped_heading_level": 0,
        "missing_main": 0,
        "multiple_main": 0,
        "missing_nav": 0,
        "multiple_nav": 0,
        "missing_header": 0,
        "multiple_header": 0,
        "multiple_footer": 0,
        "missing_footer": 0,

        # Forms
        "missing_labels": 0,
        "placeholder_only_inputs": 0,

        # Media
        "missing_alt": 0,

        # Navigation
        "empty_links": 0,
        "empty_buttons": 0,
    }

    passed = {
        "title": False,
        "lang": False,
        "single_h1": False,
        "main_landmark": False,
        "nav_landmark": False,
        "header_landmark": False,
        "footer_landmark": False,
    }

    recommendations = []
    # Title Check
    # -----------------------------
    title = "No Title Found"
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
        passed["title"] = True
    else:
        issues["missing_title"] += 1
        recommendations.append("Add a descriptive <title> tag to your page.")

    # Language Check
    # -----------------------------
    html_tag = soup.find("html")
    if html_tag and html_tag.get("lang"):
        passed["lang"] = True
    else:
        issues["missing_lang"] += 1
        recommendations.append("Add a 'lang' attribute to the <html> tag.")

    # H1 Tag Check
    # -----------------------------
    h1_tags = soup.find_all("h1")
    h1_texts = [h1.get_text(strip=True) for h1 in h1_tags]
    if len(h1_tags) == 1:
        passed["single_h1"] = True
    elif len(h1_tags) == 0:
        issues["missing_h1"] += 1
        recommendations.append("Add an <h1> tag to your page.")
    else:
        issues["multiple_h1"] = len(h1_tags) - 1
        recommendations.append("Ensure there is only one <h1> tag on the page.")

    # HEADING HIERARCHY CHECK
    # =============================
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    last_level = 0
    for heading in headings:
        level = int(heading.name[1])
        # Skip first heading
        if last_level == 0:
            last_level = level
            continue
        if last_level and level > last_level + 1:
            issues["skipped_heading_level"] += 1
            recommendations.append(
                f"Heading '{heading.get_text(strip=True)}' is an <{heading.name}> but should be at most <h{last_level + 1}>."
            )
        last_level = level


    # Semantic Landmarks
    # -----------------------------
    # Main Landmark Check
    main_tags = soup.find_all("main")
    if len(main_tags) == 1:
        passed["main_landmark"] = True
    elif len(main_tags) == 0:
        issues["missing_main"] += 1
        recommendations.append("Add a <main> landmark to your page.")
    else:
        issues["multiple_main"] = len(main_tags) - 1
        recommendations.append("Use only one main landmark.")

    # Nav Landmark Check
    nav_tags = soup.find_all("nav")
    if len(nav_tags) == 1:
        passed["nav_landmark"] = True
    elif len(nav_tags) == 0:
        issues["missing_nav"] += 1
        recommendations.append("Add a <nav> landmark to your page.")
    else:
        issues["multiple_nav"] = len(nav_tags) - 1
        recommendations.append("Use only one nav landmark.")

    # Header Landmark Check
    header_tags = soup.find_all("header")
    if len(header_tags) == 1:
        passed["header_landmark"] = True
    elif len(header_tags) == 0:
        issues["missing_header"] += 1
        recommendations.append("Add a <header> landmark to your page.")
    else:
        issues["multiple_header"] = len(header_tags) - 1
        recommendations.append("Use only one header landmark.")

    # Footer Landmark Check
    footer_tags = soup.find_all("footer")
    if len(footer_tags) == 1:
        passed["footer_landmark"] = True
    elif len(footer_tags) == 0:
        issues["missing_footer"] += 1
        recommendations.append("Add a <footer> landmark to your page.")
    else:
        issues["multiple_footer"] = len(footer_tags) - 1
        recommendations.append("Use only one footer landmark.")
    
    # Form Accessibility Checks
    # -----------------------------
    form_tags = soup.find_all("form")
    for form in form_tags:
        # Label Check
        inputs = form.find_all(["input", "textarea", "select"])
        for input_tag in inputs:
            if input_tag.name == "input" and input_tag.get("type") in ["hidden", "submit", "button", "reset"]:
                continue  # Skip non-interactive inputs
            if not input_tag.get("id") or not soup.find("label", {"for": input_tag["id"]}):
                issues["missing_labels"] += 1
                recommendations.append(
                    f"Form element '{input_tag}' is missing a label. Add a <label> with a 'for' attribute referencing the input's id."
                )
            elif input_tag.get("placeholder") and not input_tag.get("aria-label"):
                issues["placeholder_only_inputs"] += 1
                recommendations.append(
                    f"Form element '{input_tag}' relies only on a placeholder. Add an 'aria-label' or a visible <label> for better accessibility."
                )
    # Media Accessibility Checks
    # -----------------------------
    img_tags = soup.find_all("img")
    for img in img_tags:
        if not img.has_attr("alt"):
            issues["missing_alt"] += 1
            recommendations.append(
                f"Image '{img}' is missing alt text. Add a descriptive 'alt' attribute to the <img> tag."
            )
    # Navigation Accessibility Checks
    # -----------------------------
    a_tags = soup.find_all("a")
    for a in a_tags:
        if not a.get("href") or a["href"].strip() == "":
            issues["empty_links"] += 1
            recommendations.append(
                f"Link '{a}' has an empty href. Ensure all <a> tags have a valid 'href' attribute."
            )
    button_tags = soup.find_all("button")
    for button in button_tags:
        if not button.get_text(strip=True) or button.get("aria-label") == "" or button.get("title") == "": 
            issues["empty_buttons"] += 1
            recommendations.append(
                f"Button '{button}' has no text. Ensure all <button> tags have descriptive text content."
            )
    
    # Positive Score
    # -----------------------------
    positive_score = 0

    if passed["title"]:
        positive_score += 10

    if passed["lang"]:
        positive_score += 10

    if passed["single_h1"]:
        positive_score += 10

    if passed["main_landmark"]:
        positive_score += 10

    if passed["nav_landmark"]:
        positive_score += 5

    if passed["header_landmark"]:
        positive_score += 5

    if passed["footer_landmark"]:
        positive_score += 5

    weights = {
        "missing_title": 10, #moderate
        "missing_lang": 8, #moderate
        "missing_h1": 10, #critical
        "multiple_h1": 4, #minor
        "missing_main": 10, #critical
        "multiple_main": 8, #moderate
        "skipped_heading_level": 5, #moderate
        "missing_nav": 4, #minor
        "multiple_nav": 3, #minor
        "missing_header": 3, #minor
        "multiple_header": 3, #minor
        "multiple_footer": 3, #minor
        "missing_footer": 3, #minor
        "missing_labels": 8, #critical
        "placeholder_only_inputs": 5, #critical
        "missing_alt": 5, #moderate
        "empty_links": 5, #moderate
        "empty_buttons": 6, #moderate
    }
    penalty_caps = {
        "missing_title": 15,
        "missing_lang": 10,
        "missing_h1": 15,
        "multiple_h1": 10,
        "missing_main": 15,
        "multiple_main": 10,
        "skipped_heading_level": 10,
        "missing_nav": 8,
        "missing_header": 6,
        "multiple_header": 6,
        "multiple_footer": 6,
        "missing_footer": 6,
        "missing_labels": 20,
        "placeholder_only_inputs": 15,
        "missing_alt": 20,
        "empty_links": 15,
        "empty_buttons": 20,
        "multiple_nav": 10,
    }
    penalty_score = 0

    for key, count in issues.items():

        issue_penalty = count * weights[key]

        capped_penalty = min(
            issue_penalty,
            penalty_caps[key]
        )

        penalty_score += capped_penalty

    score = max(0, min(100, 100 - penalty_score))  

    # Severity breakdown (for charts)
    severity = {
        "critical": issues["missing_labels"] + issues["placeholder_only_inputs"] + issues["missing_h1"] + issues["missing_main"],
        "moderate": issues["missing_alt"] + issues["empty_links"] + issues["skipped_heading_level"] + issues["missing_title"] + issues["missing_lang"] + issues["multiple_main"],
        "minor": issues["multiple_h1"] + issues["missing_nav"] + issues["missing_header"] + issues["missing_footer"] + issues["multiple_nav"] + issues["multiple_header"] + issues["multiple_footer"],
    }

    return jsonify({
        "title": title,
        "score": score,
        "issues": issues,
        "severity": severity,
        "h1_count": len(h1_tags),
        "h1_texts": h1_texts,
        "passed_checks": passed,
        "severity": severity,
        "recommendations": list(set(recommendations))
    }), 200

if __name__ == "__main__":
    app.run(debug=True, port=9002, host="0.0.0.0")
