# pyright: reportUnusedVariable=false, reportGeneralTypeIssues=false, reportUnusedImport=false
# the above can be set to warning, info, error, false, true

from __future__ import annotations
from flask import url_for
from flask import Flask
from flask import request
from flask import make_response
from flask import abort, redirect, url_for
from flask import render_template
from flask_socketio import SocketIO, emit
from flask import jsonify
from markupsafe import escape

# NOTE: To run webapp: flask run from the Terminal in the GreenPointsSimulation venv.

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app) # https://flask-socketio.readthedocs.io/en/latest/getting_started.html


# The following section deals with handles on the server to handle messages from the client.

'''The following example creates a server-side event handler for an unnamed event using string (message) data:'''
@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)
    
'''The following example creates a server-side event handler for an unnamed event using json (message) data:'''
@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))
    
'''The most flexible type of event uses custom event names. The message data for these events can be string, bytes, int, or JSON:'''
@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

'''Custom named events can also support multiple arguments: 
    (Notice the decorator argument here is a custom event named: my_event i.e. contains an underscore)'''
@socketio.on('my_event')
def handle_my_custom_event_named_my_event(arg1, arg2, arg3):
    print('received args: ' + arg1 + arg2 + arg3)
    
'''we can do the same with more concise syntax:'''
'''When the name of the event is a valid Python identifier that does not collide with other defined symbols, 
    the @socketio.event decorator provides a more compact syntax that takes the event name from the decorated function:'''
@socketio.event
def my_custom_event(arg1, arg2, arg3):
    print('received args: ' + arg1 + arg2 + arg3)
    
'''The names message, json, connect and disconnect are reserved and cannot be used for named events.'''

'''To allow multiple independent client connections to one socket: use namespaces (default is '/' when not specified) as so:'''
@socketio.on('my event', namespace='/test')
def handle_my_custom_namespace_event(json):
    print('received json: ' + str(json))
    

# The following section deals with endpoints on the client to allow the server to push messages to the client.
# We begin with how to responsd to messages from an individual client, 
# we can also Broadcast if there is no incoming client message to start the conversation. We demonstrate Broadcasts further down...

'''SocketIO event handlers defined as shown in the previous section can send reply messages to the connected client using the send() and emit() functions.'''

'''The following examples bounce received events back to the client that sent them:'''
from flask_socketio import send, emit

@socketio.on('message')
def handle_message(message):
    send(message)

@socketio.on('json')
def handle_json(json):
    send(json, json=True)

@socketio.on('my event')
def handle_my_custom_event(json):
    emit('my response', json)

'''and for specifying a namespace different to what was received from the client:'''
@socketio.on('message')
def handle_message(message):
    send(message, namespace='/chat')

@socketio.on('my event')
def handle_my_custom_event(json):
    emit('my response', json, namespace='/chat')
    

'''and for events with multiple args:'''
@socketio.on('my event')
def handle_my_custom_event(json):
    emit('my response', ('foo', 'bar', json), namespace='/chat')
    
'''Check message was received by client with a callback:'''
def ack():
    print('message was received!')

@socketio.on('my event')
def handle_my_custom_event(json):
    emit('my response', json, callback=ack)
    
# Broadcasts from Server to Clients that are subscribed to namespace:

'''When a message is sent with the broadcast option enabled, all clients connected to the namespace receive it, including the sender. 
    When namespaces are not used, the clients connected to the global namespace ('/') receive the message. 
    Note that callbacks are not invoked for broadcast messages.'''
@socketio.on('my event')
def handle_my_custom_event(data):
    emit('my response', data, broadcast=True)   
    
    
'''In all the examples shown until this point the server responds to an event sent by the client. 
    But for some applications, the server needs to be the originator of a message. 
    This can be useful to send notifications to clients of events that originated in the server, for example in a background thread. 
    The socketio.send() and socketio.emit() methods can be used to broadcast to all connected clients: 
    (Remember socketio is our flask app instance)'''
def some_function():
    socketio.emit('some event', {'data': 42})
    # NOTE: Note that socketio.send() and socketio.emit() 
    #   are not the same functions as the context-aware send() and emit(). 
    # Also note that in the above usage there is no client context, 
    #   so broadcast=True is assumed and does not need to be specified.
    

# Grouping Clients (Users) into subsets with different permissions, types etc...


@socketio.on('my event')                          # Decorator to catch an event called "my event":
def test_message(message):                        # test_message() is the event callback function.
    '''
    Test function to illustrate flask websockets.
        Docs: https://flask-socketio.readthedocs.io/en/latest/getting_started.html'''
    emit('my response', {'data': 'got it!'})      # Trigger a new event called "my response" 
                                                  # that can be caught by another callback later in the program.




@app.route('/')
def index():
    return 'Index Page'



@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return f'User {escape(username)}'

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return f'Post {post_id}'

@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    # show the subpath after /path/
    return f'Subpath {escape(subpath)}'

def valid_login(username, password):
    return True

def log_the_user_in(username):
    pass

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)
    
    


with app.test_request_context('/hello', method='POST'):
    # now you can do something with the request until the
    # end of the with block, such as basic assertions:
    assert request.path == '/hello'
    assert request.method == 'POST'
    
    
# Cookies:

@app.route('/cookies', method='GET')
def cookies():
    username = request.cookies.get('username')
    # use cookies.get(key) instead of cookies[key] to not get a
    # KeyError if the cookie is missing.
    
@app.route('/cookie', method='POST')
def cookie():
    resp = make_response(render_template(...))
    resp.set_cookie('username', 'the username')
    return resp

@app.route('/redirect')
def redirectMe():
    return redirect(url_for('login'))

def this_is_never_executed():
    pass

@app.route('/abortlogin')
def abortlogin():
    abort(401)
    this_is_never_executed()
    
    
# https://flask.palletsprojects.com/en/2.0.x/quickstart/#apis-with-json

def get_current_user():
    pass

def get_all_users():
    pass

@app.route("/me")
def me_api():
    user = get_current_user()
    return {
        "username": user.username,
        "theme": user.theme,
        "image": url_for("user_image", filename=user.image),
    }
    


@app.route("/users")
def users_api():
    users = get_all_users()
    return jsonify([user.to_json() for user in users])


@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return f'User {escape(username)}'


@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return f'Post {post_id}'


@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    # show the subpath after /path/
    return f'Subpath {escape(subpath)}'


@app.route('/')
def index():
    return 'index'


@app.route('/login')
def login():
    return 'login'


@app.route('/user/<username>')
def profile(username):
    return f'{username}\'s profile'


with app.test_request_context():
    print(url_for('index'))
    print(url_for('login'))
    print(url_for('login', next='/'))
    print(url_for('profile', username='John Doe'))
