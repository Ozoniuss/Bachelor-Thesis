import os

from app import create_app

from app.extensions import socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app, port=os.getenv("PORT", 5000), debug=os.getenv("DEBUG", True))
