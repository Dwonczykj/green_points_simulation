# from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
# from geventwebsocket.handler import WebSocketHandler
# from gevent.lock import Semaphore
# from gevent.pywsgi import WSGIServer, WSGISecureEnviron
# import gevent
# import queue
# from queue_main_global import QueueHolder
from enum import Enum
from typing import Any
from event_names import WebSocketClientEvent, WebSocketServerResponseEvent, MySocketIONamespaces
from flask_socketio import send, emit
import logging
from colorama import Fore, Style
import json
from app_globals import gpApp
from Bank import RetailerStrategyGPMultiplier, RetailerSustainabilityIntercept
from http_validators import validate_retailer_name, validate_retailer_sustainability, validate_retailer_strategy
from logic import *
from socketio_init import socketio

@socketio.on('connect')
def on_connect_socketio_global():
    if gpApp.debug:
        emit('fromServer',
            f'server ack connection to {MySocketIONamespaces.global_namespace.value} namespace')
    
@socketio.on('connect', namespace=MySocketIONamespaces.transactions.value)
def on_connect_socketio_transactions_channel():
    if gpApp.debug:
        emit('fromServer',
         f'server ack connection to {MySocketIONamespaces.transactions.value} namespace')

@socketio.on('connect', namespace=MySocketIONamespaces.simulation.value)
def on_connect_socketio_simulation_channel():
    if gpApp.debug:
        emit('fromServer', f'server ack connection to {MySocketIONamespaces.simulation.value} namespace')
    
@socketio.on('connect', namespace='/socket.io')
def on_connect_socketio():
    if gpApp.debug:
        emit('fromServer', f'server ack connection to /socket.io namespace')

@socketio.on('message')
def handle_message_socketio(message:str):
    '''Client sends us a message:str -> simply return the same message back to the client'''
    handle_message(gpApp, message)
    send(f'Client: [{message}], Server: [This is my response :)]')


# @socketio.on('connection success event')
# def handle_my_client_request_connection_success_event(json):
#     # emit('my response', json)
#     process_connection_success(json)


# @socketio.on('start new simulation')
# def start_new_simulation_socketio():
#     entities = init_new_simulation(gpApp)
#     if entities is not None:
#         emit('simulation initialised', {'entities': entities})

#     outputJson = start_isolated_simulation(gpApp)
#     if outputJson is not None:
#         # Not a broadcast, but emit to the client that made the request
#         emit('simulation ran', outputJson)
#     else:
#         emit('simulation already running', '')
        
# @socketio.on('connect')
# def socketio_connected():
#     logging.debug('socketio connected...')
    
@socketio.on('disconnect')
def socketio_disconnected():
    print(Fore.RED + f'socketio disconnected from {MySocketIONamespaces.global_namespace.value} namespace...' + Style.RESET_ALL)
    logging.debug(f'socketio disconnected from {MySocketIONamespaces.global_namespace.value} namespace...')


@socketio.on('disconnect', namespace=MySocketIONamespaces.transactions.value)
def socketio_disconnected_transactions_channel():
    logging.debug(
        f'socketio disconnected from {MySocketIONamespaces.transactions.value} namespace...')

@socketio.on('disconnect', namespace=MySocketIONamespaces.simulation.value)
def socketio_disconnected_simulation_channel():
    logging.debug(
        f'socketio disconnected from {MySocketIONamespaces.simulation.value} namespace...')
    
class WSMessage:
    def __init__(self, jsonBlob:Any) -> None:
        assert hasattr(jsonBlob, 'type')
        self.eventName:str = jsonBlob['type']
        self.data:Any = {}
        if hasattr(jsonBlob, 'data'):
            self.data = jsonBlob['data']

@socketio.on('ping')
def handle_ping_from_client(data):
    emit('pong', 'PONGING')       
    
@socketio.on('json')
def handle_json_global_nsp(jsonBlob):
    message = WSMessage(jsonBlob=jsonBlob)
    eventName = message.eventName
    if eventName == WebSocketClientEvent.connection_success_event:
        process_connection_success(message.data)
    elif eventName == WebSocketClientEvent.message and hasattr(message, 'data'):
        handle_message(gpApp, message.data)
        emit(WebSocketServerResponseEvent.message_received, 'hi from the green points server')
    # elif eventName == WebSocketClientEvent.start_isolated_simulation:
    #     entities = init_new_simulation(gpApp)
    #     if entities is not None:
    #         emit(WebSocketServerResponseEvent.gpApp_initialised,
    #              {
    #                 'entities': entities
    #              })
    #     outputJson = start_isolated_simulation(gpApp)
    #     if outputJson is not None:
    #         emit(WebSocketServerResponseEvent.simulation_ran, json.loads(outputJson))
    #     else:
    #         emit(WebSocketServerResponseEvent.simulation_already_running, 'simulation already running')
    elif eventName == WebSocketClientEvent.get_purchase_delay:
        emit(WebSocketServerResponseEvent.purchase_delay, gpApp.secondsBetweenPurchases)
    elif eventName == WebSocketClientEvent.change_purchase_delay:
        if isinstance(message.data, float) or isinstance(message.data, int):
            gpApp.secondsBetweenPurchases = float(
                message.data)
        elif isinstance(message.data, str) and message.data.isdecimal():
            gpApp.secondsBetweenPurchases = float(
                message.data)
        emit(WebSocketServerResponseEvent.purchase_delay, gpApp.secondsBetweenPurchases)
    elif eventName == WebSocketClientEvent.change_retailer_strategy:
        retailerName = message.data['retailerName']
        newStrategy = message.data['strategy']
        simulationId = message.data['simulation_id']
        if validate_retailer_name(retailerName):
            validate_retailer_strategy(
                retailerName, newStrategy)
            # Each client should be connected to an individual Simulation Environment that is indexed by a guid,
            #   the guid is given to the client when it pings off a simulation.
            #   There should also be a call to get current running simulation for clients.
            #   / WS to notify all clients of a new simulation running along with the guid for that simulation.
            simEnv = gpApp\
                .getSimulationEnvironment(simulationId)
            if simEnv is not None:
                simEnv.retailers[retailerName].strategy = RetailerStrategyGPMultiplier[newStrategy]
                emit(WebSocketServerResponseEvent.retailer_strategy_changed,
                     simEnv.retailers[retailerName].strategy)
    elif eventName == WebSocketClientEvent.change_retailer_sustainability_multiplier:
        retailerName = message.data['retailerName']
        newSustainability = message.data['sustainability']
        simulationId = message.data['simulation_id']
        if validate_retailer_name(retailerName):
            validate_retailer_sustainability(
                retailerName, newSustainability)
            simEnv = gpApp\
                .getSimulationEnvironment(simulationId)
            if simEnv is not None:
                simEnv.retailers[retailerName].sustainability = RetailerSustainabilityIntercept[newSustainability]
                emit(
                     WebSocketServerResponseEvent.retailer_sustainbility_changed,
                     simEnv.retailers[retailerName].sustainability)
    elif eventName == WebSocketClientEvent.change_customer_stickyness_factor:
        raise Exception(
            '<{__name__}> Not yet implemented a customer stickyness factor')
    else:
        logging.debug(
            f'<{__name__}> Unknown event passed with name {eventName}')
    # send(json, json=True)
    # pass


# def broadcast_new_transaction_to_clients(transaction: dict):
#     socketio.emit(WebSocketServerResponseEvent.bank_transaction_created, transaction, namespace=MySocketIONamespaces.global_namespace)
#     socketio.emit(WebSocketServerResponseEvent.bank_transaction_created,
#                   transaction, namespace=MySocketIONamespaces.transactions)
#     # NOTE: Note that socketio.send() and socketio.emit()
#     #   are not the same functions as the context-aware send() and emit().


# @socketio.on('my event')
# def handle_my_client_request_update_event(json):
#     emit('my response', json)

# callback_queue = QueueHolder.global_callback_queue


# def _from_main_thread_nonblocking():
#     while True:
#         try:
#             callback = callback_queue.get(False)  # doesn't block
#         except queue.Empty:  # raised when queue is empty
# #             break
# #         callback()
# import logging
# from colorama import Fore, Style
# from pprint import PrettyPrinter
# pp = PrettyPrinter(indent=2,sort_dicts=False)




# class AsyncWebSocketApplication(WebSocketApplication):
#     def on_open(self):
#         print("Connection opened")

#     def on_message(self, message):
#         self.ws.send(message)

#     def on_close(self, reason):
#         print(reason)

# def my_app(environ:WSGISecureEnviron, start_response:Callable):
#     sem = Semaphore()
#     path = environ["PATH_INFO"]
#     if path == "/websocket":
#         logging.debug(Fore.BLUE + pp.pformat(environ) + Style.RESET_ALL)
#         socket = MyWebSocket.getInstance(websocket=environ["wsgi.websocket"], 
#                                          gpApp=httpRoutes.gpApp,
#                                          semaphore=sem)
#         socket.handle_websocket()
#         socket.flush_event_emissions_queue()
#     # elif path == "/":
#     #     # TODO: Configure start_response to fix: list(self.application(self.environ, lambda s, h, e=None: [])) -> TypeError: 'NoneType' object is not iterable
#     #     #   See https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.wsgi_app for start_response explanation
#     #     return httpRoutes.app(environ, start_response)
#     else:
#         _app = httpRoutes.flaskHttpApp(environ, start_response)
#         socket = MyWebSocket.checkForInstance()
#         if socket is not None:
#             socket.flush_event_emissions_queue()
#         return _app
    
#     # _from_main_thread_nonblocking()


# environ_keys = [
#     'GATEWAY_INTERFACE',	
#     'SERVER_SOFTWARE',	
#     'SCRIPT_NAME',	
#     'wsgi.version',	
#     'wsgi.multithread',	
#     'wsgi.multiprocess',	
#     'wsgi.run_once',	
#     'wsgi.url_scheme',	
#     'wsgi.errors',	
#     'SERVER_NAME',	
#     'SERVER_PORT',	
#     'REQUEST_METHOD',	
#     'PATH_INFO',	
#     'QUERY_STRING',	
#     'SERVER_PROTOCOL',	
#     'REMOTE_ADDR',	
#     'REMOTE_PORT',	
#     'HTTP_HOST',	
#     'HTTP_CONNECTION',	
#     'HTTP_PRAGMA',	
#     'HTTP_CACHE_CONTROL',	
#     'HTTP_USER_AGENT',	
#     'HTTP_UPGRADE',	
#     'HTTP_ORIGIN',	
#     'HTTP_SEC_WEBSOCKET_VERSION',	
#     'HTTP_ACCEPT_ENCODING',	
#     'HTTP_ACCEPT_LANGUAGE',	
#     'HTTP_SEC_WEBSOCKET_KEY',	
#     'HTTP_SEC_WEBSOCKET_EXTENSIONS',	
#     'wsgi.input',	
#     'wsgi.input_terminated',	
#     'wsgi.websocket_version',	
#     'wsgi.websocket'
# ] # gevent.pywsgi.WSGISecureEnviron.keys