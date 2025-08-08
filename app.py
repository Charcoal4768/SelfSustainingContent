from mainSite import app, socketio  # <- import socketio from __init__.py

if __name__ == '__main__':
    import eventlet.wsgi
    socketio.run(app, debug=True)