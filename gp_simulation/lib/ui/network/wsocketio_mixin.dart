import 'dart:async';
import 'dart:html';

import 'package:ansicolor/ansicolor.dart';
import 'package:logging/logging.dart';
import 'package:flutter/material.dart';

import '../../utils/ansi_print_colors.dart';
import '../../utils/pipe.dart';
import '../model/all_models.dart';
import 'market_state_viewer.dart';
import 'socket_service.dart';
import 'web_socket/web_socket_message_handler.dart';
import 'web_socket/web_socket_message_type.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

mixin ReloadAppMixin {}

abstract class SocketIoMixin extends WebSocketHandlers with ReloadAppMixin {
  static const socketIoUrl = wsSocketioUrl;
  var connectionStates = <String, bool>{};

  Logger get log => Logger('SocketIoMixin');

  final globalNspChannel = SocketService()
    ..createSocketConnection('$apiWSUrl/');

  final transactionsChannel = SocketService()
    ..createSocketConnection('$apiWSUrl/transactions');

  final simulationChannel = SocketService()
    ..createSocketConnection('$apiWSUrl/simulation');

  // final socketioChannel = SocketService()
  //   ..createSocketConnection('$apiWSUrl/socket.io');

  List<SocketService> get channels => <SocketService>[
        globalNspChannel,
        transactionsChannel,
        simulationChannel,
        // socketioChannel,
      ];

  void onDispose() {
    for (var channel in channels) {
      channel.removeListener(connectionStatusChanged);
      channel.cancel();
    }
  }

  dynamic printPipe<T>(dynamic data, T Function(dynamic data) handler,
      [AnsiPen? pen]) {
    pen ??= PrintPens.bluePen;
    log.finest(pen(data));
    return handler(data);
  }

  void onInit({void Function()? onReconnect}) {
    log.finest('WS: Connected to channel: ${globalNspChannel.protocol}');

    transactionHandlers.entries.forEach((element) {
      transactionsChannel.socketOnEvent(element.key,
          (event) => printPipe(event, element.value, PrintPens.orangePen));
    });

    simulationHandlers.entries.forEach((element) {
      simulationChannel.socketOnEvent(element.key,
          (event) => printPipe(event, element.value, PrintPens.orangePen));
    });

    globalNamespaceHandlers.entries.forEach((element) {
      globalNspChannel.socketOnEvent(element.key,
          (event) => printPipe(event, element.value, PrintPens.orangePen));
    });

    for (var channel in channels) {
      channel.addListener(connectionStatusChanged);
      channel.registerConnectionHandlers(onReconnect);
    }

    eventNamesClientSendsToServerSynced = true;
  }

  void connectionStatusChanged() {
    // connectionStates = Map.fromEntries(channels
    //     .map((channel) => MapEntry(channel.socketUri, channel.connected)));
    
    final disconnectedChannelName = tryCatchWrap(
        () => channels
            .firstWhere((channel) => channel.connected == false)
            .socketUri,
        throwErr: false);
    if (disconnectedChannelName == null) {
      connectionStatus = 'connected';
    } else {
      connectionStatus = '$disconnectedChannelName disconnected';
    }
    notifyListeners();
  }

  String connectionStatus = 'N/A';
  // bool get webSocketConnected => globalNspChannel.isClosed == false;

  void emitToWSServer({required String type, dynamic data}) {
    if (globalNspChannel.isClosed == false) {
      globalNspChannel.emit(type, data);
    }
  }
}

mixin NativeWSMixin
    on ChangeNotifier, WebSocketHandlers, WSBaseMixin, IMarketStateViewer {
  final pollEveryMillis = const Duration(milliseconds: 5000);

  final unhandledWssMessageTypes = <String>[];

  void pollUpdates() async {
    // void tick(Timer timer) {
    //   if (channel.isClosed == false) {
    //     _emitToWSServer(
    //         type: WebSocketClientEvent.message,
    //         data: 'checking for updates...');
    //   }
    // }

    // Timer.periodic(pollEveryMillis, tick);
  }

  void processWssMessage(WebSocketMessageHandler parser) {
    // try {

    // if (_transactionEmitterController.hasListener &&
    //     parser.type ==
    //         WebSocketServerResponseEvent.bank_transaction_completed) {
    //   if (parser.looksLikeTransactionJson()) {
    //     var transaction = parser.getTransactionModelFromJson();
    //     if (transaction != null) {
    //       _transactionEmitterController.add(transaction);
    //     }
    //   }
    // } else {
    // if (parser.type == WebSocketServerResponseEvent.purchase_delay) {
    //   final val = double.tryParse(parser.data.toString());
    //   if (val != null) {
    //     purchaseDelaySeconds = val;
    //     notifyListeners();
    //   }
    // } else if (parser.type == WebSocketServerResponseEvent.entity_updated &&
    //     parser.looksLikeEntityJson()) {
    //   var entity = parser.getEntityModelFromJson();
    //   if (entity != null) {
    //     _updateEntityInCatalog(entity);
    //     notifyListeners();
    //   }
    //   // } else if (parser.type ==
    //   //     WebSocketServerResponseEvent.simulation_iteration_completed) {
    //   //   if (_simulationProgressEmitterController.hasListener) {
    //   //     pipe_if_exists(_parseSimulationProgressData(parser.data),
    //   //         _simulationProgressEmitterController.add);
    //   //   }
    // } else if (parser.type ==
    //     WebSocketServerResponseEvent.retailer_strategy_changed) {
    //   _updateRetailerStrategy(parser.data['name'], parser.data['strategy']);
    // } else if (parser.type ==
    //     WebSocketServerResponseEvent.retailer_sustainbility_changed) {
    //   _updateRetailerSustainabilityRating(
    //       parser.data['name'], parser.data['sustainability']);
    // } else if (unhandledWssMessageTypes.contains(parser.type.toString())) {
    //   // already seen that we dont handle messages with this type
    // } else {
    //   print(PrintPens.magentaPen(
    //       'Not handling websocket messages of type: ${parser.type}'));
    //   unhandledWssMessageTypes.add(parser.type.toString());
    // }
    //   }
    // } catch (e) {
    //   rethrow;
    // }
  }

  // bool get webSocketConnected => channel.isClosed == false;

  // void emitToWSServer({required String type, dynamic data}) {
  //   if (channel.isClosed == false) {
  //     channel.emit(type, data);
  //   }
  // }

  // void onInit() {
  //   if (channel != null) {
  //     print(
  //         'WS: Connected to channel: ${channel} at ${MarketStateViewer.socketIoUrl}');
  //     _websocketChannelSubscription = channel.stream
  //         .listen((dynamic msg) => handleWssMessage(msg, processWssMessage));

  //     _websocketChannelSubscription?.onDone(() {
  //       print(
  //           'WS: Completed on channel: [${channel}] at ${MarketStateViewer.socketIoUrl}');
  //     });

  //     _websocketChannelSubscription?.onError((err) {
  //       print('WebSocket closed: $err');
  //     });

  //     pollUpdates();
  //   }

  //   eventNamesClientSendsToServerSynced = true;
  // }

  // void onDispose() {
  //   _websocketChannelSubscription?.cancel();
  //   channel.sink.close();
  // }
}
