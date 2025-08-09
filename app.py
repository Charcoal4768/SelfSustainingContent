from mainSite import app, socketio  # <- import socketio from __init__.py
#gunicorn app:app would work?
#

if __name__ == '__main__':
    import eventlet.wsgi
    socketio.run(app, host="0.0.0.0", debug=True)