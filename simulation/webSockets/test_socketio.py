import json
import eventlet
import unittest
import os
import logging
from flask import Flask, session, request, json as flask_json
from flask_socketio import SocketIO, send, emit, \
    Namespace, disconnect
    
import pandas as pd
from Bank import ControlRetailer, RetailerStrategyGPMultiplier, RetailerSustainabilityIntercept

from GreenPointsSimulation import GreenPointsLoyaltyApp
from app_config import SimulationConfig



flaskHttpAppConfig = {}
flaskHttpAppConfig['USE_HTTPS'] = False
flaskHttpAppConfig['GEMBER_HTTPS_KEYFILE'] = '/private/etc/ssl/localhost/localhost.key'
flaskHttpAppConfig['GEMBER_HTTPS_CERTFILE'] = '/private/etc/ssl/localhost/localhost.crt'
flaskHttpAppConfig['GEMBER_BIND_HOST'] = '127.0.0.1'
flaskHttpAppConfig['GEMBER_PORT'] = 8443
flaskHttpAppConfig['SECRET_KEY'] = os.urandom(24)
flaskHttpAppConfig["ALLOW_THREADING"] = True
flaskHttpAppConfig['DEBUG_APP'] = False

flaskHttpApp = Flask(__name__)

pardir = os.path.basename(os.getcwd())
if os.path.basename(os.getcwd()) == 'simulation':
    pardir = '/test'
elif os.path.basename(os.getcwd()) == 'GreenPoint':
    pardir = '/simulation/test'
else:
    cwd = os.getcwd()
    raise Exception(
        f'{cwd} should be simulation/test /Users/joeyd/Documents/JoeyDCareer/GitHub/Gember/GreenPoint/simulation/test')
df:pd.DataFrame = pd.read_json(f'.{pardir}/GreenPointsSimulation.json') #type:ignore

socketio = SocketIO(flaskHttpApp,
                    path='socket.io',
                    cors_allowed_origins="*",
                    logger=False,
                    engineio_logger=False,
                    # allow_upgrades=False,
                    async_mode='eventlet')

gpApp = GreenPointsLoyaltyApp.getInstance(data=df,
                                          socketio=socketio,
                                          debug=flaskHttpAppConfig['DEBUG_APP'])
disconnected = None


@socketio.on('connect')
def on_connect(auth):
    if auth != {'foo': 'bar'}:  # pragma: no cover
        return False
    if request.args.get('fail'):
        return False
    send('connected')
    send(json.dumps(request.args.to_dict(flat=False)))
    send(json.dumps({h: request.headers[h] for h in request.headers.keys()
                     if h not in ['Host', 'Content-Type', 'Content-Length']}))


@socketio.on('disconnect')
def on_disconnect():
    global disconnected
    disconnected = '/'


@socketio.event(namespace='/test')
def connect():
    send('connected-test')
    send(json.dumps(request.args.to_dict(flat=False)))
    send(json.dumps({h: request.headers[h] for h in request.headers.keys()
                     if h not in ['Host', 'Content-Type', 'Content-Length']}))


@socketio.on('disconnect', namespace='/test')
def on_disconnect_test():
    global disconnected
    disconnected = '/test'
    

@socketio.event
def message(message):
    send(message)
    if message == 'test session':
        session['a'] = 'b'
    if message not in "test noackargs":
        return message
    

@socketio.on('json')
def on_json(data):
    send(data, json=True, broadcast=True)
    if not data.get('noackargs'):
        return data


@socketio.on('message', namespace='/test')
def on_message_test(message):
    send(message)


@socketio.on('json', namespace='/test')
def on_json_test(data):
    send(data, json=True, namespace='/test')


@socketio.on('my custom event')
def on_custom_event(data):
    emit('my custom response', data)
    if not data.get('noackargs'):
        return data


@socketio.on('other custom event')
@socketio.on('and another custom event')
def get_request_event(data):
    global request_event_data
    request_event_data = request.data
    emit('my custom response', data)


def get_request_event2(data):
    global request_event_data
    request_event_data = request.data
    emit('my custom response', data)


socketio.on_event('yet another custom event', get_request_event2)


@socketio.on('my custom namespace event', namespace='/test')
def on_custom_event_test(data):
    emit('my custom namespace response', data, namespace='/test')


def on_custom_event_test2(data):
    emit('my custom namespace response', data, namespace='/test')


socketio.on_event('yet another custom namespace event', on_custom_event_test2,
                  namespace='/test')


@socketio.on('my custom broadcast event')
def on_custom_event_broadcast(data):
    emit('my custom response', data, broadcast=True)


@socketio.on('my custom broadcast namespace event', namespace='/test')
def on_custom_event_broadcast_test(data):
    emit('my custom namespace response', data, namespace='/test',
         broadcast=True)
    

@socketio.on('ping')    
@socketio.on('ping', namespace='/test')
def ping(data):
    logging.debug(data)
    emit('pong','PONGING')
    



class MyNamespace(Namespace):
    def on_connect(self):
        send('connected-ns')
        send(json.dumps(request.args.to_dict(flat=False)))
        send(json.dumps(
            {h: request.headers[h] for h in request.headers.keys()
             if h not in ['Host', 'Content-Type', 'Content-Length']}))

    def on_disconnect(self):
        global disconnected
        disconnected = '/ns'

    def on_message(self, message):
        send(message)
        if message == 'test session':
            session['a'] = 'b'
        if message not in "test noackargs":
            return message

    def on_json(self, data):
        send(data, json=True, broadcast=True)
        if not data.get('noackargs'):
            return data

    def on_exit(self, data):
        disconnect()

    def on_my_custom_event(self, data):
        emit('my custom response', data)
        if not data.get('noackargs'):
            return data

    def on_other_custom_event(self, data):
        global request_event_data
        request_event_data = getattr(request,'event')
        emit('my custom response', data)


socketio.on_namespace(MyNamespace('/ns'))

app = flaskHttpApp


@app.route('/session')
def session_route():
    session['foo'] = 'bar'
    return ''


class TestSocketIO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_connect(self):
        # client = socketio.test_client(app)
        # client2 = socketio.test_client(app)
        client = socketio.test_client(app, auth={'foo': 'bar'})
        client2 = socketio.test_client(app, auth={'foo': 'bar'})
        
        self.assertTrue(client.is_connected())
        self.assertTrue(client2.is_connected())
        self.assertNotEqual(client.eio_sid, client2.eio_sid)
        received = client.get_received()
        self.assertEqual(len(received), 3)
        self.assertEqual(received[0]['args'], 'connected')
        self.assertEqual(received[1]['args'], '{}')
        self.assertEqual(received[2]['args'], '{}')
        client.disconnect()
        self.assertFalse(client.is_connected())
        self.assertTrue(client2.is_connected())
        client2.disconnect()
        self.assertFalse(client2.is_connected())

    def test_connect_query_string_and_headers(self):
        client = socketio.test_client(
            app, query_string='?foo=bar&foo=baz',
            headers={'Authorization': 'Bearer foobar'},
            auth={'foo': 'bar'})
        received = client.get_received()
        self.assertEqual(len(received), 3)
        self.assertEqual(received[0]['args'], 'connected')
        self.assertEqual(received[1]['args'], '{"foo": ["bar", "baz"]}')
        self.assertEqual(received[2]['args'],
                         '{"Authorization": "Bearer foobar"}')
        client.disconnect()

    # def test_connect_namespace(self):
    #     client = socketio.test_client(app, namespace='/test')
    #     self.assertTrue(client.is_connected('/test'))
    #     received = client.get_received('/test')
    #     self.assertEqual(len(received), 3)
    #     self.assertEqual(received[0]['args'], 'connected-test')
    #     self.assertEqual(received[1]['args'], '{}')
    #     self.assertEqual(received[2]['args'], '{}')
    #     client.disconnect(namespace='/test')
    #     self.assertFalse(client.is_connected('/test'))

    # def test_connect_namespace_query_string_and_headers(self):
    #     client = socketio.test_client(
    #         app, namespace='/test', query_string='foo=bar',
    #         headers={'My-Custom-Header': 'Value'})
    #     received = client.get_received('/test')
    #     self.assertEqual(len(received), 3)
    #     self.assertEqual(received[0]['args'], 'connected-test')
    #     self.assertEqual(received[1]['args'], '{"foo": ["bar"]}')
    #     self.assertEqual(received[2]['args'], '{"My-Custom-Header": "Value"}')
    #     client.disconnect(namespace='/test')

    def test_connect_rejected(self):
        client = socketio.test_client(app, query_string='fail=1',
                                      auth={'foo': 'bar'})
        self.assertFalse(client.is_connected())

    def test_disconnect(self):
        global disconnected
        disconnected = None
        client = socketio.test_client(app, auth={'foo': 'bar'})
        client.disconnect()
        self.assertEqual(disconnected, '/')

    # def test_disconnect_namespace(self):
    #     global disconnected
    #     disconnected = None
    #     client = socketio.test_client(app, namespace='/test')
    #     client.disconnect('/test')
    #     self.assertEqual(disconnected, '/test')

    def test_send(self):
        client = socketio.test_client(app, auth={'foo': 'bar'})
        client.get_received()
        client.send('echo this message back')
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args'], 'echo this message back')
    
    def test_server_is_pingable(self):
        client = socketio.test_client(app, auth={'foo': 'bar'})
        client.get_received()
        client.emit('ping','PINGING')
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args'][0], 'PONGING')
    
    
    def test_server_is_pingable_namespace(self):
        # client = socketio.test_client(app, auth={'foo': 'bar'})
        client = socketio.test_client(app, namespace='/test')
        client.get_received('/test')
        client.emit('ping','PINGING', namespace="/test")
        received = client.get_received('/test')
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args'][0], 'PONGING')
        
        
    def test_run_simulation_is_non_blocking_for_socket_channel(self):
        import threading
        client = socketio.test_client(app, auth={'foo': 'bar'})
        client.get_received()
        
        gpApp.initAppEnv()
        simConfig = SimulationConfig()
        simConfig.maxN=10
        simConfig.convergenceTH=0.1
        simId, simType = gpApp.initSimulationFullEnvironment(
            simConfig=simConfig)
        
        def _f():
            client.get_received()
            client.emit('ping','PINGING')
            print('Try to ping server socket...')
            received = client.get_received()
            names = [r["name"] for r in received]
            print(names)
            self.assertGreater(len(received), 1)
            pongs= [r for r in received if r['name'] == 'pong']
            self.assertEqual(len(pongs), 1)
            self.assertEqual(pongs[0]['args'][0], 'PONGING')
            print('Success Ping -> Pong received')
            
        def _doNothing():
            pass
            
        def _g():
            print('run full sim')
            gpApp.run_full_simulation(simId,betweenIterationCallback=_doNothing)
            received = client.get_received()
            print('completed full sim')
            self.assertGreater(len(received), 50)
        
        t = threading.Thread(name='simulation_thread', 
                             target=_g)
        # w = threading.Thread(name='ping_thread',
        #                      target=_f)
        # w2 = threading.Thread(target=worker) # use default name
        # w2.start()
        # w.start()
        t.start()
        eventlet.sleep(1)
        _f()
        
        t.join() # finish task before logging test output.
        

    def test_send_json(self):
        client1 = socketio.test_client(app, auth={'foo': 'bar'})
        client2 = socketio.test_client(app, auth={'foo': 'bar'})
        client1.get_received()
        client2.get_received()
        client1.send({'a': 'b'}, json=True)
        received = client1.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args']['a'], 'b')
        received = client2.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args']['a'], 'b')

    def test_send_namespace(self):
        client = socketio.test_client(app, namespace='/test')
        client.get_received('/test')
        client.send('echo this message back', namespace='/test')
        received = client.get_received('/test')
        self.assertTrue(len(received) == 1)
        self.assertTrue(received[0]['args'] == 'echo this message back')

    def test_send_json_namespace(self):
        client = socketio.test_client(app, namespace='/test')
        client.get_received('/test')
        client.send({'a': 'b'}, json=True, namespace='/test')
        received = client.get_received('/test')
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args']['a'], 'b')

    def test_emit(self):
        client = socketio.test_client(app, auth={'foo': 'bar'})
        client.get_received()
        client.emit('my custom event', {'a': 'b'})
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]['args']), 1)
        self.assertEqual(received[0]['name'], 'my custom response')
        self.assertEqual(received[0]['args'][0]['a'], 'b')

    def test_emit_binary(self):
        client = socketio.test_client(app, auth={'foo': 'bar'})
        client.get_received()
        client.emit('my custom event', {u'a': b'\x01\x02\x03'})
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]['args']), 1)
        self.assertEqual(received[0]['name'], 'my custom response')
        self.assertEqual(received[0]['args'][0]['a'], b'\x01\x02\x03')

    # def test_request_event_data(self):
    #     client = socketio.test_client(app, auth={'foo': 'bar'})
    #     client.get_received()
    #     global request_event_data
    #     request_event_data = None
    #     client.emit('other custom event', 'foo')
    #     expected_data = {'message': 'other custom event', 'args': ('foo',)}
    #     self.assertEqual(request_event_data, expected_data)
    #     client.emit('and another custom event', 'bar')
    #     expected_data = {'message': 'and another custom event',
    #                      'args': ('bar',)}
    #     self.assertEqual(request_event_data, expected_data)

    def test_emit_namespace(self):
        client = socketio.test_client(app, namespace='/test')
        client.get_received('/test')
        client.emit('my custom namespace event', {'a': 'b'}, namespace='/test')
        received = client.get_received('/test')
        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]['args']), 1)
        self.assertEqual(received[0]['name'], 'my custom namespace response')
        self.assertEqual(received[0]['args'][0]['a'], 'b')

    def test_broadcast(self):
        client1 = socketio.test_client(app, auth={'foo': 'bar'})
        client2 = socketio.test_client(app, auth={'foo': 'bar'})
        client3 = socketio.test_client(app, namespace='/test')
        client2.get_received()
        client3.get_received('/test')
        client1.emit('my custom broadcast event', {'a': 'b'}, broadcast=True)
        received = client2.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]['args']), 1)
        self.assertEqual(received[0]['name'], 'my custom response')
        self.assertEqual(received[0]['args'][0]['a'], 'b')
        self.assertEqual(len(client3.get_received('/test')), 0)


if __name__ == '__main__':
    unittest.main()
