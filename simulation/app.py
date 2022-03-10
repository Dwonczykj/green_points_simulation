# from __future__ import annotations, print_function
import logging
# from colorama import Fore, Style
from socketio_init import socketio
from httpRoutes2 import flaskHttpApp as flaskHttpAppWithRoutes
from colorama import Fore, Style
import socketioRoutes # type:ignore
HOST:str = flaskHttpAppWithRoutes.config.get('GEMBER_BIND_HOST') # type:ignore
PORT:int = flaskHttpAppWithRoutes.config.get('GEMBER_PORT') # type:ignore
def run_app():
    # logging.getLogger().setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG,
                        format=Fore.BLUE + '[%(levelname)s] (%(threadName)-10s) %(message)s' + Style.RESET_ALL,
                        )
    logging.getLogger().addHandler(logging.FileHandler('gpAppLog.log'))
    print(Fore.BLUE + Style.DIM + f'Running FLASK http server in {flaskHttpAppWithRoutes.env} mode with debug:={flaskHttpAppWithRoutes.debug}' + Style.RESET_ALL)
    # print(flaskHttpAppWithRoutes.url_map._rules)
    # print(Fore.GREEN + f'module name: {__name__}' + Style.RESET_ALL)
    socketio.run(flaskHttpAppWithRoutes, 
                 host=HOST, port=PORT, 
                 log_output=True, 
                 debug=False, 
                 use_reloader=False)
    
if __name__ == '__main__':
    print(f'Hooray, we are using {__name__}')
    run_app()
else:
    print(f'why are we not using main: {__name__}')
    run_app()

# logging.getLogger().setLevel(logging.DEBUG)
# logging.getLogger().addHandler(logging.FileHandler('gpAppLog.log'))


# HOST:str = flaskHttpApp.config.get('GEMBER_BIND_HOST')
# PORT:int = flaskHttpApp.config.get('GEMBER_PORT')
# if flaskHttpApp.config.get('USE_HTTPS'):
#     raise Exception('HTTPS Socket.io not yet implemented... cheers!')
#     if __name__ == '__main__':
#         socketio.run(flaskHttpApp, host=HOST, port=PORT, use_reloader=True, log_output=True, debug=True, **ssl_args)
# else:
#     logging.debug(Fore.YELLOW + 'Running HTTP' + Style.RESET_ALL)
#     if __name__ == '__main__':
        
#         socketio.run(flaskHttpApp, host=HOST, port=PORT
#                      ,log_output=True
#                      , debug=True
#                      , use_reloader=True
#                      )









# from geventwebsocket.handler import WebSocketHandler
# from gevent.pywsgi import WSGIServer
    

# if __name__ == '__main__':
#     # from httpRoutes import *
#     HOST = 'localhost'  # or try '0.0.0.0'
#     PORT = 5000
#     # https://kracekumar.com/post/54437887454/ssl-for-flask-local-development/
    
#     # ------------------------------------------Socketio----------------------------------------------------
#     # NOTE: The default Flask development server doesn't support websockets so you'll need to use another server. Thankfully it's simple to get eventlet working with Flask. All you should have to do is install the eventlet package using pip.
#     # $ (conda venv) conda install -c conda-forge eventlet
#     # Once eventlet is installed socketio will detect and use it when running the server.
#     # You can use chrome to double check what transport method is being used. 
#     #   Open your chrome dev tools Ctrl+Shift+I in Windows and go to the Network tab. 
#     #   On each network request you should see either transport=polling or transport=websocket
    
#     # socketio.run(app, host=HOST, port=PORT, ssl_context='adhoc') # BUG: eventlet doesnt support ssl_context kwargs.
#     # If running flask app on Heroku, use these links to set up SSL:
#     # https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-18-04
#     # https://stackoverflow.com/questions/53992331/cant-connect-to-flask-socketio-via-wss-but-works-via-ws

#     HOST = '127.0.0.1'
#     IP_ADDRESS = f"https://localhost:{PORT}/"
#     WSS_ADDRESS = f'wss://{IP_ADDRESS}/socket.io/?EIO=3&transport=websocket'
#     # Copied from Browser Console: https://localhost:5000/socket.io/?EIO=4&transport=polling&t=Ny2kvDQ&sid=ow8Yykvsa24xTGTzAAAC
#     # socketio.run(app,
#     #              host=HOST,
#     #              debug=True,
#     #              port=PORT,
#     #              ssl_context=('/private/etc/ssl/localhost/localhost.crt',
#     #                           '/private/etc/ssl/localhost/localhost.key'))
#     # wss://127.0.0.1:5000/socket.io/?EIO=4&transport=websocket&sid=d3LsyQHzBSwk_UmWAAAC
#     # from layer_socketio import socketio
#     PORT = 8443
#     IP_ADDRESS = f"https://localhost:{PORT}/"
#     WSS_ADDRESS = f'wss://{IP_ADDRESS}/socket.io/?EIO=3&transport=websocket'
#     # socketio.run(app,
#     #              host=HOST,
#     #              port=PORT,
#     #              debug=True,
#     #              certfile='/private/etc/ssl/localhost/localhost.crt',
#     #              keyfile='/private/etc/ssl/localhost/localhost.key'
#     #              )
#     # ------------------------------------------Simple WS----------------------------------------------------
#     # app.config['HOST'] = HOST
#     # app.config['PORT'] = PORT
#     # app.config['debug'] = True
#     # app.config['WEBSOCKET_URL'] = True # TODO Might need to configure this
    
#     # from layer_ws_simple import wsSimpleMixin
#     # ws = wsSimpleMixin(app)
#     # ws.run(
#     #     app,
#     #     host=HOST,
#     #     port=PORT,
#     #     debug=True,
#     #     )
#     # -------------------------------------------gevents ws ssl---------------------------------------------------
#     # from layer_gevents import server, LayerGevents, ws
    
#     # # to start the server asynchronously, call server.start()
#     # # we use blocking serve_forever() here because we have no other jobs
#     # try:
#     #     # server.serve_forever()
#     #     LayerGevents(app).serve_forever()
#     # except Exception as e:
#     #     print(f'GEvents websocket errored on creation: \n\t{e}')
#     # ----------------------------------------------------------------------------------------------
#     # from layer_geventwebsockets2 import server_basic_gevents_ws

#     # server_basic_gevents_ws.serve_forever()
    
#     # class RedirectStderr(TextIO):

#     #     def __init__(self, *args, **kwargs):
#     #         self._cfg = kwargs.pop('cfg')
#     #         self._log_file = open(self._cfg['access_log_path'], 'a')
#     #         super().__init__(*args, **kwargs)

#     #     def write(self, msg):
#     #         # Just in-case you want to write to both stderr and another log file
#     #         super(RedirectStderr, self).write(msg)

#     #         # Write to another access log file
#     #         self._log_file.write(msg)
#     #         self._log_file.flush()

#     #         # Or use Python's logging facility to log the standard way you log
#     #         # across your project
#     #         logging.info(msg)

#     #     def close(self):
#     #         super(RedirectStderr, self).close()
#     #         self._log_file.close()

#     # import sys
#     # cfg = {
#     #     'access_log_path': 'gpLog.log'
#     # }
#     # sys.stderr = RedirectStderr('/dev/stderr', 'w', cfg=cfg)
    
#     from geventwebsocket import WebSocketServer, WebSocketApplication, Resource


#     class EchoApplication(WebSocketApplication):
#         def on_open(self):
#             print("Connection opened")

#         def on_message(self, message):
#             self.ws.send(message)

#         def on_close(self, reason):
#             print(reason)
    
    
    
#     # -------------------------BASIC Server-------------------------
    
        
#     use_https = False
#     try:
#         import logging
#         # import subprocess
#         # from capturer import CaptureOutput
#         # , filename='app.log'
#         # logging.basicConfig(level=logging.DEBUG)
#         # Link to the original issue with Socket-IO using flutter: https://stackoverflow.com/questions/60348534/connecting-flask-socket-io-server-and-flutter
#         logging.getLogger().setLevel(logging.DEBUG)
#         logging.getLogger().addHandler(logging.FileHandler('gpAppLog.log'))
#         if use_https:
#             logging.debug(Fore.BLUE + 'Running HTTPS' + Style.RESET_ALL)
#             https_server = WSGIServer((HOST,PORT), my_app, handler_class=WebSocketHandler, **ssl_args)
#             https_server.serve_forever()
#         else:
#             # with CaptureOutput() as capturer:
#             logging.debug(Fore.YELLOW + 'Running HTTP' + Style.RESET_ALL)
#             _app = my_app
#             _app = Resource({'/': EchoApplication}) # Turn EchoApplication into MyApp 
#             http_server = WSGIServer((HOST,PORT), _app, handler_class=WebSocketHandler)
#             http_server.serve_forever()
#     except Exception as e:
#         logging.debug(
#             Fore.RED + f'WebApp level exception at app.py of: \n\t{e}' + Style.RESET_ALL)
