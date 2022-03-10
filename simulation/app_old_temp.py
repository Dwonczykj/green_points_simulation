from __future__ import annotations, print_function

import logging
from flask import Flask, request
from flask.wrappers import Response
from http import HTTPStatus
import os
from flask_socketio import SocketIO, send

use_https = False
app = Flask(__name__)
socketio = SocketIO(app, path='socket.io', cors_allowed_origins="*")

def handle_message(message: str):
    logging.debug(
        f'Client: [{message}], Server: [Message handled]')


@socketio.on('message')
def handle_message_socketio(message):
    '''Client sends us a message:str -> simply return the same message back to the client'''
    handle_message(message)
    send(
        f'Client: [{message}], Server: [This is my response :)]')

app.config['GEMBER_HTTPS_KEYFILE'] = '/private/etc/ssl/localhost/localhost.key'
app.config['GEMBER_HTTPS_CERTFILE'] = '/private/etc/ssl/localhost/localhost.crt'
app.config['GEMBER_BIND_HOST'] = '127.0.0.1'
app.config['GEMBER_PORT'] = 8443
app.secret_key = os.urandom(24)
app.config['SECRET_KEY'] = 'secret!'
app.config["ALLOW_THREADING"] = False
app.config['DEBUG_APP'] = True


def wrap_CORS_response(response: Response):
    response.headers['Access-Control-Allow-Origin'] = request.origin
    return response

@app.route('/')
def index():
    return wrap_CORS_response(response=Response('flask app connected over http',status=HTTPStatus.OK))


@app.route('/anon')
def anon():
    return wrap_CORS_response(response=Response(f'hi anon',status=HTTPStatus.OK))


@app.route('/name/<name>')
def indexwName(name):
    return wrap_CORS_response(response=Response(f'hi {name}', status=HTTPStatus.OK))



HOST = app.config['GEMBER_BIND_HOST']  # or try '0.0.0.0'
PORT = app.config['GEMBER_PORT']

ssl_args = {}
if use_https:
    ssl_args = {
        'keyfile': app.config.get('GEMBER_HTTPS_KEYFILE'),
        'certfile': app.config.get('GEMBER_HTTPS_CERTFILE')
    }

httpEchoApplication = app


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().addHandler(logging.FileHandler('gpAppLog.log'))

    socketio.run(httpEchoApplication, host=HOST, port=PORT
                , log_output=True
                , debug=True
                , use_reloader=False
                )

