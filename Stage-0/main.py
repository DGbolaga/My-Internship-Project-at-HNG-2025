import requests
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

    
#Configuration
CAT_API_URL = "https://catfact.ninja/fact"
USER_EMAIL = os.getenv("USER_EMAIL", "your.email@example.com")
USER_NAME = os.getenv("USER_NAME", "Your Name")
USER_STACK = os.getenv("USER_STACK", "Python/Flask")


def get_cat_fact():
    """
    Fetch a random cat fact from Cat Facts API.
    Returns a fallback message if API fails.
    """
    try: 
        response = requests.get(CAT_API_URL, timeout=5)
        response.raise_for_status() # raise exception for bad status code
        data = response.json()
        return data.get("fact", "No cat fact available")
    except Exception as e:
        # return a fall back message if any error occurrs.
        print(f"Error fetching cat fact: {e}")
        return "Cats are amazing creatures with incredible agility."
    

@app.route('/me')
def get_profile():
    """
    Main endpoint that returns user profile with cat fact.
    """
    
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    cat_fact = get_cat_fact()

    response_data = {
        "status": "success",
        "user": {
            "email": USER_EMAIL,
            "name": USER_NAME,
            "stack": USER_STACK,
        },
        "timestamp": current_time,
        "fact": cat_fact,
    }

    return jsonify(response_data), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
        