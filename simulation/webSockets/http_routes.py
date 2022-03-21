# from app_init import flaskHttpApp

# http://eventlet.net/doc/patching.html
from enum import Enum
import http
from http.client import INTERNAL_SERVER_ERROR
import logging
from eventlet.greenpool import GreenPool
from eventlet.greenthread import GreenThread
import cachetools
from http import HTTPStatus
from typing import Any, Callable, Tuple, Type, TypeAlias, Generic, TypeVar
import uuid
from flask import request, make_response, abort, render_template, jsonify
from flask.wrappers import Response
from functools import wraps
import os
import json
from dotenv import load_dotenv
import eventlet
# eventlet.monkey_patch() # locate monkey_patching before all my own imports IF i do NOT want to patch some of my own modules.


from event_names import WebSocketClientEvent, WebSocketServerResponseEvent
from http_validators import validate_retailer_name, validate_retailer_sustainability, validate_retailer_strategy
from Bank import RetailerStrategyGPMultiplier, RetailerSustainabilityIntercept, ControlRetailer, InvalidRetailerReason
from app_init import flaskHttpApp
from app_config import SimulationConfig, SimulationIterationConfig
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
    # def foo(*args: str, **kwds: int): ...
    def decorated_function(*args:Any, **kwargs:Any):
        if request.args.get('GEMBER_API_KEY') and request.args.get('GEMBER_API_KEY') == os.getenv('APPKEY'):
            return view_function(*args, **kwargs)
        else:
            logging.debug('Unauthenticated client refused access.')
            abort(401)
    return decorated_function

def check_app_initialised(view_function:Callable):
    @wraps(view_function)
    def decorated_function(*args:Any, **kwargs:Any):
        if not gpApp.initialised():
            logging.debug('Uninitialised client -> refused access.')
            status=HTTPStatus.BAD_REQUEST
            abort(wrap_CORS_response(Response(
                'app must first be initialised to create a simulation environment', status=status)))
        return view_function(*args, **kwargs)
    return decorated_function



GreenThreadCallBack: TypeAlias = Callable[[GreenThread, list, dict],Any]
GreenThreadResultCallBack: TypeAlias = Callable[[GreenThread, Any, Any],Any]
GreenThreadResultCallBackSimple: TypeAlias = Callable[[Any],Any]




_RT = TypeVar("_RT")
class TypedGreenThread(GreenThread,Generic[_RT]):
    def __init__(self, gt:GreenThread):
        self.greenThread = gt
        result:_RT|None=None
        _completed:bool=False
     
    @property   
    def completed(self):
        return self._completed
    
    def link(self, func: Callable[[GreenThread, Any, Any], Any], *curried_args, **curried_kwargs):
        return self.greenThread.link(func, *curried_args, **curried_kwargs)
    
    # def linkWait(self, func: Callable[[GreenThread, _RT, list, dict],Any], *curried_args, **curried_kwargs):
    #     return self.greenThread.link(func, *curried_args, **curried_kwargs)
    
    def unlink(self, func: GreenThreadCallBack, *curried_args, **curried_kwargs):
        return self.greenThread.unlink(func, *curried_args, **curried_kwargs)
    
    def wait(self) -> _RT | None:
        x: _RT | None = self.greenThread.wait()  # type:ignore
        self._completed = True
        self.result = x
        taskResults[self] = x
        return x
    
    def getGreenThreadResult(self, callback: Callable[[_RT | None], Any]) -> Callable[[GreenThread, Any, Any], Any]:
        '''wrap the link func so that we can just handle the result of the thread'''
        def _greenThreadResultCallBack(gt: GreenThread, *args: list, **kwargs: dict):
            try:
                res = self.wait()
            except Exception as e:
                raise e
            try:
                return callback(res)
            except Exception as e:
                raise e
        return _greenThreadResultCallBack
    
    
class TypedGreenPool(GreenPool):
    def spawn(self, function:Callable[...,_RT], *args, **kwargs:Any) -> TypedGreenThread[_RT]:
        return TypedGreenThread(super().spawn(function, *args, **kwargs))



# Implement GreenThread result handlers as in docs: http://eventlet.net/doc/modules/greenthread.html#eventlet.greenthread.GreenThread
# http://eventlet.net/doc/modules/greenthread.html#eventlet.greenthread.GreenThread
tasks = cachetools.TTLCache[str, TypedGreenThread](maxsize=10000,ttl=10*60)
taskResults = cachetools.TTLCache[TypedGreenThread, Any](maxsize=10000,ttl=10*60)
# taskPresenters: dict[str, Callable[[Any], Any]] = {} 
dual_pool = TypedGreenPool(size=100) # Dont use python lib ThreadPool that will break eventlet threads https://bleepcoder.com/flask-socketio/201694856/emit-in-loop-not-sending-until-loop-completion-when-using

## ─── APP ROUTE HELPER FUNCTIONS ─────────────────────────────────────────────────


def _abortBadRetailerRequest(validateRetailer: InvalidRetailerReason):
    if validateRetailer == InvalidRetailerReason.invalidName:
        abort(wrap_CORS_response(Response(
            'retailer_name passed to simulation init request not found', status=HTTPStatus.NOT_FOUND)))
    elif validateRetailer == InvalidRetailerReason.invalidStrategy:
        abort(wrap_CORS_response(Response(
            'Strategy enum name passed to simulation init request not found', status=HTTPStatus.NOT_FOUND)))
    elif validateRetailer == InvalidRetailerReason.invalidSustainability:
        abort(wrap_CORS_response(Response(
            'Sustainability enum name passed to simulation init request not found', status=HTTPStatus.NOT_FOUND)))
    else:
        abort(wrap_CORS_response(Response(
            'Invalid data supplied to init-sim request', status=HTTPStatus.NOT_FOUND)))

# @require_appkey
# @flaskHttpApp.route('/init-new-sim', methods=['POST'])


def _loadSimulationId() -> str:
    data = _loadRequestData()
    if 'simulationId' not in data:
        abort(wrap_CORS_response(Response(
            'No Simulation ID supplied to run-full-sim request', status=HTTPStatus.NOT_FOUND)))
    simId = data['simulationId']
    return simId

# def require_queryparam(view_function:Callable[[str,str],Any], queryparam_name:str):
#     pass

# def require_simulationid(view_function:Callable):
#     @wraps(view_function)
#     # the new, post-decoration function. Note *args and **kwargs here.
#     # def foo(*args: str, **kwds: int): ...
#     def decorated_function(*args:Any, **kwargs:Any):
#         simId = _loadSimulationId()
#         setattr(request,'gember_args', object())
#         request.gember_args.__doc__ = 'custom args from the request for gember only'
#         setattr(request.gember_args,'simId', simId)
#     return decorated_function

# def require_simulation_config(view_function:Callable):
#     @wraps(view_function)
#     # the new, post-decoration function. Note *args and **kwargs here.
#     # def foo(*args: str, **kwds: int): ...
#     def decorated_function(*args:Any, **kwargs:Any):
#         simId = _loadSimulationId()
#         setattr(request,'gember_args', object())
#         request.gember_args.__doc__ = 'custom args from the request for gember only'
#         setattr(request.gember_args,'simId', simId)
#         data = _loadRequestData()
#         simConfig = SimulationIterationConfig.createFromDict(data)
#         setattr(request.gember_args, 'simConfig', simConfig)
#     return decorated_function


def eventlet_sleep_thread():
    eventlet.sleep(1)


def _loadRequestData():
    '''get the data from the request body combining and form fields in the request'''
    data = {}
    if request.data:
        data = {**data, **json.loads(request.data)}
    elif len(request.form) > 0:
        data = {**data, **request.form}
    return data


def _validateRetailerInRequestData(data: dict):

    valid_retailer_name = validate_retailer_name(
        data['retailer_name'])

    if not valid_retailer_name:
        return (InvalidRetailerReason.invalidName, None)

    valid_retailer_strategy = validate_retailer_strategy(
        data['retailer_name'], data['retailer_strategy'])
    if not valid_retailer_strategy:
        return (InvalidRetailerReason.invalidStrategy, None)

    valid_retailer_sustainability = validate_retailer_sustainability(
        data['retailer_name'], data['retailer_sustainability'])
    if not valid_retailer_sustainability:
        return (InvalidRetailerReason.invalidSustainability, None)

    return (InvalidRetailerReason.validRetailer,
            ControlRetailer(name=data['retailer_name'],
                            strategy=RetailerStrategyGPMultiplier[data['retailer_strategy']],
                            sustainability=RetailerSustainabilityIntercept[data['retailer_sustainability']]))

# ─── APP ROUTES ─────────────────────────────────────────────────────────────────

@require_appkey
@flaskHttpApp.route('/task-result', methods=['POST'])
def get_task_result():
    data = _loadRequestData()
    if 'taskId' not in data.keys():
        abort(HTTPStatus.BAD_REQUEST, 'No taskId in request')
    taskId: str = data['taskId']
    
    if taskId in taskResults:
        gt = tasks.pop(taskId)
        res = taskResults.pop(gt)
        response = wrap_CORS_response(
            make_response(jsonify(res)))
        return response
    elif taskId in tasks:
        return wrap_CORS_response(make_response(jsonify('Task still running'), HTTPStatus.PROCESSING))
    else:
        abort(404, 'Bad Request: taskId not found!')


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
    
    if flaskHttpApp.config["ALLOW_THREADING"]:
        
        # http://eventlet.net/doc/patching.html
        green_thread = dual_pool.spawn(_emitNEvents, N=20)
        if green_thread in taskResults:
            taskResults.pop(green_thread)
        tasks[taskId] = green_thread
        
        #BUG: This will cause a memory leak given enough time as this store should be on disk on a db....
        #  we can just delete old tasks by popping them once accessed as they should only be asked fro once if one client has the taskid.
        
        
        # do some other stuff in the main process ...
        # resultDf = async_result.get()
        # response = make_response(resultDf.to_json())
        statusId = HTTPStatus.ACCEPTED
        return wrap_CORS_response(make_response({'status': statusId, 'message': 'test-ws-event-memory_running', 'task_id': taskId}, statusId))
    else:
        _emitNEvents(100)
        statusId = HTTPStatus.OK
        return wrap_CORS_response(make_response({'status': statusId, 'message': 'test-ws-event-memory_ran', 'task_id': taskId}, statusId))


    

@require_appkey
@flaskHttpApp.route('/init-lazy', methods=['POST'])
def init_gpApp():
    '''Initialise the entire app, reading data sources etc'''
    if not gpApp.initialised():
        res = gpApp.initAppEnv()
        if res.initialised:
            return_status_code = HTTPStatus.OK
            return wrap_CORS_response(
                make_response({
                    'status': return_status_code,
                    'message': 'application initialised',
                }, return_status_code))
        else:
            abort(wrap_CORS_response(Response(
                'app failed to initialise', status=HTTPStatus.INTERNAL_SERVER_ERROR)))
    return_status_code = HTTPStatus.OK
    return wrap_CORS_response(make_response({
                    'status': return_status_code,
                    'message': 'application initialised',
                }, return_status_code))
    
@require_appkey
@flaskHttpApp.route('/load-entities', methods=['POST'])
def load_entities():
    '''Load the retailers and N (_from config_) customers with simulation level configuration also settable'''
    data = _loadRequestData()
    simConfig = SimulationIterationConfig.createFromDict(data) #INFO: NUM_CUSTOMERS N specified here
    simId, simType = gpApp.initSimulationSingleIterationEnvironment(
        simConfig=simConfig,
    )
    simEnv = gpApp.getSimulationEnvironmentUnsafe(
        simulationId=simId)
    entities = simEnv.entities
    return wrap_CORS_response(make_response(entities,HTTPStatus.OK))

@require_appkey
@flaskHttpApp.route('/retailer_names', methods=['GET'])
def get_retailer_names():
    simEnv = gpApp.getSimulationDummyEnvironment()
    retailerNames = {'retailer_names': simEnv.retailerNames}
    return wrap_CORS_response(make_response(retailerNames,HTTPStatus.OK))

    
@check_app_initialised
@require_appkey
@flaskHttpApp.route('/run-full-sim', methods=['POST'])
def run_simulation(**kwds:Any):
    '''Initialise a new single iteration simulation environment and start it.
        --
        Required query params: 
            - simulation configuration params
        '''
    if not gpApp.initialised():
        status = HTTPStatus.BAD_REQUEST
        abort(wrap_CORS_response(Response(
            'app must first be initialised to create a simulation environment', status=status)))

    data = _loadRequestData()
    simConfig = SimulationConfig.createFromDict(data)

    simId, simType = gpApp.initSimulationFullEnvironment(
        simConfig=simConfig,
    )
    
    simEnv = gpApp.getSimulationEnvironmentUnsafe(simulationId=simId)
    simData = simEnv.data

    taskId = str(uuid.uuid4())
    

    if flaskHttpApp.config["ALLOW_THREADING"]:
        # async_result = dual_pool.apply_async(
        #     lambda: gpApp.run_full_simulation(simulationId=simId, **kwds), callback=None)
        kwds = {
            **kwds,
            'simulationId': simId,
            'betweenIterationCallback': eventlet_sleep_thread
        }
        green_thread = dual_pool.spawn(
            gpApp.run_full_simulation, **kwds)
        green_thread.link(green_thread.getGreenThreadResult(
            lambda res: res if res is not None else None))
        if green_thread in taskResults:
            taskResults.pop(green_thread)
        tasks[taskId] = green_thread
        
        return_status_code = HTTPStatus.ACCEPTED
        return wrap_CORS_response(make_response({'status': return_status_code,
                                                 'message': 'simulation_running',
                                                 'task_id': taskId,
                                                 'simulation_id': simId,
                                                 'simulation_type': simType,
                                                 'simulation_data': simData,
                                                 }, return_status_code))
    else:
        df = gpApp.run_full_simulation(
            simulationId=simId, betweenIterationCallback=eventlet_sleep_thread, **kwds)
        return_status_code = HTTPStatus.ACCEPTED
        return wrap_CORS_response(make_response({'status': return_status_code,
                                                 'message': 'simulation_ran',
                                                 'task_id': taskId,
                                                 'simulation_id': simId,                                                 
                                                 'simulation_type': simType,
                                                 'simulation_data': simData,
                                                 }, return_status_code))
        
@check_app_initialised
@require_appkey
@flaskHttpApp.route('/sim-result/<string:simId>', methods=['GET'])
def get_simulation_result(simId:str):
    simEnv = gpApp.getSimulationEnvironment(simulationId=simId,throw=False)
    if simEnv is not None:
        return wrap_CORS_response(make_response(simEnv.summarise_simulation_to_dict()))
        # return wrap_CORS_response(make_response(simEnv.summarise_simulation_to_df().to_dict()))
    else:
        abort(wrap_CORS_response(Response(
                'Simulation Environment not found', status=HTTPStatus.NOT_FOUND)))

@check_app_initialised
@require_appkey
@flaskHttpApp.route('/sim-compare', methods=['GET'])
def get_simulation_history():
    '''allowed measureType:
    - sales_volume
    - gp_issued
    - market_share
    - total_sales_price
    - total_sales_price_less_gp
    - * Not currently -> total_sales_price_by_item *
    '''
    data = _loadRequestData()
    simulationIds = str(data['simulationIds']).split(',')
    retailerName = data['retailerName']
    measureType = data['measureType']
    return _get_simulation_history(
        simulationIds=simulationIds,
        retailerName=retailerName,
        measureType=measureType,
        )

def _get_simulation_history(
    simulationIds:list[str], 
    retailerName:str, # 📒 Cant use retailer.id as this will change accross simulations...
    measureType:str,
    ):
    '''allowed measureType:
    - sales_volume
    - gp_issued
    - market_share
    - total_sales_price
    - total_sales_price_less_gp
    - * Not currently -> total_sales_price_by_item *
    '''
    
    simEnvs:dict[str,Any] = {}
    for simId in simulationIds:
        simEnv = gpApp.getSimulationEnvironment(simulationId=simId,throw=False)
        if simEnv is not None:
            simEnvs[simId] = [simEnv.simulationConfig.toJson(), simEnv.summarise_simulation_to_dict(forRetailer=retailerName)]
    if simEnvs:
        return wrap_CORS_response(make_response(simEnvs, HTTPStatus.OK))
    else:
        return wrap_CORS_response(make_response('No simulations found with simulationIds requested', HTTPStatus.NOT_FOUND))
    
    
    # TODO: 1. Get the params for this from the request data , body, form
        # 2. comprehension map the ids -> dict[id,simEnv] lookup of simEnvs (GemberAppConfig, finalRunningAv. result) 
        #   where they exist.
        # 3. in the above comprehension, only get the retailer and the measureTyep which will 
        #   be one number for each simulation -> this can be shown in a barchart where 
        #   each xlabel is the params that led to that result, 
        #   so for that we need the simEnv GemberAppConfig information in each of the filters above
        # 4. return in this in an object that contains: data as a dict of simId to simInfo, 
        #   then aggregation information that 
        # 5. 
        
    pass
    

@check_app_initialised
@require_appkey
@flaskHttpApp.route('/run-scenario', methods=['POST'])
def run_realtime_scenario():
    '''Initialise a new scenario runner simulation environment and start it.
        --
        Required query params: 
            - simulation configuration params
        '''
#     if not gpApp.initialised():
#         status = HTTPStatus.BAD_REQUEST
#         abort(wrap_CORS_response(Response(
#             'app must first be initialised to create a simulation environment', status=status)))

#     data = _loadRequestData()
#     simConfig = SimulationIterationConfig.createFromDict(data)

#     simId = gpApp.initSimulationScenarioRunEnvironment(
#         simConfig=simConfig,
#     )

#     taskId = str(uuid.uuid4())
#     # This needs to be updated to return a simulation environment immediately that can be
#     if flaskHttpApp.config["ALLOW_THREADING"]:
#         # http://eventlet.net/doc/patching.html
#         green_thread = dual_pool.spawn(
#             lambda: gpApp.run_scenario(simulationId=simId))
#         green_thread.link(green_thread.getGreenThreadResult(
#             lambda res: res[0].to_json() if res is not None else None))
#         if green_thread in taskResults:
#             taskResults.pop(green_thread)
#         tasks[taskId] = green_thread

#         statusId = HTTPStatus.ACCEPTED
#         return wrap_CORS_response(make_response({'status': statusId, 'message': 'scenario_running', 'task_id': taskId}, statusId))
#     else:
#         abort(wrap_CORS_response(Response(
#             'Cant run scenarios in synchronous mode as will block the rest of the app and therefore wont be able to adjust parameters to continuously parameterise the scenario', status=HTTPStatus.METHOD_NOT_ALLOWED)))
    raise NotImplementedError('must implement gpApp.run_scenario(simulationId=simId) first')
        

@check_app_initialised
@require_appkey
@flaskHttpApp.route('/run-single-iteration', methods=['POST'])
def run_single_iteration():
    '''Initialise a new single iteration simulation environment and start it.
        --
        Required query params: 
            - simulation configuration params
        '''
    
        
    data = _loadRequestData()
    simConfig = SimulationIterationConfig.createFromDict(data)
    
    simId,simType = gpApp.initSimulationSingleIterationEnvironment(
        simConfig=simConfig,
    )
    
    adjDone = _setRetailerParamasForSimulationEnv(simulationId=simId,blocking=True)
    if not adjDone:
        abort(wrap_CORS_response(Response('Failed to parameterize retailer',HTTPStatus.INTERNAL_SERVER_ERROR)))
    simEnv = gpApp.getSimulationEnvironmentUnsafe(simulationId=simId)
    simData = simEnv.data
    taskId = str(uuid.uuid4())
    # This needs to be updated to return a simulation environment immediately that can be 
    if flaskHttpApp.config["ALLOW_THREADING"]:
        # http://eventlet.net/doc/patching.html
        green_thread = dual_pool.spawn(
            lambda : gpApp.run_isolated_iteration(simulationId=simId))
        green_thread.link(green_thread.getGreenThreadResult(lambda res: res[0] if res is not None else None))
        if green_thread in taskResults:
            taskResults.pop(green_thread)
        tasks[taskId] = green_thread
        
        statusId = HTTPStatus.ACCEPTED
        return wrap_CORS_response(make_response({
            'status': statusId, 
            'message': 'single_iteration_running', 
            'task_id': taskId,
            'simulation_data': simData,
            'simulation_type': simType,
            }, statusId))
    else:
        df = gpApp.run_isolated_iteration(simulationId=simId)
        statusId = HTTPStatus.OK
        return wrap_CORS_response(make_response({
            'status': statusId, 
            'message': 'single_iteration_ran', 
            'task_id': taskId,
            'simulation_type': simType,
            'simulation_data': simData,
            }, statusId))


@check_app_initialised
@require_appkey
@flaskHttpApp.route('/app-config', methods=['POST'])
def get_sim_config():
    statusId = HTTPStatus.OK
    simId = _loadSimulationId()
    simConfig = gpApp.getSimConfig(simulationId=simId)
    if simConfig is None:
        abort(wrap_CORS_response(Response(
            'No simulation env found', status=HTTPStatus.NOT_FOUND)))
    else:
        return wrap_CORS_response(make_response(jsonify(simConfig.toJson()), statusId))
    

@check_app_initialised
@require_appkey
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


@check_app_initialised
@require_appkey
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
        logging.debug(e)
        raise e


@check_app_initialised
@require_appkey
@flaskHttpApp.route('/adjust-retailer', methods=['POST'])
def adjust_retailer_in_sim(*args, **kwargs):
    simId = _loadSimulationId()
    adjQueued = _setRetailerParamasForSimulationEnv(simulationId=simId, *args, **kwargs)
    if adjQueued:
        return wrap_CORS_response(make_response({
            'status': HTTPStatus.ACCEPTED, 
            'message': 'retailer_asjustment_accepted',
            }, HTTPStatus.ACCEPTED))
    else:
        abort(wrap_CORS_response(Response(
            '', status=HTTPStatus.INTERNAL_SERVER_ERROR)))

def _setRetailerParamasForSimulationEnv(simulationId:str,blocking:bool=False,*args,**kwargs):
    data = _loadRequestData()
    validateRetailer, controlRetailer = _validateRetailerInRequestData(data)
    if validateRetailer != InvalidRetailerReason.validRetailer:
        _abortBadRetailerRequest(validateRetailer=validateRetailer)
    elif controlRetailer is not None:
        adjQueued = gpApp.adjustSimParameters(simulationId=simulationId, controlRetailer=controlRetailer, blocking=blocking)
        return adjQueued
    else:
        return None


@require_appkey
@flaskHttpApp.route('/ws/event-names-cat', methods=['GET'])
def get_all_accepted_ws_event_names():
    eventNames = list(
        [w.value for w in WebSocketClientEvent.__members__.values()])
    return wrap_CORS_response(Response({'data': eventNames}, status=HTTPStatus.OK))

@require_appkey
@flaskHttpApp.route('/ws/event-response-names-cat', methods=['GET'])
def get_all_accepted_ws_response_event_names():
    eventNames = dict({name: value for (name, value)
                      in RetailerStrategyGPMultiplier.__members__.items()})
    return wrap_CORS_response(Response({'data': eventNames}, status=HTTPStatus.OK))

@require_appkey
@flaskHttpApp.route('/strategy-names-cat', methods=['GET'])
def getStrategyValueMap():
    eventNames = dict({name: value for (name, value)
                      in RetailerStrategyGPMultiplier.__members__.items()})
    return wrap_CORS_response(Response({'data': eventNames}, status=HTTPStatus.OK))


@require_appkey
@flaskHttpApp.route('/sustainability-names-cat', methods=['GET'])
def getSustainabilityValueMap():
    eventNames = list(
        [w.value for w in RetailerSustainabilityIntercept.__members__.values()])
    return wrap_CORS_response(Response({'data': eventNames}, status=HTTPStatus.OK))


@check_app_initialised
@require_appkey
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


@require_appkey
@flaskHttpApp.route('/start', methods=['GET'])
def startApp():
    if not gpApp.initialised():
        gpApp.initAppEnv()
    run_single_iteration() # if needs api key, can copy the logic from this function here...
        
    


@flaskHttpApp.route('/starting-state', methods=['GET'])
def startingState():

    resp = wrap_CORS_response(make_response())
    resp.set_cookie('username', 'the username')
    return resp
    # use cookies.get(key) instead of cookies[key] to not get a
    # KeyError if the cookie is missing.


flaskHttpAppWithRoutes = flaskHttpApp
