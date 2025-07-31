from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from dotenv import load_dotenv
from flask_cors import CORS
import os
import pyrebase
from fallback import build_crew

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")

# Firebase Config
firebase_config = {
    "apiKey": os.getenv("API_KEY"),
    "authDomain": os.getenv("AUTH_DOMAIN"),
    "databaseURL": os.getenv("DATABASE_URL"),
    "projectId": os.getenv("PROJECT_ID"),
    "storageBucket": os.getenv("STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("MESSAGING_SENDER_ID"),
    "appId": os.getenv("APP_ID")
}
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirmpassword = request.form['confirmPassword']
        try:
            if password == confirmpassword:
                auth.create_user_with_email_and_password(email, password)
                flash("Account created successfully. Please login.", "success")
                return redirect(url_for('login'))
            else:
                flash("Passwords do not match.", "danger")
        except Exception as e:
            flash(f"Signup failed: {extract_error_message(e)}", "danger")
    return render_template('chatbot/signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
            return redirect(url_for('chatbot'))
        except Exception as e:
            flash(f"Login failed: {extract_error_message(e)}", "danger")
    return render_template('chatbot/login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    return render_template('chatbot/dashboard.html', user=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/chatbot')
def chatbot():
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    return render_template('chatbot/chatbot.html', user=session['user'])

@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400

        user_message = data['message']
        print(f"📝 Processing message: {user_message}")

       
        result = build_crew(user_message)
        output = result.final_answer if hasattr(result, "final_answer") else str(result)
        
        print(f"✅ Response generated: {output}")
        return jsonify({"response": output})

    except Exception as e:
        print(f"❌ Error in chatbot_api: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def extract_error_message(exception):
    try:
        return exception.args[1]['error']['message']
    except:
        return str(exception)

# Run app
if __name__ == '__main__':
    app.run(debug=True)
