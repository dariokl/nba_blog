from webapp import app
import schedule
import time
from webapp import socketio


if __name__ == '__main__':
    socketio.run(app, debug=True)
