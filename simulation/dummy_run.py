# from httpRoutes2 import flaskHttpApp
# from socketio_init import socketio
# from flask_socketio import SocketIO
# # from httpRoutes import flaskHttpAppWithRoutes
# from colorama import Fore, Style
# import socketioRoutes # type:ignore
# # https://www.tutlinks.com/debugging-flask-app-with-vs-code-made-easy/
# # flaskHttpApp.run(host='0.0.0.0', port=5000)
# socketio = SocketIO(flaskHttpApp,
#                     path='socket.io',
#                     cors_allowed_origins="*",
#                     logger=True,
#                     engineio_logger=False,
#                     # allow_upgrades=False,
#                     async_mode='eventlet')

import logging
from socketio_init import socketio
from http_routes import flaskHttpApp
# from httpRoutes2 import flaskHttpAppWithRoutes
from colorama import Fore, Style
import socketioRoutes  # type:ignore
HOST: str = flaskHttpApp.config.get(
    'GEMBER_BIND_HOST')  # type:ignore
PORT: int = flaskHttpApp.config.get('GEMBER_PORT')  # type:ignore


def run_app():
    # logging.getLogger().setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                        )
    logging.getLogger().addHandler(logging.FileHandler('gpAppLog.log'))
    print(
        f'Running FLASK http server in {flaskHttpApp.env} mode with debug:={flaskHttpApp.debug}')
    print(flaskHttpApp.url_map._rules)
    print(Fore.GREEN + f'module name: {__name__}' + Style.RESET_ALL)
    socketio.run(flaskHttpApp,
                 host=HOST, port=PORT,
                 log_output=True,
                 debug=False,
                 use_reloader=False)
if __name__ == '__main__':
    run_app()