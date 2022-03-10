from flask_socketio import SocketIO

from app_init import flaskHttpApp
socketio = SocketIO(flaskHttpApp,
                    path='socket.io',
                    cors_allowed_origins="*", 
                    logger=True,
                    engineio_logger=False,
                    # allow_upgrades=False,
                    async_mode='eventlet')