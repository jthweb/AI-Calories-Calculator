import os
import requests
import json
from flask import Flask, render_template, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# --- App Initialization ---
app = Flask(__name__, template_folder='templates')

# --- In-Memory Database (Placeholder for MySQL) ---
# This dictionary will act as our database for now.
# In a real application, you would replace this with MySQL queries.
# TODO: Replace with a proper User table in MySQL.
users_db = {}
# TODO: Replace with a proper DailyLogs table in MySQL, linked by a user_id.
user_logs_db = {}


# --- Frontend Routes ---
@app.route("/")
def index():
    """Serves the main HTML page."""
    return render_template("index.html")


# --- API Routes ---

@app.route("/signup", methods=["POST"])
def signup():
    """Handles user registration with name and API key."""
    data = request.json
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    api_key = data.get("apiKey")

    if not all([email, password, name, api_key]):
        return jsonify({"error": "All fields (Email, Password, Name, API Key) are required."}), 400

    if email in users_db:
        return jsonify({"error": "User with this email already exists."}), 409

    # TODO: Replace with MySQL INSERT query
    # IMPORTANT: In a real database, the API key should be encrypted.
    users_db[email] = {
        "name": name,
        "password_hash": generate_password_hash(password),
        "api_key": api_key  # Storing encrypted key is recommended
    }
    
    # Initialize user log
    user_logs_db[email] = {}

    return jsonify({"message": "User created successfully."}), 201


@app.route("/login", methods=["POST"])
def login():
    """Handles user login."""
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    # TODO: Replace with MySQL SELECT query
    user = users_db.get(email)
    if user and check_password_hash(user["password_hash"], password):
        # In a real app, you would create a session or JWT token here
        return jsonify({
            "message": "Login successful.", 
            "email": email,
            "name": user.get("name")
        }), 200
    else:
        return jsonify({"error": "Invalid credentials."}), 401


@app.route("/daily-log/<email>/<date>", methods=["GET"])
def get_daily_log(email, date):
    """Fetches the daily log for a user."""
    # TODO: Replace with MySQL SELECT query
    if email in user_logs_db and date in user_logs_db[email]:
        return jsonify(user_logs_db[email][date])
    else:
        return jsonify({"calorieGoal": 0, "totalCalories": 0, "meals": []})

@app.route("/daily-log/<email>/<date>/goal", methods=["POST"])
def set_calorie_goal(email, date):
    """Sets the daily calorie goal."""
    data = request.json
    goal = data.get("goal")

    if not isinstance(goal, int) or goal <= 0:
        return jsonify({"error": "Invalid goal."}), 400
        
    # TODO: Replace with MySQL UPDATE or INSERT query
    if email not in user_logs_db:
        user_logs_db[email] = {}
    if date not in user_logs_db[email]:
        user_logs_db[email][date] = {"calorieGoal": 0, "totalCalories": 0, "meals": []}
    
    user_logs_db[email][date]["calorieGoal"] = goal
    return jsonify({"message": "Goal updated."}), 200


@app.route("/daily-log/<email>/<date>/meal", methods=["POST"])
def add_meal_log(email, date):
    """Adds a meal to the daily log."""
    meal_data = request.json
    
    # TODO: Replace with MySQL UPDATE query
    if email not in user_logs_db:
        return jsonify({"error": "User not found"}), 404
    if date not in user_logs_db[email]:
         user_logs_db[email][date] = {"calorieGoal": 0, "totalCalories": 0, "meals": []}

    log = user_logs_db[email][date]
    log["meals"].append(meal_data)
    log["totalCalories"] += meal_data.get("totalMealCalories", 0)

    return jsonify({"message": "Meal added successfully."}), 200


def get_user_api_key(email):
    """Safely retrieves a user's API key."""
    if email in users_db:
        return users_db[email].get("api_key")
    return None

@app.route("/analyze-meal", methods=["POST"])
def analyze_meal():
    """Analyzes a meal image using the user's Gemini API key."""
    data = request.json
    email = data.get("email")
    api_key = get_user_api_key(email)
    if not api_key:
        return jsonify({"error": "API Key not found for user. Please check your profile."}), 400
        
    base64_image = data.get("image")
    mime_type = data.get("mimeType")
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    system_prompt = """
    You are a nutrition expert. Analyze the food image. Identify all food items, estimate portion sizes, and calculate nutritional info.
    Respond ONLY with a JSON object. The JSON should have two keys: "totalCalories" (a number) and "foodItems" (an array of objects).
    Each object in "foodItems" must have these keys: "item" (string), "calories" (number), "fat" (number), "carbs" (number), "protein" (number).
    Do not include any text outside the JSON object.
    """

    payload = {
        "contents": [{"parts": [{"text": system_prompt}, {"inline_data": {"mime_type": mime_type, "data": base64_image}}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        api_response = response.json()
        json_text = api_response["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify(json.loads(json_text)), 200
    except requests.exceptions.RequestException as e:
        error_info = e.response.json() if e.response else str(e)
        return jsonify({"error": f"API request failed: {error_info.get('error', {}).get('message', str(e))}"}), 500
    except (KeyError, IndexError):
        return jsonify({"error": "Invalid response from AI model. Check if the image is clear."}), 500


@app.route("/get-suggestion", methods=["POST"])
def get_suggestion():
    """Gets a meal suggestion from the Gemini API using the user's key."""
    data = request.json
    email = data.get("email")
    log_data = data.get("log")
    
    api_key = get_user_api_key(email)
    if not api_key:
        return jsonify({"error": "API Key not found for user."}), 400

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    remaining_calories = log_data.get('calorieGoal', 2000) - log_data.get('totalCalories', 0)
    eaten_foods = ", ".join(item['item'] for meal in log_data.get('meals', []) for item in meal.get('foodItems', [])) or "nothing yet"

    prompt = f"""
    I am on a diet with a daily goal of {log_data.get('calorieGoal', 2000)} calories.
    So far today, I have consumed {log_data.get('totalCalories', 0)} calories. I have eaten: {eaten_foods}.
    I have {remaining_calories} calories left.
    Please suggest a simple, healthy, and specific meal for my next meal that fits within my remaining calories.
    Provide 2-3 options. Be brief and encouraging. Format your response with markdown for titles and lists.
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        api_response = response.json()
        suggestion_text = api_response["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"suggestion": suggestion_text}), 200
    except requests.exceptions.RequestException as e:
        error_info = e.response.json() if e.response else str(e)
        return jsonify({"error": f"API request failed: {error_info.get('error', {}).get('message', str(e))}"}), 500
    except (KeyError, IndexError):
        return jsonify({"error": "Invalid response from AI model."}), 500


# --- Main Execution ---
if __name__ == "__main__":
    app.run(debug=True, port=5001)

