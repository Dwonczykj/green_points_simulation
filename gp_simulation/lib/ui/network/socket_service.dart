import 'dart:async';

import 'package:flutter/material.dart';
import 'package:socket_io_client/socket_io_client.dart' as io;
import 'package:webtemplate/ui/network/web_socket/web_socket_message_type.dart';
import 'package:ansicolor/ansicolor.dart';
import 'package:webtemplate/utils/ansi_print_colors.dart';

class SocketService extends ChangeNotifier {
  final _streamController = StreamController<dynamic>();

  get stream => _streamController.stream;
  get sink => _streamController.sink;
  get isClosed => _streamController.isClosed;
  get isPaused => _streamController.isPaused;
  get hasListener => _streamController.hasListener;
  get done => _streamController.done;

  late io.Socket? _socketInst;

  late final String socketUri;

  String get protocol => _socketInst?.io.uri ?? 'N/A';

  String get connectionStatus =>
      ((_socketInst?.connected ?? false)
          ? 'WS Connected to ${_socketInst?.id}'
          : null) ??
      'WS Disconnected';

  bool connected = false;

  void cancel() {
    _socketInst?.close();
    _socketInst?.dispose();
  }

  /// Reconnect to socket if disconnected. Will also initialise socket if doesn't exist.
  void tryReconnect() {
    _socketInst ??= io.io(socketUri, {
      'transports': ['websocket'],
      'autoConnect': true,
    });
    if (_socketInst!.disconnected) {
      _socketInst!.connect();
    }
  }

  // get closeReason => _streamController.closeReason;

  createSocketConnection(String socketIoUrl) {
    socketUri = socketIoUrl;

    var _socket = io.io(socketUri, {
      'transports': ['websocket'],
      'autoConnect': true,
    });
    // ..on('connect', (_) {
    //   print('connected to socketio from flutter SocketService');
    // })
    // ..on('disconnect', (_) {
    //   print('disconnected from socketio in flutter SocketService');
    // });
    // ..on('json', _jsonEventHandler);

    _socketInst = _socket;

    _socket.onConnect((_) {
      print(PrintPens.cyanPen(
          'WS Connected to ${_socket.io.uri} ${_socket.nsp} with timeout: ${_socket.io.timeout} ms'));
      connected = true;
      notifyListeners();
    });
    _socket.onReconnect((_) {
      print(PrintPens.cyanPen(
          'WS Reconnected to ${_socket.io.uri} ${_socket.nsp} with timeout: ${_socket.io.timeout} ms'));
      connected = true;
      notifyListeners();
    });

    _socket.onReconnecting((_) {
      print(PrintPens.cyanPen(
          'WS reconnecting to ${_socket.io.uri} ${_socket.nsp} with timeout: ${_socket.io.timeout} ms'));
      connected = false;
      notifyListeners();
    });

    _socket.onDisconnect((reason) {
      print(PrintPens.peachPen(
          'Socketio disconnected from $protocol with reason: $reason')); //BUG: https://github.com/Dwonczykj/gp_simulation_frontend/issues/1
      connected = false;
      notifyListeners();
    });

    // _socket.onPing((data) => print(PrintPens.greyPen('client was pinged')));
    // _socket.onPong((data) => print(PrintPens.brownPen('client was ponged')));
  }

  bool socketOnEvent(
      String eventName, dynamic Function(dynamic event) handler) {
    if (_socketInst == null) {
      return false;
    }
    _socketInst?.on(eventName, handler);
    return true;
  }

  // void addHandlers(
  //     [Map<String, dynamic Function(dynamic data)> handlers =
  //         const <String, dynamic Function(dynamic data)>{}]) {
  //   var socket = _socketInst!;

  //   void _registerHandler(String eventName, dynamic Function(dynamic event) handler){
  //     socket.on(eventName,(dynamic object) {
  //       handler(_wrapEvent(eventName, object));
  //     });
  //   }

  //   // socket.on('message', (dynamic object) {
  //   //   _eventHandler(_wrapEvent('message', object));
  //   // });
  //   _registerHandler(WebSocketServerResponseEvent.message, _eventHandler);
  //   socket.on('json', _jsonEventHandler);

  //   // Custom Handlers
  //   _registerHandler('broadcastFromServer', _eventHandler);
  //   socket.on(WebSocketServerResponseEvent.bank_transaction_completed, (dynamic obj) {
  //     if (_transactionEmitterController.hasListener)
  //   });

  //   // overwrite any handlers with these:
  //   for (var entry in handlers.entries) {
  //     socket.on(entry.key, entry.value);
  //   }
  // }

  // Map<String, dynamic> _wrapEvent(String eventName, dynamic object) =>
  //     <String, dynamic>{'type': eventName, 'data': object};

  /// emit from socketInstance which has its namespace embedded within the connection
  emit(String eventName, dynamic data) => _socketInst?.emit(eventName, data);

  // void _eventHandler(dynamic object) {
  //   print(object);
  //   _streamController.add(object);
  // }

  // void _jsonEventHandler(dynamic object) {
  //   print('json event handler: $object');
  //   _streamController.add(object);
  // }
}
