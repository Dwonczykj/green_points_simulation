from __future__ import annotations
# import queue
# import threading
# from types import TracebackType
# import uuid
# import gevent
# from geventwebsocket import WebSocketError
# from geventwebsocket.websocket import WebSocket
# from geventwebsocket.handler import WebSocketHandler
# # from geventwebsocket.logging import create_logger, getLogger, StreamHandler
# import logging
# from gevent.lock import Semaphore
# from gevent.exceptions import ConcurrentObjectUseError
# from logging import getLogger

# from queue_main_global import QueueHolder
# import json
import abc
from colorama import Fore, Back, Style
from flask_socketio import SocketIO
import traceback
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from Bank import debug
from event_names import WebSocketClientEvent, WebSocketServerResponseEvent, MySocketIONamespaces
# from web_socket_wrapper import IWrapWebSocket
if TYPE_CHECKING:
    from GreenPointsSimulation import GreenPointsLoyaltyApp
    
# #somewhere accessible to both:
# wsock_callback_queue = QueueHolder.global_callback_queue


class WSEvent:
    def __init__(self, eventName: WebSocketServerResponseEvent|WebSocketClientEvent, data: Any):
        self._eventName = eventName
        self._data = data
    
    @property
    def eventName(self):
        return self._eventName
    
    @property
    def eventNameStr(self):
        return str(self._eventName.value)
    
    @property
    def data(self):
        return self._data

    def __str__(self):
        return str(self.__dict__)
    

class WSResponseEvent(WSEvent):
    def __init__(self, eventName: WebSocketServerResponseEvent, data: Any):
        super().__init__(eventName, data)
        self._responseEventName = eventName
        
    @property
    def eventName(self):
        return self._responseEventName
    
class IWebSocketsStack(metaclass=abc.ABCMeta):
    
    debug: bool = debug
    
    @abc.abstractproperty
    def webSocketOpen(self):
        pass
        
    @abc.abstractmethod
    def send(self, eventName: WebSocketServerResponseEvent, data: Any):
        pass
    
    @abc.abstractmethod
    def broadcast(self, eventName: WebSocketServerResponseEvent, data: Any):
        pass
    
    @abc.abstractmethod
    def receive(self):
        pass



class WebSocketsStack(IWebSocketsStack):
    '''Singleton: Call getInstance() to get [MyWebSocket]'''
    __instance: WebSocketsStack | None = None
    
    debug:bool = debug
    
    

    @staticmethod
    def getInstance(gpApp: GreenPointsLoyaltyApp,socketio:SocketIO):
        """ Static access method. """
        if WebSocketsStack.__instance == None:
            WebSocketsStack(gpApp,socketio)
        assert isinstance(WebSocketsStack.__instance, WebSocketsStack)
        return WebSocketsStack.__instance

    def __init__(self, gpApp: GreenPointsLoyaltyApp,socketio:SocketIO):
        """ Virtually private constructor. """
        if WebSocketsStack.__instance != None:
            raise Exception("WebSocketsStack class is a singleton!")
        else:
            WebSocketsStack.__instance = self
            self.gpApp = gpApp
            self._socketio = socketio
            
            

    @property
    def webSocketOpen(self):
        return True
    
    _channelMap:dict[str,str] = {v.value: k for k, l in {
        MySocketIONamespaces.global_namespace.value: [
            WebSocketServerResponseEvent.gpApp_initialised,
            WebSocketServerResponseEvent.unknown_client_event_response,
            WebSocketServerResponseEvent.message_received,
            WebSocketServerResponseEvent.purchase_delay,
            WebSocketServerResponseEvent.app_state_loaded,
            WebSocketServerResponseEvent.entity_updated,
            WebSocketServerResponseEvent.bank_account_added,
            WebSocketServerResponseEvent.crypto_transfer_requested,
            WebSocketServerResponseEvent.crypto_transfer_completed,
            WebSocketServerResponseEvent.customer_checked_out,
            WebSocketServerResponseEvent.customer_added_item_to_basket,
            WebSocketServerResponseEvent.retailer_strategy_changed,
            WebSocketServerResponseEvent.retailer_sustainbility_changed],
        MySocketIONamespaces.simulation.value: [
            WebSocketServerResponseEvent.simulation_initialised,
            WebSocketServerResponseEvent.simulation_iteration_completed,
            WebSocketServerResponseEvent.simulation_ran,
            WebSocketServerResponseEvent.simulation_already_running,
            ],
        MySocketIONamespaces.transactions.value: [
            WebSocketServerResponseEvent.bank_transaction_created,
            WebSocketServerResponseEvent.bank_transaction_completed,
            WebSocketServerResponseEvent.bank_transaction_failed,
            ],
    }.items() for v in l}
    
    def send(self, eventName: WebSocketServerResponseEvent, data: Any, namespace:MySocketIONamespaces|None=None):
        self.broadcast(eventName, data, namespace=namespace)
    
    def broadcast(self, eventName: WebSocketServerResponseEvent, data: Any, namespace: MySocketIONamespaces | None = None):
        self._socketio.emit(eventName.value, data, namespace=(
            WebSocketsStack._channelMap[eventName.value] if namespace is None else namespace.value))
        # socketio.emit('json', {'type': eventName.value, 'data': data}, namespace=(
        #     WebSocketsStack._channelMap[eventName.value] if namespace is None else namespace.value))
    
    def receive(self):
        raise NotImplementedError()



# class WebSocketsStackOld(IWebSocketsStack):
#     '''Singleton: Call getInstance() to get [MyWebSocket]'''
#     __instance: WebSocketsStack | None = None
    
#     debug:bool = debug
    
#     __event_emission_queue: queue.Queue[WSResponseEvent] = queue.Queue()

#     @staticmethod
#     def getInstance(gpApp: GreenPointsLoyaltyApp):
#         """ Static access method. """
#         if WebSocketsStack.__instance == None:
#             WebSocketsStack(gpApp)
#         assert isinstance(WebSocketsStack.__instance, WebSocketsStack)
#         return WebSocketsStack.__instance

#     def __init__(self, gpApp: GreenPointsLoyaltyApp):
#         """ Virtually private constructor. """
#         if WebSocketsStack.__instance != None:
#             raise Exception("WebSocketsStack class is a singleton!")
#         else:
#             WebSocketsStack.__instance = self
#             self._webSocketsRawList: dict[str,IWrapWebSocket] = {}
#             self.gpApp = gpApp
#             _numThreadsThatCanSendConcurrently = 1
#             self._lock = Semaphore(_numThreadsThatCanSendConcurrently)

#     @property
#     def webSocketOpen(self):
#         return bool(self._webSockets)
    
#     def flush_event_emissions_queue(self):
#         while True:
#             try:
#                 message = WebSocketsStack.__event_emission_queue.get(False)  # doesn't block
#                 self._emit_all_sockets(eventName=message.eventName, data=message.data)
#                 if WebSocketsStack.debug:
#                     logging.debug(Fore.YELLOW + f'{message.eventName} emitted...' + Style.RESET_ALL)
#             except queue.Empty:  # raised when queue is empty
#                 break

#     # def run_queue_check_loop(self):
#         # The below doesnt work as websocket.send fails inside a new thread...
#         # threading.Thread(target=self.run_while_true_queue_checker, args=())\
#         #     .start()
            
#     def run_while_true_queue_checker(self):
#         try:
#             while True:
#                 self.flush_event_emissions_queue()
#         except Exception as e:
#             logging.debug(e)
            

#     def append(self, ws: WebSocket):
#         if self.isLiveSocket(ws) and isinstance(ws.environ,dict):
#             # self._webSocketsRawList[self._getWsOrigin(ws)] = ws
#             key = self._getWsOrigin(ws)
#             logging.debug(Fore.YELLOW + Style.DIM + f'Adding ws with origin: {key}' + Style.RESET_ALL)
#             self._webSocketsRawList[key] = IWrapWebSocket(ws)
#             # ws.handler = StreamHandler()

#     def removeWS(self, ws: IWrapWebSocket):
#         # import traceback
#         key = next((k for k,v in self._webSocketsRawList.items() if v == ws),None) if self._webSocketsRawList is not None else None
#         if key:
#             logging.debug(Fore.YELLOW + Style.DIM + f'Removing WS: {key}' + Style.RESET_ALL)
#             # logging.debug(traceback.format_exc())
#             # logging.debug(traceback.format_stack())
#             self.remove(key)
    
#     def remove(self, keyOrigin:str):
#         ws = self._webSocketsRawList.pop(keyOrigin)
#         ws.close(code=WebSocket.OPCODE_CLOSE, message=b'Websocket was closed')

#     def isLiveSocket(self, ws: WebSocket|IWrapWebSocket):
#         if ws.closed:
#             return False
#         elif ws.origin == '':
#             return False
#         elif isinstance(ws.environ, dict):
#             if ('HTTP_HOST' in ws.environ and ws.environ['HTTP_HOST'] == '127.0.0.1:8443') \
#                 and ('HTTP_ORIGIN' in ws.environ and ws.environ['HTTP_ORIGIN'] != ''):
#                 return True
#         else:
#             return False
        
        
#         # return bool((not ws.closed)
#         #             and ws.origin != ''
#         #             and isinstance(ws.environ, dict)
#         #             and ('HTTP_HOST' in ws.environ
#         #                  and ws.environ['HTTP_HOST'] == '127.0.0.1:8443')
#         #             and ('HTTP_ORIGIN' in ws.environ
#         #                  and ws.environ['HTTP_ORIGIN'] != '')
#         #             )

#     def isDeadSocket(self, ws: WebSocket | IWrapWebSocket):
#         return not self.isLiveSocket(ws)

#     def send(self, eventName: WebSocketServerResponseEvent, data: Any):
#         return self.emitQ(eventName, data)
    
#     def _getWsOrigin(self, ws:WebSocket|IWrapWebSocket) -> str:
#         if isinstance(ws.environ, dict):
#             return ws.environ['HTTP_ORIGIN']
#         elif ws.origin is not None:
#             return ws.origin
#         else:
#             return str(uuid.uuid4())
    
#     @property
#     def _webSockets(self):
#         # deadSockets = [ws for ws in self._webSockets if self.isDeadSocket(ws)]
#         # if deadSockets:
#         #     for dWs in deadSockets:
#         #         self.remove(dWs)
#         if self._webSocketsRawList:
#             liveSockets = [ws for ws in self._webSocketsRawList.values() if self.isLiveSocket(ws)]
#             for k,ws in self._webSocketsRawList.items():
#                 if ws not in liveSockets:
#                     self.removeWS(ws)
#             self._webSocketsRawList = {self._getWsOrigin(ws):ws for ws in liveSockets}
#             return self._webSocketsRawList
#         else:
#             return {}
    
#     def emitQ(self, eventName: WebSocketServerResponseEvent, data: Any):
#         WebSocketsStack.__event_emission_queue.put(WSResponseEvent(eventName=eventName, data=data))
#         # logging.debug(Fore.LIGHTYELLOW_EX + Style.DIM +
#         #       f'Queued [{eventName}] in WebSocketStack' + Style.RESET_ALL)
        
#     def _emit_all_sockets(self, eventName: WebSocketServerResponseEvent, data: Any):
#         if self._webSockets:
#             # logging.debug(Fore.LIGHTYELLOW_EX + Style.DIM +
#             #     f'Emitting [{eventName}] from all sockets' + Style.RESET_ALL)
#             for webSocket in self._webSockets.values():
#                 self._emit(ws=webSocket,eventName=eventName, data=data)
        
                
#     def _emit(self, ws:IWrapWebSocket, eventName: WebSocketServerResponseEvent, data: Any):
#         # def emit_main_thread_lambda(ws:WebSocket, eventName: WebSocketServerResponseEvent, data: Any):
        
#             # logging.debug(Fore.GREEN + Style.DIM + f'Emitting [{eventName}] from a socket' + Style.RESET_ALL)
#             # if not self._lock.locked:
#             # https: // www.geeksforgeeks.org/synchronization-by-using-semaphore-in-python/
#             timeoutAfterSecs = 5.0
#             self._lock.acquire(blocking=True, timeout=timeoutAfterSecs)
#             messageSent = False
#             _N = 50
#             for i in range(_N):
#                 try:
#                     ws.send(message=json.dumps(
#                         {'type': eventName.value, 'data': data}))
#                     messageSent = True
#                 except WebSocketError as wsErr:
#                     'DeadSocket'
#                     # logging.debug(Fore.RED + Style.DIM +
#                     #         f'WebSocketError in web_socket_stack.py ({__name__}): ->\n\t{wsErr}' + Style.RESET_ALL)
#                 except ConcurrentObjectUseError as e:
#                     retrying = 'Retrying...' if i < (_N - 1) else 'Done trying!'
#                     #BUG: https://github.com/Dwonczykj/gember-points/issues/1 -> receiving messages from the client whilst trying sending messages to the client -> Fix using 2 channels?
#                     # Try to implement https://stackoverflow.com/questions/27572336/handle-multiple-requests-with-select
#                     logging.debug(Fore.YELLOW + Style.DIM + f'Failed to send from ws on attempt: {i}, {retrying}' + Style.RESET_ALL)
#                     logging.debug(Fore.CYAN + 'BUG is due to receiving messages from the client whilst trying sending messages to the client .' + Style.RESET_ALL)
#                     logging.debug(Fore.RED + Style.DIM)
#                     # import sys
#                     traceback.print_exc()
#                     logging.debug(Style.RESET_ALL)
                    
#                 except Exception as e:
#                     logging.debug(Fore.RED + Style.NORMAL +
#                             f'{type(e).__name__} (in {__name__}.py): ->\n\t' + Style.BRIGHT + f'{e}' + Style.RESET_ALL)
#                     break
#                         # logging.debug(e)
#                 finally:
#                     self._lock.release()
#                 if messageSent:
#                     break
        
#         # wsock_callback_queue.put(lambda: emit_main_thread_lambda(ws=ws, eventName=eventName, data=data))
                
#     def receive(self):
#         if self._webSockets:
#             for ws in self._webSockets.values():
#                 ws_received = None
#                 timeoutAfterSecs = 5.0
#                 self._lock.acquire(blocking=True, timeout=timeoutAfterSecs)
#                 try:    
#                     ws_received = ws.receive()
#                 except WebSocketError as wsErr:
#                     self._webSocketOpen = False
#                     return
#                 except Exception as e:
#                     logging.debug(e)
#                     return
#                 finally:
#                     self._lock.release()
                
#                 if ws_received is None:
#                     continue
#                 else:
#                     message = WebSocketsStack.WSMessage(parentStack=self, ws=ws, obj={})
#                     if isinstance(ws_received,str):
#                         try:
#                             message = WebSocketsStack.WSMessage(parentStack=self, ws=ws, obj=json.loads(ws_received))
#                         except Exception as e:
#                             message = WebSocketsStack.WSMessage(parentStack=self, ws=ws, obj={'type': 'message', 'data': ws_received})
#                         yield message
#                     else:
#                         def _f(sem:Semaphore):
#                             with sem:
#                                 self._emit(ws, WebSocketServerResponseEvent.unknown_client_event_response,
#                                         'Not sure how to process message to websocket of type: ' + str(type(ws_received)))
#                         logging.debug(
#                             Fore.BLUE + Style.DIM + 'Spawning new Greenlet for request with unknown client event...' + Style.RESET_ALL)
#                         gevent.spawn(_f,self._lock)
                        
#     class WSMessage:
#         def __init__(self, parentStack:WebSocketsStack, ws:IWrapWebSocket, obj: dict | str):
#             self._ws = ws
#             assert parentStack is not None
#             self._parentStack = parentStack
#             if isinstance(obj, str):
#                 obj = json.loads(obj)
#             assert isinstance(obj, dict)
#             if 'type' in obj:
#                 self.type = obj['type']
#             if 'data' in obj:
#                 self.data = obj['data']
        
#         T = TypeVar('T')
#         def useWS(self, cb:Callable[[IWrapWebSocket],T]):
#             result = None
#             if cb is not None:
#                 self._parentStack._lock.acquire(blocking=True,timeout=5.0)
#                 try:
#                     result = cb(self._ws)
#                 except Exception as e:
#                     if self._parentStack.debug:
#                         logging.debug(Fore.RED,e,Style.RESET_ALL)
#                 finally:
#                     self._parentStack._lock.release()
#             return result

#         def __str__(self):
#             return str(self.__dict__)
                

    
