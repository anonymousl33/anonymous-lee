from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os, json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Gmail configuration
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
NOTIFICATION_EMAIL = "lee.anonymousl33@gmail.com"

def send_email_notification(message_data, message_type):
    """Send email notification for new messages"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = GMAIL_EMAIL
        msg['To'] = NOTIFICATION_EMAIL
        msg['Subject'] = f"New {message_type} Message - Anonymous Lee"
        
        # Email body
        body = f"""
New {message_type} message received on Anonymous Lee:

Timestamp: {message_data.get('timestamp', 'N/A')}
Type: {message_type}

"""
        
        if message_type == "Music":
            body += f"""Artist: {message_data.get('artist', 'N/A')}
Song: {message_data.get('song', 'N/A')}
Message Type: {message_data.get('type', 'N/A').title()}
"""
            if message_data.get('recipient'):
                body += f"Recipient: {message_data.get('recipient')}\n"
            if message_data.get('from'):
                body += f"From: {message_data.get('from')}\n"
            if message_data.get('message'):
                body += f"Optional Message: {message_data.get('message')}\n"
        else:
            body += f"""Recipient: {message_data.get('recipient', 'N/A')}
Message: {message_data.get('message', 'N/A')}
From: {message_data.get('from', 'Anonymous')}
"""
        
        body += f"\n---\nAnonymous Lee Admin Panel: https://{request.host}/admin"
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_EMAIL, GMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(GMAIL_EMAIL, NOTIFICATION_EMAIL, text)
        server.quit()
        
        print(f"Email notification sent for {message_type} message")
        
    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")

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

    # Send email notification
    if GMAIL_EMAIL and GMAIL_PASSWORD:
        send_email_notification(new_msg, "Normal")

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
    
    # Count new messages
    new_message_count = sum(1 for msg in messages if msg.get('status') == 'new')
    
    return render_template("dashboard.html", messages=messages, new_message_count=new_message_count)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("admin"))

@app.route("/label/<int:index>/<status>")
def label(index, status):
    if not session.get("admin"):
        return redirect(url_for("admin"))

    messages = load_messages()
    # Convert reversed index back to actual index
    actual_index = len(messages) - 1 - index
    if 0 <= actual_index < len(messages):
        messages[actual_index]['status'] = status
        save_messages(messages)

    return redirect(url_for("dashboard"))

@app.route("/delete-message/<int:index>")
def delete_message(index):
    if not session.get("admin"):
        return redirect(url_for("admin"))

    messages = load_messages()
    # Convert reversed index back to actual index
    actual_index = len(messages) - 1 - index
    if 0 <= actual_index < len(messages):
        messages.pop(actual_index)
        save_messages(messages)
        flash("Message deleted successfully!", "success")

    return redirect(url_for("dashboard"))

# Load polls
def load_polls():
    if not os.path.exists("polls.json"):
        return []
    with open("polls.json", "r") as f:
        return json.load(f)

# Save polls
def save_polls(polls):
    with open("polls.json", "w") as f:
        json.dump(polls, f, indent=2)

# Load user votes
def load_user_votes():
    if not os.path.exists("user_votes.json"):
        return {}
    with open("user_votes.json", "r") as f:
        return json.load(f)

# Save user votes
def save_user_votes(votes):
    with open("user_votes.json", "w") as f:
        json.dump(votes, f, indent=2)

# Load wall posts
def load_wall_posts():
    if not os.path.exists("wall_posts.json"):
        return []
    with open("wall_posts.json", "r") as f:
        return json.load(f)

# Save wall posts
def save_wall_posts(posts):
    with open("wall_posts.json", "w") as f:
        json.dump(posts, f, indent=2)

# Load quotes
def load_quotes():
    if not os.path.exists("quotes.json"):
        return []
    with open("quotes.json", "r") as f:
        return json.load(f)

# Save quotes
def save_quotes(quotes):
    with open("quotes.json", "w") as f:
        json.dump(quotes, f, indent=2)

# Load public posts
def load_public_posts():
    if not os.path.exists("public_posts.json"):
        return []
    with open("public_posts.json", "r") as f:
        return json.load(f)

# Save public posts
def save_public_posts(posts):
    with open("public_posts.json", "w") as f:
        json.dump(posts, f, indent=2)

@app.route("/rules")
def rules():
    return render_template("rules.html")

@app.route("/polls")
def polls():
    polls_data = load_polls()
    user_votes = load_user_votes()
    user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))

    # Prepare polls with voting status and results
    polls_with_status = []
    for i, poll in enumerate(polls_data):
        poll_copy = poll.copy()

        # Check if user has voted
        user_voted = user_ip in poll.get('votes', {})
        poll_copy['user_voted'] = user_voted

        # Calculate results
        votes = poll.get('votes', {})
        results = {}
        total_votes = 0

        for option in poll['options']:
            results[option] = 0

        for voter_ip, vote in votes.items():
            if vote in results:
                results[vote] += 1
                total_votes += 1

        poll_copy['results'] = results
        poll_copy['total_votes'] = total_votes

        # Add comments if they exist
        if 'comments' not in poll_copy:
            poll_copy['comments'] = []

        polls_with_status.append(poll_copy)

    return render_template("polls.html", polls=polls_with_status)

@app.route("/polls/vote/<int:poll_index>", methods=["POST"])
def vote_poll(poll_index):
    polls_data = load_polls()
    user_votes = load_user_votes()
    user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))

    if 0 <= poll_index < len(polls_data):
        vote = request.form.get("vote")

        # Check if user already voted
        if 'votes' not in polls_data[poll_index]:
            polls_data[poll_index]['votes'] = {}

        if user_ip not in polls_data[poll_index]['votes']:
            # Record the vote
            polls_data[poll_index]['votes'][user_ip] = vote
            save_polls(polls_data)

            flash("Your vote has been recorded!", "success")
        else:
            flash("You have already voted on this poll.", "error")

    return redirect(url_for("polls"))

@app.route("/admin/polls")
def admin_polls():
    if not session.get("admin"):
        return redirect(url_for("admin"))

    polls_data = load_polls()

    # Calculate total votes for each poll
    for poll in polls_data:
        poll['total_votes'] = len(poll.get('votes', {}))

    return render_template("admin_polls.html", polls=polls_data)

@app.route("/admin/polls/create", methods=["POST"])
def create_poll():
    if not session.get("admin"):
        return redirect(url_for("admin"))

    question = request.form.get("question")
    options = request.form.getlist("options")
    admin_insight = request.form.get("admin_insight")

    # Filter out empty options
    options = [opt.strip() for opt in options if opt.strip()]

    if question and len(options) >= 2:
        new_poll = {
            "question": question,
            "options": options,
            "admin_insight": admin_insight,
            "votes": {},
            "comments": [],
            "created_at": datetime.now(pytz.timezone("Asia/Manila")).strftime("%Y-%m-%d %I:%M %p")
        }

        polls_data = load_polls()
        polls_data.append(new_poll)
        save_polls(polls_data)

        flash("Poll created successfully!", "success")
    else:
        flash("Please provide a question and at least 2 options.", "error")

    return redirect(url_for("admin_polls"))

@app.route("/admin/polls/delete/<int:poll_index>")
def delete_poll(poll_index):
    if not session.get("admin"):
        return redirect(url_for("admin"))

    polls_data = load_polls()

    if 0 <= poll_index < len(polls_data):
        polls_data.pop(poll_index)
        save_polls(polls_data)
        flash("Poll deleted successfully!", "success")

    return redirect(url_for("admin_polls"))

@app.route("/polls/comment/<int:poll_index>", methods=["POST"])
def comment_on_poll(poll_index):
    data = request.get_json()
    comment_text = data.get("text", "").strip()

    if not comment_text:
        return {"success": False}

    polls_data = load_polls()

    if 0 <= poll_index < len(polls_data):
        if 'comments' not in polls_data[poll_index]:
            polls_data[poll_index]['comments'] = []

        new_comment = {
            "text": comment_text,
            "timestamp": datetime.now(pytz.timezone("Asia/Manila")).strftime("%Y-%m-%d %I:%M %p")
        }

        polls_data[poll_index]['comments'].append(new_comment)
        save_polls(polls_data)

        return {"success": True}

    return {"success": False}

# Public Wall routes
@app.route("/wall")
def public_wall():
    user_posts = load_wall_posts()
    admin_posts = load_public_posts()

    # Combine and sort posts by timestamp
    all_posts = []

    # Add user messages with type indicator
    for post in user_posts:
        post_copy = post.copy()
        post_copy['type'] = 'user'
        if 'reactions' not in post_copy:
            post_copy['reactions'] = {'like': 0, 'heart': 0, 'laugh': 0, 'sad': 0, 'wow': 0, 'angry': 0}
        if 'comments' not in post_copy:
            post_copy['comments'] = []
        all_posts.append(post_copy)

    # Add admin posts with type indicator
    for post in admin_posts:
        post_copy = post.copy()
        post_copy['type'] = 'admin'
        if 'reactions' not in post_copy:
            post_copy['reactions'] = {'like': 0, 'heart': 0, 'laugh': 0, 'sad': 0, 'wow': 0, 'angry': 0}
        if 'comments' not in post_copy:
            post_copy['comments'] = []
        all_posts.append(post_copy)

    # Sort by wall timestamp (newest first) - when admin posted it publicly
    try:
        all_posts.sort(key=lambda x: datetime.strptime(x.get('wall_timestamp', x.get('timestamp', '')), "%Y-%m-%d %I:%M %p"), reverse=True)
    except:
        pass  # If timestamp parsing fails, keep original order

    return render_template("public_wall.html", all_posts=all_posts)

@app.route("/admin/wall")
def admin_wall():
    if not session.get("admin"):
        return redirect(url_for("admin"))

    posts = load_wall_posts()
    return render_template("admin_wall.html", posts=posts)

@app.route("/post-to-wall/<int:index>", methods=["GET", "POST"])
def post_to_wall(index):
    if not session.get("admin"):
        return redirect(url_for("admin"))

    messages = load_messages()
    # Convert reversed index back to actual index
    actual_index = len(messages) - 1 - index
    
    if not (0 <= actual_index < len(messages)):
        flash("Message not found", "error")
        return redirect(url_for("dashboard"))

    if request.method == "GET":
        # Show reply form
        message = messages[actual_index]
        return render_template("admin_reply_form.html", message=message, index=index)
    
    if request.method == "POST":
        # Process reply and post to wall
        admin_reply = request.form.get("admin_reply", "").strip()
        
        message = messages[actual_index].copy()
        # Add admin reply if provided
        if admin_reply:
            message['admin_reply'] = admin_reply
        
        # Add wall timestamp
        message['wall_timestamp'] = datetime.now(pytz.timezone("Asia/Manila")).strftime("%Y-%m-%d %I:%M %p")
        
        # Mark original message as posted
        messages[actual_index]['status'] = 'seen'
        save_messages(messages)

        # Add to wall posts
        wall_posts = load_wall_posts()
        wall_posts.append(message)
        save_wall_posts(wall_posts)

        flash("Message posted to Freedom Wall!", "success")
        return redirect(url_for("dashboard"))

@app.route("/remove-from-wall/<int:index>")
def remove_from_wall(index):
    if not session.get("admin"):
        return redirect(url_for("admin"))

    wall_posts = load_wall_posts()

    if 0 <= index < len(wall_posts):
        wall_posts.pop(index)
        save_wall_posts(wall_posts)
        flash("Post removed from wall!", "success")

    return redirect(url_for("admin_wall"))

# Quotes routes
@app.route("/quotes")
def quotes():
    quotes_data = load_quotes()
    return render_template("quotes.html", quotes=quotes_data)

@app.route("/admin/quotes")
def admin_quotes():
    if not session.get("admin"):
        return redirect(url_for("admin"))

    quotes_data = load_quotes()
    return render_template("admin_quotes.html", quotes=quotes_data)

@app.route("/admin/quotes/create", methods=["POST"])
def create_quote():
    if not session.get("admin"):
        return redirect(url_for("admin"))

    text = request.form.get("text")
    author = request.form.get("author")

    if text:
        new_quote = {
            "text": text,
            "author": author or "Unknown",
            "timestamp": datetime.now(pytz.timezone("Asia/Manila")).strftime("%Y-%m-%d %I:%M %p")
        }

        quotes_data = load_quotes()
        quotes_data.append(new_quote)
        save_quotes(quotes_data)

        flash("Quote added successfully!", "success")
    else:
        flash("Please provide quote text.", "error")

    return redirect(url_for("admin_quotes"))

@app.route("/admin/quotes/delete/<int:index>")
def delete_quote(index):
    if not session.get("admin"):
        return redirect(url_for("admin"))

    quotes_data = load_quotes()

    if 0 <= index < len(quotes_data):
        quotes_data.pop(index)
        save_quotes(quotes_data)
        flash("Quote deleted successfully!", "success")

    return redirect(url_for("admin_quotes"))

# Admin Public Wall Management
@app.route("/admin/public-wall")
def admin_public_wall():
    if not session.get("admin"):
        return redirect(url_for("admin"))

    # Get both admin posts and user messages posted to wall
    admin_posts = load_public_posts()
    user_posts = load_wall_posts()
    
    # Combine all posts for admin view
    all_posts = []
    
    # Add admin posts with type indicator
    for i, post in enumerate(admin_posts):
        post_copy = post.copy()
        post_copy['type'] = 'admin'
        post_copy['source_index'] = i
        post_copy['source'] = 'admin'
        all_posts.append(post_copy)
    
    # Add user posts with type indicator
    for i, post in enumerate(user_posts):
        post_copy = post.copy()
        post_copy['type'] = 'user'
        post_copy['source_index'] = i
        post_copy['source'] = 'user'
        all_posts.append(post_copy)
    
    # Sort by wall timestamp (newest first)
    try:
        all_posts.sort(key=lambda x: datetime.strptime(x.get('wall_timestamp', x.get('timestamp', '')), "%Y-%m-%d %I:%M %p"), reverse=True)
    except:
        pass  # If timestamp parsing fails, keep original order
    
    return render_template("admin_public_wall.html", posts=all_posts)

@app.route("/admin/public-wall/create", methods=["POST"])
def create_public_post():
    if not session.get("admin"):
        return redirect(url_for("admin"))

    content = request.form.get("content")
    image = request.files.get("image")
    attachment = request.files.get("attachment")

    if content:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)

        new_post = {
            "content": content,
            "timestamp": datetime.now(pytz.timezone("Asia/Manila")).strftime("%Y-%m-%d %I:%M %p"),
            "reactions": {"like": 0, "laugh": 0, "heart": 0},
            "comments": []
        }

        # Handle image upload
        if image and image.filename:
            image_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.filename}"
            image.save(f"uploads/{image_filename}")
            new_post["image"] = image_filename

        # Handle file attachment
        if attachment and attachment.filename:
            attachment_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{attachment.filename}"
            attachment.save(f"uploads/{attachment_filename}")
            new_post["attachment"] = attachment_filename

        posts = load_public_posts()
        posts.append(new_post)
        save_public_posts(posts)

        flash("Public post created successfully!", "success")
    else:
        flash("Please provide content for the post.", "error")

    return redirect(url_for("admin_public_wall"))

@app.route("/admin/public-wall/delete/<int:index>")
def delete_public_post(index):
    if not session.get("admin"):
        return redirect(url_for("admin"))

    posts = load_public_posts()

    if 0 <= index < len(posts):
        post = posts.pop(index)
        save_public_posts(posts)

        # Clean up uploaded files
        if 'image' in post:
            try:
                os.remove(f"uploads/{post['image']}")
            except:
                pass
        if 'attachment' in post:
            try:
                os.remove(f"uploads/{post['attachment']}")
            except:
                pass

        flash("Public post deleted successfully!", "success")

    return redirect(url_for("admin_public_wall"))

@app.route("/admin/delete-from-wall/<source>/<int:index>")
def delete_from_wall(source, index):
    if not session.get("admin"):
        return redirect(url_for("admin"))

    if source == 'admin':
        posts = load_public_posts()
        if 0 <= index < len(posts):
            post = posts.pop(index)
            save_public_posts(posts)
            
            # Clean up uploaded files
            if 'image' in post:
                try:
                    os.remove(f"uploads/{post['image']}")
                except:
                    pass
            if 'attachment' in post:
                try:
                    os.remove(f"uploads/{post['attachment']}")
                except:
                    pass
            
            flash("Post deleted from Freedom Wall!", "success")
    
    elif source == 'user':
        posts = load_wall_posts()
        if 0 <= index < len(posts):
            posts.pop(index)
            save_wall_posts(posts)
            flash("Message deleted from Freedom Wall!", "success")

    return redirect(url_for("admin_public_wall"))

# Wall interaction routes
@app.route("/wall/react/<int:post_index>/<reaction_type>", methods=["POST"])
def react_to_post(post_index, reaction_type):
    user_posts = load_wall_posts()
    admin_posts = load_public_posts()

    # Combine posts to find the right one
    all_posts = user_posts + admin_posts

    if 0 <= post_index < len(all_posts):
        if 'reactions' not in all_posts[post_index]:
            all_posts[post_index]['reactions'] = {'like': 0, 'laugh': 0, 'heart': 0}

        if reaction_type in all_posts[post_index]['reactions']:
            all_posts[post_index]['reactions'][reaction_type] += 1
        else:
            all_posts[post_index]['reactions'][reaction_type] = 1

        # Save back to appropriate file
        if post_index < len(user_posts):
            save_wall_posts(user_posts)
        else:
            save_public_posts(admin_posts)

        return {"success": True, "count": all_posts[post_index]['reactions'][reaction_type]}

    return {"success": False}

@app.route("/wall/comment/<int:post_index>", methods=["POST"])
def comment_on_post(post_index):
    data = request.get_json()
    comment_text = data.get("text", "").strip()

    if not comment_text:
        return {"success": False}

    user_posts = load_wall_posts()
    admin_posts = load_public_posts()

    # Combine posts to find the right one
    all_posts = user_posts + admin_posts

    if 0 <= post_index < len(all_posts):
        if 'comments' not in all_posts[post_index]:
            all_posts[post_index]['comments'] = []

        new_comment = {
            "text": comment_text,
            "timestamp": datetime.now(pytz.timezone("Asia/Manila")).strftime("%Y-%m-%d %I:%M %p")
        }

        all_posts[post_index]['comments'].append(new_comment)

        # Save back to appropriate file
        if post_index < len(user_posts):
            save_wall_posts(user_posts)
        else:
            save_public_posts(admin_posts)

        return {"success": True}

    return {"success": False}

# Serve uploaded files
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return app.send_static_file(f"uploads/{filename}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

@app.route("/music", methods=["GET", "POST"])
def music():
    if request.method == "POST":
        artist = request.form.get("artist")
        song = request.form.get("song")  # updated name
        msg_type = request.form.get("type")
        recipient = request.form.get("recipient") if msg_type == "dedicated" else ""
        from_user = request.form.get("from")
        optional_msg = request.form.get("message")

        # Server-side validation for message type
        if not msg_type or msg_type not in ["recommended", "dedicated"]:
            flash("Please select a valid message type (Recommended by or Dedicated to)", "error")
            return redirect(url_for("music"))

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

        # Send email notification
        if GMAIL_EMAIL and GMAIL_PASSWORD:
            send_email_notification(new_music_msg, "Music")

        flash("Music message sent!", "success")
        return redirect(url_for("music"))

    return render_template("music_form.html")