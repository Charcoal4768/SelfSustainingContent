# views.py (updated, no Flask-WTF)
from . import db, csrf, socketio
from secrets import token_urlsafe
from .models import Users, Comments, Articles
from threading import Thread
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session
from flask_wtf.csrf import generate_csrf, validate_csrf, CSRFError
from flask_login import current_user, login_required
from .generator import SearchTermsPrompt
from .generator.controller import startProcess
from .experiments.HTMLformatter import format_article_html

views = Blueprint('views', __name__)

def issue_publish_token():
    token = token_urlsafe(32)
    session['publish_token'] = token
    return token

@views.route('/')
def MainPage():
    return render_template('home.html', current_user=current_user)

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
        thread = socketio.start_background_task(
            startProcess, app, prompt, article_info, include_hacker_news=includeHN, article_type=article_type, room = room_id
        )
        return render_template(
            'admin.html',
            room_id=room_id,
            csrf_token=generate_csrf(),
            publish_token = publish_token,
            current_user=current_user
        )

    csrf_token = generate_csrf()
    return render_template('admin.html', csrf_token=csrf_token, publish_token=publish_token, current_user=current_user, room_id=room_id)

@views.route("/posts/", methods=['GET', 'POST'])
def ShowPost():
    try:
        post_id = int(request.args.get('pid'))
    except (TypeError, ValueError):
        return render_template('error.html', error_code=404), 404
    article_extracted = Articles.get_article_by_id(post_id)
    if not article_extracted:
        return render_template('error.html',error_code = 404), 404
    article_extracted = format_article_html(article_extracted.json_response)
    return render_template('post.html',article=article_extracted)

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

@csrf.exempt
@views.route('/api/publish', methods=['POST'])
def Publish():
    auth_header = request.headers.get("X-CSRF-Token", "")
    token = session.get("publish_token")
    print(auth_header)
    print(token)
    if not token or auth_header != token:
        return jsonify({"error": "CSRF token missing or invalid"}), 403

    article_data = request.get_json()
    if not article_data:
        return jsonify({"error": "Request body is missing or not JSON"}), 400

    published_article = Articles.create_article(article_data)
    print(published_article.title)
    session.pop("publish_token", None)

    return jsonify({
        "status": "success",
        "message": "Article received successfully!",
        "data_received": article_data
    }), 200

@views.route('/api/comment')
def Comment():
    return None