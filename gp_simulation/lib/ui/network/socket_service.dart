import 'dart:async';

import 'package:flutter/material.dart';
import 'package:socket_io_client/socket_io_client.dart' as io;
import 'package:ansicolor/ansicolor.dart';
import 'package:logging/logging.dart';

import 'package:webtemplate/ui/network/web_socket/web_socket_message_type.dart';
import 'package:webtemplate/utils/ansi_print_colors.dart';

class SocketService extends ChangeNotifier {
  final _streamController = StreamController<dynamic>();

  get stream => _streamController.stream;
  get sink => _streamController.sink;
  get isClosed => _streamController.isClosed;
  get isPaused => _streamController.isPaused;
  get hasListener => _streamController.hasListener;
  get done => _streamController.done;
  Logger get log => Logger('SocketService');

  late io.Socket? _socketInst;

  late final String socketUri;

  late DateTime? connectedAt;

  String get protocol => _socketInst?.io.uri ?? 'N/A';

  String get connectionStatusMessage =>
      ((_socketInst?.connected ?? false)
          ? 'WS $connectionStatus to ${_socketInst?.id}'
          : null) ??
      'WS $connectionStatus';

  String connectionStatus = 'disconnected';

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

  createSocketConnection(String socketIoUrl, [void Function()? onReconnect]) {
    socketUri = socketIoUrl;

    var _socket = io.io(socketUri, {
      'transports': ['websocket'],
      'autoConnect': true,
    });

    _socketInst = _socket;
    registerConnectionHandlers(onReconnect);
  }

  void registerConnectionHandlers([void Function()? onReconnect]) {
    if (_socketInst != null) {
      final _socket = _socketInst!;
      _socket.onConnect((_) {
        connectedAt = DateTime.now();
        var connectedAtStr = connectedAt.toString();
        log.info(PrintPens.cyanPen(
            'WS Connected to ${_socket.io.uri} ${_socket.nsp} with timeout: ${_socket.io.timeout} ms at $connectedAtStr'));
        connected = true;
        connectionStatus = 'connected';
        if (onReconnect != null) {
          onReconnect();
        }
        notifyListeners();
      });

      _socket.onReconnect((_) {
        log.info(PrintPens.cyanPen(
            'WS Reconnected to ${_socket.io.uri} ${_socket.nsp} with timeout: ${_socket.io.timeout} ms'));
        connected = true;
        connectedAt = DateTime.now();
        connectionStatus = 'reconnected';
        if (onReconnect != null) {
          onReconnect();
        }
        notifyListeners();
      });

      _socket.onReconnecting((_) {
        log.info(PrintPens.cyanPen(
            'WS reconnecting to ${_socket.io.uri} ${_socket.nsp} with timeout: ${_socket.io.timeout} ms'));
        connected = false;
        connectionStatus = 'reconnecting';
        notifyListeners();
      });

      _socket.onDisconnect((reason) {
        var timeTaken = DateTime.now().difference(connectedAt!).toString();
        log.warning(PrintPens.peachPen(
            'Socketio disconnected from $protocol with reason: $reason after $timeTaken')); //BUG: https://github.com/Dwonczykj/gp_simulation_frontend/issues/1
        connected = false;
        connectionStatus = 'disconnected';
        notifyListeners();
      });

      // _socket.onPing((data) => log.info(PrintPens.greyPen('client was pinged')));
      // _socket.onPong((data) => log.info(PrintPens.brownPen('client was ponged')));
    }
  }

  bool socketOnEvent(
      String eventName, dynamic Function(dynamic event) handler) {
    if (_socketInst == null) {
      return false;
    }
    _socketInst?.on(eventName, handler);
    return true;
  }

  /// emit from socketInstance which has its namespace embedded within the connection
  emit(String eventName, dynamic data) => _socketInst?.emit(eventName, data);
}
