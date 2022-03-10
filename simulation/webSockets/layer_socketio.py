from flask_socketio import SocketIO, send, emit
from app_init import flaskHttpApp, gpApp

from logic import *

# https://flask-socketio.readthedocs.io/en/latest/getting_started.html
# 'wss://[IP_ADDRESS]/socket.io/?EIO=3&transport=websocket'
socketio = SocketIO(flaskHttpApp)

'''The following examples bounce received events back to the client that sent them:'''


@socketio.on('message')
def handle_message_socketio(message):
    '''Client sends us a message:str -> simply return the same message back to the client'''
    handle_message(gpApp, message)
    send(
        f'Client: [{message}], Server: [Message recieved, Simulations run: ({gpApp.simulationsRun})]')


@socketio.on('connection success event')
def handle_my_client_request_connection_success_event(json):
    # emit('my response', json)
    process_connection_success(json)


@socketio.on('start new simulation')
def start_new_simulation_socketio():
    entities = init_new_simulation(gpApp)
    if entities is not None:
        emit('simulation initialised', {'entities': entities})

    outputJson = start_isolated_simulation(gpApp)
    if outputJson is not None:
        # Not a broadcast, but emit to the client that made the request
        emit('simulation ran', outputJson)
    else:
        emit('simulation already running', '')

# @socketio.on('json')
# def handle_json(json):
#     send(json, json=True)


# @socketio.on('my event')
# def handle_my_client_request_update_event(json):
#     emit('my response', json)





def broadcast_new_transaction_to_clients(transaction: dict):
    socketio.emit('some event', transaction, namespace='/transaction')
    # NOTE: Note that socketio.send() and socketio.emit()
    #   are not the same functions as the context-aware send() and emit().


# def broadcast_new_app_initialised_to_clients():
#     socketio.emit('init success', gpApp.entities, namespace='/')
