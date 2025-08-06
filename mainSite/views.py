import secrets
from . import db, csrf
from .models import Users, Comments, Articles
from threading import Thread
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session
from flask_login import current_user# , login_required
from .generator import SearchTermsPrompt
from .generator.controller import startProcess
# from .experiments.secutiry_token import verify_token, stop_emitting_tokens
from .experiments.HTMLformatter import format_article_html

views = Blueprint('views',__name__)

@views.route('/')
def MainPage():
    return render_template('home.html')

@views.route('/home')
def RedirectHome():
    return redirect(url_for('views.MainPage'))

# @login_required
@views.route('/admin/generate', methods=['GET', 'POST'])
def Adminpanel():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    # if not current_user.is_admin:
    #     return render_template('error.html',error_code = 403)
    '''Hookup to generator'''
    if request.method == 'POST':
        product1 = request.form.get('product1')
        product2 = request.form.get('product2')
        affiliate1 = request.form.get('affiliate1')
        affiliate2 = request.form.get('affiliate2')
        article_type = request.form.get('articleType')
        includeHN = request.form.get("includeHN") == "on"
        extra = request.form.get('extra')
        article_info = request.form.get('article-extra')
        prompt = SearchTermsPrompt(product1=product1, product2=product2, extra_txt=extra)
        thread = Thread(target=startProcess, args=(prompt, article_info, includeHN, article_type), daemon=True)
        thread.start()
    print(session["csrf_token"])
    return render_template('admin.html', csrf_token=session['csrf_token'])

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

@csrf.exempt
@views.route('/api/publish', methods=['GET', 'POST'])
def Publish():
    auth_header = request.headers.get("X-CSRF-Token", "")
    # token = auth_header.replace("Bearer ", "")
    # if not verify_token(token):
    #     return jsonify({"error": "Authorization token is missing or invalid"}), 401
    token = session.get("csrf_token")
    if not token or auth_header != token:
        return jsonify({"error": "CSRF token missing or invalid"}), 403
    article_data = request.get_json()
    if not article_data:
        return jsonify({"error": "Request body is missing or not JSON"}), 400
    published_article = Articles.create_article(article_data)
    print(published_article.title)
    return jsonify({
        "status": "success",
        "message": "Article received successfully!",
        "data_received": article_data
    }), 200

@views.route('/api/comment')
def Comment():
    return None