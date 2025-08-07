from mainSite import make_app, socketio  # <- import socketio from __init__.py

app = make_app()

if __name__ == '__main__':
    # app.run(host = "0.0.0.0", debug = True, port=3000)
    socketio.run(app, debug=True, port=3000)  # this is crucial