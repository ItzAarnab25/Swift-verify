from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "secure_secret_key"

DATABASE = "voter_data.db"

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
                voted INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS officers (
                username TEXT PRIMARY KEY,
                password TEXT
            )
        """)
        cursor.execute("INSERT OR IGNORE INTO voters VALUES ('123456789012', 'Alice Smith', '1990-01-01', 34, '9876543210', '123 Main St', 0)")
        cursor.execute("INSERT OR IGNORE INTO voters VALUES ('987654321098', 'Bob Johnson', '1985-05-15', 39, '8765432109', '456 Oak Ave', 0)")
        cursor.execute("INSERT OR IGNORE INTO voters VALUES ('488621545365', 'Aman Rajput', '2005-02-30', 19, '8874512354', '472 dairy road', 0)")
        cursor.execute("INSERT OR IGNORE INTO voters VALUES ('432654567895', 'Ankit Giri', '2000-10-16', 24, '9824156213', '456 wow street', 0)")
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
    if request.method == "POST":
        aadhar_id = request.form["aadhar_id"]
        voter_data = fetch_voter(aadhar_id)
        if voter_data:
            if voter_data[6] == 1:
                status_message = "Voter has already voted."
            else:
                show_biometric = True
        else:
            status_message = "Voter ID not found."
    return render_template("voter_check.html", voter_data=voter_data, status_message=status_message, show_biometric=show_biometric, aadhar_id=request.form.get("aadhar_id"))

@app.route("/biometric_verification", methods=["POST"])
def biometric_verification():
    aadhar_id = request.form["aadhar_id"]
    update_voter_voted(aadhar_id)
    return redirect(url_for("voter_check"))

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run()