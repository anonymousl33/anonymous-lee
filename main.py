from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from datetime import datetime
import pytz

import os, json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Load messages
def load_messages():
    if not os.path.exists("messages.json"):
        return []
    with open("messages.json", "r") as f:
        return json.load(f)

# Save messages
def save_messages(messages):
    with open("messages.json", "w") as f:
        json.dump(messages, f, indent=2)

@app.route("/")
def home():
    return render_template("message_form.html")

@app.route("/send", methods=["POST"])
def send():
    recipient = request.form.get("recipient")
    message = request.form.get("message")
    sender = request.form.get("from")

    new_msg = {
        "recipient": recipient,
        "message": message,
        "from": sender,
        "status": "new",
        "timestamp": datetime.now(pytz.timezone("Asia/Manila")).strftime("%Y-%m-%d %I:%M %p")
    }

    messages = load_messages()
    messages.append(new_msg)
    save_messages(messages)

    flash("Message sent anonymously!", "success")
    return redirect(url_for("home"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid login credentials", "error")
            return redirect(url_for("admin"))

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin"))

    messages = load_messages()
    messages.reverse()  # Show newest first
    return render_template("dashboard.html", messages=messages)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("admin"))

@app.route("/label/<int:index>/<status>")
def label(index, status):
    if not session.get("admin"):
        return redirect(url_for("admin"))

    messages = load_messages()
    if 0 <= index < len(messages):
        messages[index]['status'] = status
        save_messages(messages)

    return redirect(url_for("dashboard"))

if __name__ == '__main__':
    app.run(debug=True)

@app.route("/rules")
def rules():
    return render_template("rules.html")

@app.route("/music", methods=["GET", "POST"])
def music():
    if request.method == "POST":
        artist = request.form.get("artist")
        song = request.form.get("song")  # updated name
        msg_type = request.form.get("type")
        recipient = request.form.get("recipient") if msg_type == "dedicated" else ""
        from_user = request.form.get("from")
        optional_msg = request.form.get("message")

        new_music_msg = {
            "artist": artist,
            "song": song,
            "type": msg_type,
            "recipient": recipient,
            "from": from_user,
            "message": optional_msg,
            "timestamp": datetime.now(pytz.timezone("Asia/Manila")).strftime("%Y-%m-%d %I:%M %p"),
            "status": "new"
        }


        # Load and save like the regular message
        messages = load_messages()
        messages.append(new_music_msg)
        save_messages(messages)

        flash("Music message sent!", "success")
        return redirect(url_for("music"))

    return render_template("music_form.html")
