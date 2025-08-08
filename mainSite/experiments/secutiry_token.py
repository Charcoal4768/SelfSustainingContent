from secrets import token_urlsafe

def issue_publish_token():
    token = token_urlsafe(32)
    session['publish_token'] = token
    return token