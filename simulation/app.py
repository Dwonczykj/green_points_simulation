import logging
from socketio_init import socketio
from http_routes import flaskHttpApp as flaskHttpAppWithRoutes
from colorama import Fore, Style
import socketioRoutes # type:ignore
HOST:str = flaskHttpAppWithRoutes.config.get('GEMBER_BIND_HOST') # type:ignore
PORT:int = flaskHttpAppWithRoutes.config.get('GEMBER_PORT') # type:ignore
WSPORT:int = flaskHttpAppWithRoutes.config.get('GEMBER_WS_PORT') # type:ignore
def run_app():
    
    logging.basicConfig(level=logging.DEBUG,
                        format=Fore.BLUE + '[%(levelname)s] (%(threadName)-10s) %(message)s' + Style.RESET_ALL,
                        )
    logging.getLogger().addHandler(logging.FileHandler('gpAppLog.log'))
    print(Fore.BLUE + Style.DIM + f'Running FLASK http server in {flaskHttpAppWithRoutes.env} mode with debug:={flaskHttpAppWithRoutes.debug}' + Style.RESET_ALL)
    
    socketio.run(flaskHttpAppWithRoutes, 
                 host=HOST, port=PORT, 
                 log_output=True, 
                 debug=False, 
                 use_reloader=False)
    
if __name__ == '__main__':
    logging.debug(f'Hooray, we are using main thread: \'{__name__}\'')
    run_app()
else:
    logging.debug(f'why are we not using main thread and instead using: {__name__}.py')
    run_app()
