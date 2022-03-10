# from app_init import flaskHttpApp

from multiprocessing.pool import ThreadPool, AsyncResult, Pool
from http import HTTPStatus
from typing import Any, Callable
import uuid
from flask import request, make_response, abort, render_template, jsonify
from flask.wrappers import Response
from functools import wraps
import os
import json
from dotenv import load_dotenv


from event_names import WebSocketClientEvent, WebSocketServerResponseEvent
from http_validators import validate_retailer_name, validate_retailer_sustainability, validate_retailer_strategy
from Bank import GPStrategyMultiplier, RetailerSustainabilityIntercept
from app_init import flaskHttpApp
from app_globals import gpApp, flaskHttpAppConfig
for k in flaskHttpAppConfig:
    flaskHttpApp.config[k] = flaskHttpAppConfig[k]
    

def wrap_CORS_response(response: Response):
    response.headers['Access-Control-Allow-Origin'] = request.origin
    return response


def thread_caller(fn: Callable[[], Any],
                  callback: Callable[[], Any] | None = None,
                  error_callback: Callable[[Exception], Any] | None = None, *args, **kwargs):
    try:
        fn()
    except Exception as e:
        if error_callback is not None:
            error_callback(e)
    if callback is not None:
        return callback()


load_dotenv()

# The actual decorator function


def require_appkey(view_function:Callable):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if request.args.get('GEMBER_API_KEY') and request.args.get('GEMBER_API_KEY') == os.getenv('APPKEY'):
            return view_function(*args, **kwargs)
        else:
            print('Unauthenticated client refused access.')
            abort(401)
    return decorated_function

# @flaskHttpApp.route('/')
# @flaskHttpApp.route('/hello')
# def hello():
#     return 'Hello, World!'


tasks: dict[str, AsyncResult] = {}
taskPresenters: dict[str, Callable[[Any], Any]] = {}
dual_pool = Pool(processes=2)


@flaskHttpApp.route('/')
def index():
    return render_template('index.html')


@flaskHttpApp.route('/hello')
def hello():
    return 'Hello, World!'


@flaskHttpApp.route('/anon')
def anon():
    return indexwName('Client')


@flaskHttpApp.route('/name/<name>')
def indexwName(name):
    return make_response(render_template('tut_my_first_template.html',
                                         name=name, company='gember.inc'))


@flaskHttpApp.route('/test', methods=['GET'])
def test():
    return jsonify('Test Response')


@flaskHttpApp.route('/test-ws-event-memory', methods=['GET'])
def testWsEventMemory():
    taskId = str(uuid.uuid4())

    def _emitNEvents(N: int):
        for i in range(N):
            gpApp._emit_event(WebSocketServerResponseEvent.message_received, {
                              'data': f'test message {N}'})
    if isinstance(dual_pool, ThreadPool):
        if flaskHttpApp.config["ALLOW_THREADING"]:
            async_result = dual_pool.apply_async(
                _emitNEvents, args=[2], kwds={}, callback=None)
            tasks[taskId] = async_result
            #BUG: This will cause a memory leak given enough time as this store should be on disk on a db....
            #  we can just delete old tasks by popping them once accessed as they should only be asked fro once if one client has the taskid.
            taskPresenters[taskId] = lambda res: res.to_json()
            # do some other stuff in the main process ...
            # resultDf = async_result.get()
            # response = make_response(resultDf.to_json())
            statusId = HTTPStatus.ACCEPTED
            return wrap_CORS_response(make_response({'status': statusId, 'message': 'test-ws-event-memory_running', 'task_id': taskId}, statusId))
        else:
            _emitNEvents(100)
            statusId = HTTPStatus.OK
            return wrap_CORS_response(make_response({'status': statusId, 'message': 'test-ws-event-memory_ran', 'task_id': taskId}, statusId))

    else:
        abort(401, 'Flask Server isnt running on the main thread...')


@require_appkey
@flaskHttpApp.route('/init', methods=['POST'])
def init_simulation():
    print('init gpApp')
    response = wrap_CORS_response(make_response({}))
    if not gpApp.initialised():
        valid_retailer_name = validate_retailer_name(
            request.form['retailer_name'])
        if valid_retailer_name:
            valid_retailer_strategy = validate_retailer_strategy(
                request.form['retailer_name'], request.form['retailer_strategy'])
            valid_retailer_sustainability = validate_retailer_sustainability(
                request.form['retailer_name'], request.form['retailer_sustainability'])
            if valid_retailer_strategy and valid_retailer_sustainability:
                (_, entities) = gpApp.initNewSim()

                response = wrap_CORS_response(make_response(entities))
                # response.headers['Access-Control-Allow-Origin'] = request.origin
            else:
                abort(wrap_CORS_response(Response(
                    'Strategy / Sustainability enum name passed to simulation init request not found', status=404)))
        else:
            abort(wrap_CORS_response(Response(
                'retailer_name passed to simulation init request not found', status=404)))
    return wrap_CORS_response(make_response(gpApp.initialEntitiesSnapshot))


@require_appkey
@flaskHttpApp.route('/adjust-retailer', methods=['POST'])
def adjust_retailer_in_sim():
    response = wrap_CORS_response(make_response({}))
    kwds = {}
    data = {}
    if request.data:
        data = {**data, **json.loads(request.data)}
    elif len(request.form) > 0:
        data = {**data, **request.form}

    if 'simulation_id' in data:
        simId = data['simulation_id']
        valid_simId = gpApp.getSimulationEnvironment(
            simulationId=simId) is not None
    else:
        statusId = 404
        abort(wrap_CORS_response(Response(
            'retailer_name passed to adjust-retailer POST request not found', status=statusId)))

    if 'retailer_name' in data:
        retailerName = data['retailer_name']
        valid_retailer_name = validate_retailer_name(retailerName)
    else:
        statusId = 404
        abort(wrap_CORS_response(Response(
            'retailer_name passed to adjust-retailer POST request not found', status=statusId)))

    valid_retailer_strategy = False
    valid_retailer_sustainability = False
    retailerStrategy = ''
    retailerSustainability = ''
    if 'retailer_strategy' in data:
        retailerStrategy = data['retailer_strategy']
        valid_retailer_strategy = validate_retailer_strategy(
            retailerName, retailerStrategy)

    if 'retailer_sustainability' in data:
        retailerSustainability = data['retailer_sustainability']
        valid_retailer_strategy = validate_retailer_strategy(
            retailerName, retailerSustainability)

    if valid_simId and valid_retailer_strategy and valid_retailer_sustainability:
        taskId = gpApp.adjustSimParameters(simId, retailerName,
                                           GPStrategyMultiplier[retailerStrategy],
                                           RetailerSustainabilityIntercept[retailerSustainability])
        statusId = HTTPStatus.ACCEPTED
        return wrap_CORS_response(make_response({'status': statusId, 'message': 'retailer_asjustment_accepted', 'task_id': taskId}, statusId))

    else:
        statusId = 404
        abort(wrap_CORS_response(Response(
            'Strategy / Sustainability enum name passed to simulation init request not found', status=statusId)))

    return wrap_CORS_response(make_response(gpApp.initialEntitiesSnapshot))


@require_appkey
@flaskHttpApp.route('/run', methods=['POST'])
def run_isolated_simulation():
    print('Running isolated iteration example')
    if not gpApp.initialised():
        abort(403, 'Cant run a simulation when the app is not Initialised yet.')

    # T1 = Thread(target=gpApp.run, args=(), kwargs={}, name="simulation_runner_thread")
    # T1.start()
    # resultDf = T1.join()

    taskId = str(uuid.uuid4())
    if isinstance(dual_pool, ThreadPool):
        if flaskHttpApp.config["ALLOW_THREADING"]:
            async_result = dual_pool.apply_async(
                gpApp.run_isolated_iteration, args=(), kwds={}, callback=None)
            tasks[taskId] = async_result
            #BUG: This will cause a memory leak given enough time as this store should be on disk on a db....
            #  we can just delete old tasks by popping them once accessed as they should only be asked fro once if one client has the taskid.
            taskPresenters[taskId] = lambda res: res.to_json()
            # do some other stuff in the main process ...
            # resultDf = async_result.get()
            # response = make_response(resultDf.to_json())
            statusId = HTTPStatus.ACCEPTED
            return wrap_CORS_response(make_response({'status': statusId, 'message': 'simulation_running', 'task_id': taskId}, statusId))
        else:
            df = gpApp.run_isolated_iteration
            statusId = HTTPStatus.OK
            return wrap_CORS_response(make_response({'status': statusId, 'message': 'simulation_ran', 'task_id': taskId}, statusId))

    else:
        abort(401, 'Flask Server isnt running on the main thread...')


@require_appkey
@flaskHttpApp.route('/run-full-sim', methods=['POST'])
def run_simulation():
    if isinstance(dual_pool, ThreadPool):
        kwds = {}
        data = {}
        if request.data:
            data = {**data, **json.loads(request.data)}
        elif len(request.form) > 0:
            data = {**data, **request.form}
        if 'maxN' in data:
            kwds['maxN'] = int(data['maxN'])
        if 'convergence_threshold' in data:
            kwds['convergence_threshold'] = float(
                data['convergence_threshold'])
        taskId = str(uuid.uuid4())
        simId = gpApp.simulationEnvironmentToken()
        if flaskHttpApp.config["ALLOW_THREADING"]:
            async_result = dual_pool.apply_async(
                lambda: gpApp.run_full_simulation(simulationId=simId, **kwds), callback=None)
            tasks[taskId] = async_result
            #BUG: This will cause a memory leak given enough time as this store should be on disk on a db....
            #  we can just delete old tasks by popping them once accessed as they should only be asked fro once if one client has the taskid.
            taskPresenters[taskId] = lambda res: res.to_json()
            # do some other stuff in the main process ...
            # resultDf = async_result.get()

            # response = make_response(resultDf.to_json())
            return_status_code = HTTPStatus.ACCEPTED
            return wrap_CORS_response(make_response({'status': return_status_code,
                                                     'message': 'simulation_running',
                                                     'task_id': taskId,
                                                     'simulation_id': simId
                                                     }, return_status_code))
        else:
            df = gpApp.run_full_simulation(simulationId=simId, **kwds)
            return_status_code = HTTPStatus.ACCEPTED
            return wrap_CORS_response(make_response({'status': return_status_code,
                                                     'message': 'simulation_ran',
                                                     'task_id': taskId,
                                                     'simulation_id': simId
                                                     }, return_status_code))

        # response.headers['Access-Control-Allow-Origin'] = request.origin
        # return response

    else:
        abort(401, 'Flask Server isnt running on the main thread...')


def get_task_result():
    taskId: str = request.args['taskId']
    if taskId in tasks:
        async_result = tasks[taskId]
        if async_result.successful():
            result_df = async_result.get()
            response = wrap_CORS_response(
                make_response(taskPresenters[taskId](result_df)))
            # response.headers['Access-Control-Allow-Origin'] = request.origin
            return response
        else:
            abort(403, 'Task still running')
    else:
        abort(404, 'Bad Request: taskId not found!')


@flaskHttpApp.route('/item-sales', methods=['GET'])
def item_sales():
    query_params = request.args.to_dict()
    KEY = 'item-name'
    if KEY not in query_params.keys():
        return abort(Response(f'Bad query for route, must contain {KEY} in query params.', status=403))
    itemName = query_params[KEY]
    KEY = 'simulation-id'
    if KEY not in query_params.keys():
        return abort(Response(f'Bad query for route, must contain {KEY} in query params.', status=403))
    simId = query_params[KEY]
    return wrap_CORS_response(make_response(gpApp.salesForItem(simulationEnvId=simId, itemName=itemName).toJson()))


@flaskHttpApp.route('/app/purchase-delay/<delay>', methods=['POST'])
def adjust_purchases_delay_seconds(delay: float = 1.0):
    try:
        # query_params = request.args.to_dict()
        # KEY = 'delay'
        # if KEY not in query_params.keys():
        #     return abort(Response(f'Bad query for route, must contain {KEY} in query params.', status=403))
        # el
        if isinstance(delay, float) or isinstance(delay, int):
            gpApp.secondsBetweenPurchases = float(delay)
        elif isinstance(delay, str) and str(delay).isdecimal():
            gpApp.secondsBetweenPurchases = float(delay)
        else:
            return abort(Response(f'Bad query for route, must contain int value for delay.', status=403))
        response = wrap_CORS_response(
            Response({'message': 'success'}, status=HTTPStatus.ACCEPTED))
    except Exception as e:
        print(e)
        raise e


@flaskHttpApp.route('/ws/event-names-cat', methods=['GET'])
def get_all_accepted_ws_event_names():
    eventNames = list(
        [w.value for w in WebSocketClientEvent.__members__.values()])
    return wrap_CORS_response(Response({'data': eventNames}, status=HTTPStatus.OK))


@flaskHttpApp.route('/ws/event-response-names-cat', methods=['GET'])
def get_all_accepted_ws_response_event_names():
    eventNames = dict({name: value for (name, value)
                      in GPStrategyMultiplier.__members__.items()})
    return wrap_CORS_response(Response({'data': eventNames}, status=HTTPStatus.OK))


@flaskHttpApp.route('/strategy-names-cat', methods=['GET'])
def getStrategyValueMap():
    eventNames = dict({name: value for (name, value)
                      in GPStrategyMultiplier.__members__.items()})
    return wrap_CORS_response(Response({'data': eventNames}, status=HTTPStatus.OK))


@flaskHttpApp.route('/sustainability-names-cat', methods=['GET'])
def getSustainabilityValueMap():
    eventNames = list(
        [w.value for w in RetailerSustainabilityIntercept.__members__.values()])
    return wrap_CORS_response(Response({'data': eventNames}, status=HTTPStatus.OK))


@flaskHttpApp.route('/transactions', methods=['GET'])
def entity_transactions():
    query_params = request.args.to_dict()
    KEY = 'entityid'
    if KEY not in query_params.keys():
        return abort(Response(f'Bad query for route, must contain {KEY} in query params.', status=403))
    entityId = query_params[KEY]
    KEY = 'simulation-id'
    if KEY not in query_params.keys():
        return abort(Response(f'Bad query for route, must contain {KEY} in query params.', status=403))
    simId = query_params[KEY]
    return wrap_CORS_response(make_response({
        'transactionsFromEntity': gpApp.transactionsFromEntity(simulationEnvId=simId, entityId=entityId),
        'transactionsToEntity': gpApp.transactionsToEntity(simulationEnvId=simId, entityId=entityId)
    }))

# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if valid_login(request.form['username'],
#                        request.form['password']):
#             return log_the_user_in(request.form['username'])
#         else:
#             error = 'Invalid username/password'
#     # the code below is executed if the request method
#     # was GET or the credentials were invalid
#     return render_template('login.html', error=error)


@flaskHttpApp.route('/connect')
def connect():
    response = make_response(render_template('connect.html', json={}))
    response.headers['X-Parachutes'] = 'parachutes are cool'
    return wrap_CORS_response(response)


@flaskHttpApp.route('/start', methods=['GET'])
def startApp():
    if not gpApp.initialised():
        (_, entities) = gpApp.initNewSim()
        # TODO v1.0: This should then get app to push an event called initial state to the websocket whcih tells us we can load views,
        #    show a loading spinner until then.
        # TODO v1.2: Subscribe to stream
        response = wrap_CORS_response(make_response(render_template(
            'connect.html', json=entities)))
        response.headers['X-Parachutes'] = 'parachutes are cool'
        return response


@flaskHttpApp.route('/starting-state', methods=['GET'])
def startingState():

    resp = wrap_CORS_response(make_response())
    resp.set_cookie('username', 'the username')
    return resp
    # use cookies.get(key) instead of cookies[key] to not get a
    # KeyError if the cookie is missing.


flaskHttpAppWithRoutes = flaskHttpApp
