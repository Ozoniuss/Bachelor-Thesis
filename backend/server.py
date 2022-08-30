import os
import tensorflow as tf

from app import create_app

from app.extensions import socketio

app = create_app()

physical_devices = tf.config.experimental.list_physical_devices("GPU")
tf.config.experimental.set_memory_growth(physical_devices[0], True)

if __name__ == "__main__":
    socketio.run(app, port=os.getenv("PORT", 5000), debug=os.getenv("DEBUG", True))
