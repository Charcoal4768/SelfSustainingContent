import secrets
import time
import threading

_token_store = {}
_emit_thread = None
_stop_event = threading.Event()

def issue_token():
    token = secrets.token_urlsafe(16)
    _token_store[token] = time.time()
    return token

def verify_token(token):
    timestamp = _token_store.get(token)
    if not timestamp:
        return False
    if time.time() - timestamp > 300:
        _token_store.pop(token, None)
        return False
    return True

def emit_token_periodically(socket, namespace="/admin"):
    global _emit_thread, _stop_event
    _stop_event.clear()

    def loop():
        while not _stop_event.is_set():
            token = issue_token()
            socket.emit("token_update", {"token": token}, namespace=namespace)
            _stop_event.wait(timeout=300)  # wait or get interrupted

    if _emit_thread is None or not _emit_thread.is_alive():
        _emit_thread = threading.Thread(target=loop, daemon=True)
        _emit_thread.start()

def stop_emitting_tokens():
    _stop_event.set()
