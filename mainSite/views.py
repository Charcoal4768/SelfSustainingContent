from . import csrf, socketio, db
from secrets import token_urlsafe
from datetime import datetime, timedelta
from .models import Comments, Articles
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session
from flask_wtf.csrf import generate_csrf, validate_csrf, CSRFError
from flask_login import current_user, login_required
from .generator import SearchTermsPrompt
from .generator.controller import startProcess
from .experiments.HTMLformatter import format_article_html

views = Blueprint('views', __name__)
comment_tokens = {}  # token -> {user_id, article_id, expires_at, remaining_uses}

def issue_publish_token():
    token = token_urlsafe(32)
    session['publish_token'] = token
    return token

@views.route('/')
def MainPage():
    feed_content = []
    web_hosting_articles = Articles.get_articles_by_tag("web hosting")
    controversies_articles = Articles.get_articles_by_tag("AI controversies")
    latest_articles = Articles.get_latest_articles()
    feed_content.append(("Web Hosting", web_hosting_articles))
    feed_content.append(("Controversies", controversies_articles))
    feed_content.append(("Latest Articles", latest_articles))
    return render_template('home.html', current_user=current_user, feed_content=feed_content)

@views.route('/home')
def RedirectHome():
    return redirect(url_for("views.MainPage"))

@login_required
@views.route('/admin/generate', methods=['GET', 'POST'])
def Adminpanel():
    if not current_user.is_admin:
        return "Unauthorized", 403
    publish_token = issue_publish_token()
    room_id = token_urlsafe(16)
    if request.method == 'POST':
        room_id = token_urlsafe(16)
        try:
            publish_token = issue_publish_token()
        except Exception as e:
            print("Token generation error:", e)
            publish_token = None
        csrf_token = request.form.get("csrf_token")
        try:
            validate_csrf(csrf_token)
        except CSRFError:
            return "Invalid CSRF Token", 400
        from flask import current_app
        app = current_app._get_current_object()
        product1 = request.form.get("product1")
        product2 = request.form.get("product2")
        affiliate1 = request.form.get("affiliate1")
        affiliate2 = request.form.get("affiliate2")
        article_type = request.form.get("articleType") or "Listicle"
        includeHN = bool(request.form.get("includeHN"))
        extra = request.form.get("extra")
        article_info = request.form.get("article-extra")
        prompt = SearchTermsPrompt(product1=product1, product2=product2, extra_txt=extra)
        socketio.start_background_task(
            startProcess, app, prompt, article_info, include_hacker_news=includeHN,
            article_type=article_type, room=room_id
        )
        return render_template(
            'admin.html', room_id=room_id, csrf_token=generate_csrf(),
            publish_token=publish_token, current_user=current_user
        )
    csrf_token = generate_csrf()
    return render_template('admin.html', csrf_token=csrf_token,
                           publish_token=publish_token, current_user=current_user,
                           room_id=room_id)

@views.route("/posts/", methods=['GET', 'POST'])
def ShowPost():
    try:
        post_id = int(request.args.get('pid'))
    except (TypeError, ValueError):
        return render_template('error.html', error_code=404), 404
    article_extracted = Articles.get_article_by_id(post_id)
    if not article_extracted:
        return render_template('error.html', error_code=404), 404
    article_extracted = format_article_html(article_extracted.json_response)
    comments = Comments.get_comments_by_article_id(post_id)
    publish_token = issue_publish_token()
    room_id = token_urlsafe(16)
    return render_template('post.html', article=article_extracted, comments=comments,
                           publish_token=publish_token, current_user=current_user,
                           post_id=post_id, room_id=room_id)

@views.route("/trending")
def TrendingPage():
    return render_template('browse.html', current_user=current_user)

@views.route("/about")
def AboutPage():
    return render_template('about.html', current_user=current_user)

@views.route("/profile")
def ProfilePage():
    return render_template('profile.html', current_user=current_user)

@views.route("/settings")
def SettingsPage():
    return render_template('settings.html', current_user=current_user)

# --- New in-memory comment token system ---
def generate_comment_token(user_id, article_id):
    token = token_urlsafe(32)
    comment_tokens[token] = {
        "user_id": user_id,
        "article_id": article_id,
        "expires_at": datetime.utcnow() + timedelta(minutes=2),
        "remaining_uses": 10
    }
    return token

@socketio.on("request_comment_token")
def handle_request_comment_token(data):
    if not current_user.is_authenticated:
        return
    article_id = data.get("article_id")
    room_id = data.get("room_id")
    token = generate_comment_token(current_user.id, article_id)
    socketio.emit("comment_token", {"token": token}, to=room_id)

@views.route('/api/new_publish_token', methods=['GET'])
@login_required
def NewPublishToken():
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"publish_token": issue_publish_token()})

@csrf.exempt
@views.route('/api/publish', methods=['POST'])
def Publish():
    auth_header = request.headers.get("X-CSRF-Token", "")
    token = session.get("publish_token")
    if not token or auth_header != token:
        return jsonify({"error": "CSRF token missing or invalid"}), 403
    article_data = request.get_json()
    if not article_data:
        return jsonify({"error": "Request body is missing or not JSON"}), 400
    Articles.create_article(article_data)
    session.pop("publish_token", None)
    return jsonify({"status": "success", "message": "Article received successfully!",
                    "data_received": article_data}), 200

@csrf.exempt
@views.route('/api/comment', methods=['POST'])
def Comment():
    try:
        auth_header = request.headers.get("X-CSRF-Token", "")
        token_data = comment_tokens.get(auth_header)
        if not token_data:
            return jsonify({"error": "Invalid or expired token"}), 403
        if token_data["expires_at"] < datetime.utcnow() or token_data["remaining_uses"] <= 0:
            comment_tokens.pop(auth_header, None)
            return jsonify({"error": "Token expired"}), 403
        if token_data["user_id"] != current_user.id:
            return jsonify({"error": "Token mismatch"}), 403

        action = (request.json.get('action') or '').strip().lower()

        def consume():
            token_data["remaining_uses"] -= 1
            if token_data["remaining_uses"] <= 0:
                comment_tokens.pop(auth_header, None)

        if action == "delete":
            comment_id = request.json.get('comment_id')
            Comments.delete_comment(comment_id)
            consume()
            return jsonify({"status": "success", "message": "Comment deleted"})

        elif action == "edit":
            comment_id = request.json.get('comment_id')
            comment_body = (request.json.get('comment') or '').strip()
            if not comment_body:
                return jsonify({"error": "Comment body is empty"}), 400
            if len(comment_body) > 500:
                return jsonify({"error": "Comment body too long"}), 400
            Comments.edit_comment(comment_id, comment_body)
            consume()
            return jsonify({"status": "success", "message": "Comment edited"})

        elif action == "add":
            comment_body = (request.json.get('comment') or '').strip()
            if not comment_body:
                return jsonify({"error": "Comment body is empty"}), 400
            if len(comment_body) > 500:
                return jsonify({"error": "Comment body too long"}), 400
            Comments.make_comment(current_user.id, token_data["article_id"], comment_body)
            consume()
            return jsonify({"status": "success", "message": "Comment posted",
                            "username": current_user.username})

        else:
            return jsonify({"error": "Invalid action"}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Server error", "detail": str(e)}), 500
