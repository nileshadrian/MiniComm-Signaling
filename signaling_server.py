# signaling_server.py — Email Call Signaling Server with register handler and stability

import socketio
from flask import Flask

# Socket.IO server with stability settings (switch to supported async_mode)
sio = socketio.Server(cors_allowed_origins='*', async_mode='eventlet', ping_timeout=60, ping_interval=25)
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# Store user sessions
user_sessions = {}

@sio.event
def connect(sid, environ):
    print("🔌 Client connected", sid)

@sio.event
def disconnect(sid):
    print("❌ Client disconnected", sid)
    for email, session in list(user_sessions.items()):
        if session == sid:
            del user_sessions[email]
            print(f"🧹 Cleaned session for {email}")

@sio.on("register")
def handle_register(sid, data):
    email = data.get("email")
    if email:
        user_sessions[email] = sid
        print(f"✅ Registered {email} with sid: {sid}")
    else:
        print("⚠️ Registration attempt without email")

@sio.on("call")
def handle_call(sid, data):
    target = data.get("target")
    sender = data.get("from")
    offer = data.get("offer")

    print(f"📞 {sender} is calling {target}")
    if target in user_sessions:
        target_sid = user_sessions[target]
        sio.emit("incoming_call", {"from": sender, "offer": offer}, to=target_sid)
        print(f"📨 Routed call from {sender} to {target}")
    else:
        print(f"⚠️ Target {target} not found in sessions")

if __name__ == '__main__':
    print("🚀 Starting signaling server on http://localhost:5000")
    import eventlet
    import eventlet.wsgi
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
