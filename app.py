from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify
import sqlite3
import hashlib
import base64
from google import genai
from google.genai import types
import requests

app = Flask(__name__)
app.secret_key = "secure_secret_key"

DATABASE = "voter_data.db"

client = genai.Client(api_key="AIzaSyBzMsoqR1LEsBO6T4h8ILWwDabOYeejt6g")  # Replace with your actual API key
system_instructions = """
You are an image scanner to scan an voter id card.
Scan the image and provide EPIC number.
If any information is not found or unclear return 'None' for that field.
Please return the information in string format and only print out the EPIC number.
"""
user_message = "What is this image?"

prompt = f"{system_instructions}\n\n{user_message}"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(DATABASE)
        setattr(g, '_database', db)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voters (
                aadhar_id TEXT PRIMARY KEY,
                name TEXT,
                dob TEXT,
                age INTEGER,
                mobile_no TEXT,
                address TEXT,
                voted INTEGER DEFAULT 0,
                image_data BLOB
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS officers (
                username TEXT PRIMARY KEY,
                password TEXT
            )
        """)
        cursor.execute("INSERT OR IGNORE INTO voters VALUES ('123456789012', 'Arnaya Gupta', '1990-01-01', 34, '9876543210', '123 Main St', 0, NULL)")
        cursor.execute("INSERT OR IGNORE INTO voters VALUES ('987654321098', 'Akhil Singh', '1985-05-15', 39, '8765432109', '456 Oak Ave', 0, NULL)")
        cursor.execute("INSERT OR IGNORE INTO voters VALUES ('488621545365', 'Aman Rajput', '2005-02-30', 19, '8874512354', '472 dairy road', 0, NULL)")
        cursor.execute("INSERT OR IGNORE INTO voters VALUES ('432654567895', 'Ankit Giri', '2000-10-16', 24, '9824156213', '456 wow street', 0, NULL)")
        cursor.execute("INSERT OR IGNORE INTO voters VALUES ('GDN0225185', 'PREM RAJ THAKUR', '1985-00-30', 39, '9824156213', '456 dariyaganj street', 0, NULL)")
        cursor.execute("INSERT OR IGNORE INTO officers VALUES ('officer1', ?)", (hashlib.sha256('password123'.encode()).hexdigest(),))
        cursor.execute("INSERT OR IGNORE INTO officers VALUES ('officer2', ?)", (hashlib.sha256('password123'.encode()).hexdigest(),))
        db.commit()

init_db()

def fetch_voter(aadhar_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM voters WHERE aadhar_id = ?", (aadhar_id,))
    return cursor.fetchone()

def update_voter_voted(aadhar_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE voters SET voted = 1 WHERE aadhar_id = ?", (aadhar_id,))
    db.commit()

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT password FROM officers WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result and hashlib.sha256(password.encode()).hexdigest() == result[0]:
            session["username"] = username
            return redirect(url_for("voter_check"))
        else:
            error = "Invalid credentials"
    return render_template("login.html", error=error)

@app.route("/voter_check", methods=["GET", "POST"])
def voter_check():
    if "username" not in session:
        return redirect(url_for("login"))
    voter_data = None
    status_message = None
    show_biometric = False
    gemini_answer = None  # added variable to store gemini answer

    aadhar_id = request.args.get('aadhar_id') #Get aadhar_id from url parameters.

    if request.method == "POST":
        aadhar_id = request.form["aadhar_id"]

    if aadhar_id:
        voter_data = fetch_voter(aadhar_id)
        if voter_data:
            if voter_data[6] == 1:
                status_message = "Voter has already voted."
            else:
                show_biometric = True
        else:
            status_message = "Voter ID not found."
    return render_template("voter_check.html", voter_data=voter_data, status_message=status_message, show_biometric=show_biometric, aadhar_id=aadhar_id, gemini_answer=gemini_answer)  # Passing gemini_answer to template

@app.route("/biometric_verification", methods=["POST"])
def biometric_verification():
    aadhar_id = request.form["aadhar_id"]
    update_voter_voted(aadhar_id)
    return redirect(url_for("voter_check")) #Added aadhar_id parameter.

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route('/ask_gemini', methods=['POST'])
def ask_gemini():
    try:
        data = request.get_json()
        image_data = data['image']

        # Remove the data URL prefix
        image_data = image_data.split(',')[1]

        # Prepare the request payload
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt,
                      types.Part.from_bytes(data=base64.b64decode(image_data), mime_type="image/jpeg")])

        answer = response.text

        return jsonify({'answer': answer})

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"API request failed: {e}"}), 500
    except (KeyError, IndexError, TypeError) as e:
        return jsonify({'error': f"Error parsing API response: {e}"}), 500
    except Exception as e:
        return jsonify({'error': f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run()
