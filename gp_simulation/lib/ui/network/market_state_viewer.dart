import 'dart:async';
import 'dart:collection';
import 'dart:convert';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/services.dart' show rootBundle;
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:ansicolor/ansicolor.dart';
// import 'dart:html' as html;

import '../../utils/ansi_print_colors.dart';
import '../../utils/pipe.dart';
import 'network.dart';
import 'web_socket/web_socket.dart';
import '../model/models.dart';
import 'socket_service.dart';
import 'wsocketio_mixin.dart';

const String apiKey = '<Your Key>';
const String apiId = '<your ID>';
const String appHost = '127.0.0.1';
const String appPort = '8443';
const String apiUrl = 'http://$appHost:$appPort';
// const String wsUrl = 'ws://$appHost:$appPort/websocket';
const String wsSocketioUrl = 'ws://$appHost:$appPort/socket.io';

class HttpClientGember extends http.BaseClient {
  final _httpClient = http.Client();

  HttpClientGember();

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) {
    Map<String, String> defaultHeaders = <String, String>{
      // 'Content-Type': 'application/json; charset=UTF-8',
      'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
      // 'Host': '$appHost:$appPort',
      // 'Connection': 'keep-alive',
      // 'Sec-Ch-Ua':
      //     '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
      // 'Sec-Ch-Ua-Mobile': '?0',
      // 'User-Agent':
      //     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
      // 'Sec-Ch-Ua-Platform': '"macOS"',
      'Accept': '*/*',
      //TODO: remove the reliance on html by removing the origin header
      // 'Origin':
      //     'http://${html.window.location.host}:${html.window.location.port}/',
      // 'Sec-Fetch-Site': 'cross-site',
      // 'Sec-Fetch-Mode': 'cors',
      // 'Sec-Fetch-Dest': 'empty',
      // 'Referer':
      //     'http://${html.window.location.host}:${html.window.location.port}/',
      // 'Accept-Encoding': 'gzip, deflate, br',
      'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
      // 'GEMBER_API_KEY': dotenv.env['APPKEY'] ?? '',
    };
    // var uri = request.url;
    // final queryParameters = {
    //   'GEMBER_API_KEY': dotenv.env['APPKEY'] ?? '',
    // };
    // queryParameters.addAll(uri.queryParameters);
    // request.url = Uri(
    //   scheme: uri.scheme,
    //   fragment: uri.fragment,
    //   path: uri.path,
    //   queryParameters: queryParameters,
    //   userInfo: uri.userInfo,
    // );
    // final uri =
    //     Uri.https('www.myurl.com', '/api/v1/test/${widget.pk}', queryParameters);
    // final response = await http.get(uri, headers: {
    //   HttpHeaders.authorizationHeader: 'Token $token',
    //   HttpHeaders.contentTypeHeader: 'application/json',
    // });
    request.headers.addAll(defaultHeaders);
    return _httpClient.send(request);
  }
}

mixin WSBaseMixin on IMarketStateViewer {
  SimulationProgressData? _parseSimulationProgressData(dynamic event) {
    try {
      return SimulationProgressData(
          data: event, iterationNumber: event["iteration_number"]);
    } on Exception catch (e) {
      print('market_state_viewer._parseSimulationProgressData threw $e');
      return null;
    }
  }
}

abstract class WebSocketHandlers extends IMarketStateViewer with WSBaseMixin {
  late final transactionHandlers = <String, dynamic Function(dynamic data)>{
    WebSocketServerResponseEvent.bank_transaction_completed: (dynamic data) {
      if (_transactionEmitterController.hasListener) {
        WebSocketMessageHandler parser = SocketioMessageHandler(
            type: WebSocketServerResponseEvent.bank_transaction_completed,
            data: data);
        if (parser.looksLikeTransactionJson()) {
          var transaction = parser.getTransactionModelFromJson();
          if (transaction != null) {
            _transactionEmitterController.add(transaction);
          }
        }
      }
    },
  };

  late final simulationHandlers = <String, dynamic Function(dynamic data)>{
    WebSocketServerResponseEvent.simulation_iteration_completed:
        (dynamic data) {
      if (_simulationProgressEmitterController.hasListener) {
        WebSocketMessageHandler parser = SocketioMessageHandler(
            type: WebSocketServerResponseEvent.simulation_iteration_completed,
            data: data);
        pipe_if_exists(_parseSimulationProgressData(parser.data),
            _simulationProgressEmitterController.add);
      }
    },
  };

  late final globalNamespaceHandlers = <String, dynamic Function(dynamic data)>{
    WebSocketServerResponseEvent.purchase_delay: (dynamic data) {
      if (_simulationProgressEmitterController.hasListener) {
        purchaseDelaySeconds =
            double.tryParse(data.toString()) ?? purchaseDelaySeconds;
        notifyListeners();
      }
    },
    WebSocketServerResponseEvent.entity_updated: (dynamic data) {
      WebSocketMessageHandler parser = SocketioMessageHandler(
          type: WebSocketServerResponseEvent.entity_updated, data: data);
      if (parser.looksLikeEntityJson()) {
        var entity = parser.getEntityModelFromJson();
        if (entity != null) {
          _updateEntityInCatalog(entity);
          notifyListeners();
        }
      }
    },
    WebSocketServerResponseEvent.retailer_strategy_changed: (dynamic data) {
      _updateRetailerStrategy(data['name'], data['strategy']);
    },
    WebSocketServerResponseEvent.retailer_sustainbility_changed:
        (dynamic data) {
      _updateRetailerSustainabilityRating(data['name'], data['sustainability']);
    },
    WebSocketServerResponseEvent.pong: (dynamic data) {
      print(PrintPens.orangePen('pong received'));
    },
  };
}

/// [IMarketStateViewer] is a singleton that implements [ChangeNotifier]
abstract class IMarketStateViewer extends ChangeNotifier {
  // factory IMarketStateViewer.create() {
  //   _instance ??= IMarketStateViewer._privateConstruct();
  //   return _instance!;
  // }

  // IMarketStateViewer._privateConstruct();

  // static IMarketStateViewer? _instance;

  final List<TransactionModel> transactions = <TransactionModel>[];
  int get counter => transactions.length;

  late bool eventNamesClientSendsToServerSynced;
  late bool eventNamesServerSendsToClientSynced;

  abstract String wsConnectionStatus;
  bool get webSocketConnected => false;

  /// the subscription that we use to subscribe to the websockets entire channel
  late StreamSubscription<dynamic>? _websocketChannelSubscription;

  /// A stream created by the [MarketStateViewer] to push updates to consumers... -> should be using notifyListeners...
  final _transactionEmitterController = StreamController<TransactionModel>();

  // late StreamSubscription<dynamic>? _simulationProgressSubscription;

  final _simulationProgressEmitterController =
      StreamController<SimulationProgressData>();

  bool backendServerDead = false;

  LoadEntitiesResult _EntityCatalog = LoadEntitiesResult(
    retailers: <RetailerModel>[],
    retailersCluster: AggregatedRetailers.zero(),
    customers: <CustomerModel>[],
  );

  AppTransactionsStateModel _allTransactions = AppTransactionsStateModel(
    transactionsByEntityId: <String, List<TransactionModel>>{},
  );

  final Map<String, LoadTransactionsForEntityResult> _transactions =
      Map<String, LoadTransactionsForEntityResult>();

  int get transactionsCounter => _transactions.length;

  void testWsConnMemory();

  //TODO: Create an AppStateManager that has the transactionCounter, transactionsToProcess:
  //  Use a counter to confirm if I've already processed a transaction from the web socket
  //  stream or add new message to appstatemanager.transtoprocess and then process in UI,
  //  immediately set the transaction to "being processed" In the appstatemanager
  //  and then once widget finishes visuals, remove from transtoprocess

  final Map<String, LoadSalesForItem> _salesByitem =
      Map<String, LoadSalesForItem>();

  final httpClient = HttpClientGember();

  void transactionOccured(TransactionModel t) {
    //TODO: Add the Transaction object to state on this MarketStateViewer and then notifyListeners so that anyone
    //looking at the state of MarketStateViewer can see teh new transaction. Perhaps store a transaction count,
    //increment the counter and then get the latest transaction from the list
    transactions.add(t);
    notifyListeners();
  }

  void updateRetailerParamsHTTP(String simulationId, String retailerName,
      {double? strategy, double? sustainabilityRating});

  void updateRetailerParamsWS(String simulationId, String retailerName,
      {double? strategy, double? sustainabilityRating});

  void _updateRetailerStrategy(String retailerName, double strategy) {
    var matches = _EntityCatalog.retailers
        .where((retailer) => retailer.name == retailerName);
    if (matches.isNotEmpty) {
      matches.first.strategy = strategy;
      notifyListeners();
    }
  }

  void _updateRetailerSustainabilityRating(
      String retailerName, double sustainabilityRating) {
    var matches = _EntityCatalog.retailers
        .where((retailer) => retailer.name == retailerName);
    if (matches.isNotEmpty) {
      matches.first.sustainability = sustainabilityRating;
      notifyListeners();
    }
  }

  Future<LoadEntitiesResult> loadEntities();

  void _loadEntities(String? data) {
    try {
      if (data != null) {
        final dataMap = jsonDecode(data);
        var customers = TSerializable.getJsonMapValue(
            dataMap, 'customers', CustomerModel.fromJson,
            defaultVal: <String, CustomerModel>{}).values.toList();

        var retailerCluster = AggregatedRetailers(
          balance: TSerializable.getJsonValueFromChain(dataMap,
              ['retailersCluster', 'balance'], BankAccountViewModel.fromJson),
          balanceMoney: TSerializable.getJsonValueFromChain(dataMap,
              ['retailersCluster', 'balanceMoney'], CostModel.fromJson),
          salesHistory: TSerializable.getJsonListValueFromChain(dataMap,
              ['retailersCluster', 'salesHistory'], SaleModel.fromJson),
          totalSales: TSerializable.getJsonValueFromChain(
              dataMap,
              ['retailersCluster', 'totalSales'],
              SalesAggregationModel.fromJson),
          retailerNames: ((dataMap['retailers'] ?? <String, dynamic>{})
                  as Map<String, dynamic>)
              .keys
              .toList(),
        );

        var retailers = TSerializable.getJsonMapValue(
            dataMap, 'retailers', RetailerModel.fromJson,
            defaultVal: <String, RetailerModel>{}).values.toList();

        _EntityCatalog = LoadEntitiesResult(
          retailers: retailers,
          retailersCluster: retailerCluster,
          customers: customers,
        );
      }
    } catch (err) {
      print(err);
    }
  }

  Future<EntityModel?> loadEntity(InstitutionModel owner);

  EntityModel? _loadEntity(String? data) {
    if (data != null) {
      var dataMap = jsonDecode(data) as Map<String, dynamic>;

      if (dataMap.containsKey('salesHistory')) {
        return RetailerModel.fromJson(dataMap);
      } else if (dataMap.containsKey('purchaseHistory')) {
        return CustomerModel.fromJson(dataMap);
      }
      return null;
    }
  }

  Future<void> _updateEntityBalances(TransactionModel transaction) async {
    if (_EntityCatalog.isNotEmpty) {
      final fromEntity = await loadEntity(transaction.accountFrom.owner);
      final toEntity = await loadEntity(transaction.accountTo.owner);
      if (fromEntity != null) {
        _updateEntityInCatalog(fromEntity);
      }
      if (toEntity != null) {
        _updateEntityInCatalog(toEntity);
      }
      notifyListeners();
    }
  }

  void _updateEntityInCatalog(EntityModel entity) {
    if (_EntityCatalog.isNotEmpty) {
      if (entity is RetailerModel) {
        _EntityCatalog.retailers
            .removeWhere((element) => element.id == entity.id);
        _EntityCatalog.retailers.add(entity);
      } else if (entity is CustomerModel) {
        _EntityCatalog.customers
            .removeWhere((element) => element.id == entity.id);
        _EntityCatalog.customers.add(entity);
      } else {
        var name = entity.runtimeType.toString();
        throw Exception('Unhandled Entity type: $name seen to update catalog.');
      }
    }
  }

  Future<LoadTransactionsForEntityResult> loadTransactions(String entityId);

  LoadTransactionsForEntityResult _loadTransactions(
      String entityId, String? data) {
    if (data != null) {
      final dataMap = jsonDecode(data);
      _transactions[entityId] = LoadTransactionsForEntityResult(
          transactionsFromEntity: (dataMap['transactionsFromEntity'] as List)
              .map((element) =>
                  TransactionModel.fromJson(element as Map<String, dynamic>))
              .toList(),
          transactionsToEntity: (dataMap['transactionsToEntity'] as List)
              .map((element) =>
                  TransactionModel.fromJson(element as Map<String, dynamic>))
              .toList());
      return _transactions[entityId]!;
    }
    return LoadTransactionsForEntityResult(
        transactionsFromEntity: <TransactionModel>[],
        transactionsToEntity: <TransactionModel>[]);
  }

  Future<void> startIsolatedSimIteration();

  Future<LoadSalesForItem> loadSalesForItem(String itemName);

  LoadSalesForItem _loadSalesForItem(String itemName, String? data) {
    if (data != null) {
      final dataMap = jsonDecode(data);
      _salesByitem[itemName] = LoadSalesForItem(
          salesForItem: (dataMap['transactionsFromEntity'] as List)
              .map((element) =>
                  SaleModel.fromJson(element as Map<String, dynamic>))
              .toList());
      return _salesByitem[itemName]!;
    }
    return LoadSalesForItem(salesForItem: <SaleModel>[]);
  }

  Future<AppTransactionsStateModel> loadAppTransactionsState();

  AppTransactionsStateModel _loadAppTransactionsState(String? data) {
    if (data != null) {
      final dataMap = jsonDecode(data);
      _allTransactions = AppTransactionsStateModel.fromJson(
          Map<String, dynamic>.from(dataMap));
    }
    return _allTransactions;
  }

  RunSimulationResponseModel? _loadSimulationEnvironment(String? data) {
    if (data != null) {
      final dataMap = jsonDecode(data);
      return RunSimulationResponseModel.fromJson(
          Map<String, dynamic>.from(dataMap));
    }
    return null;
  }

  Future<RunSimulationResponseModel?> startFullSimulation(
      double convergenceThreshold, int maxN);

  /// A stream manufactured on the [MarketStateViewer] solely responsible for streaming Transactions that
  /// the [MarketStateViewer] has processed to consuming widgets.
  /// We use a stream instead of listening for updates from notifyListeners as it is more direct.
  late Stream<TransactionModel> onTransaction;

  late Stream<SimulationProgressData>
      onSimulationProgress; //FIXED BUG: Error: Bad State: Stream has already been listened to. Issue:->https://stackoverflow.com/a/51396947 -> (Standard Streams can only be listened to by one Listener at one time, use Broadcast to have multiple) & Solution:->https://stackoverflow.com/a/58245557

  double purchaseDelaySeconds = 2.0;

  double customerStickyness = 1.0;

  void updatePurchaseDelaySpeed(double newSpeed);
}

mixin HttpRequestMixin on SocketIoMixin, IMarketStateViewer {
  Uri _addKeyToUri(String url) {
    final uri = Uri.parse(url);
    final queryParameters = {
      'GEMBER_API_KEY': dotenv.env['APPKEY'] ?? '',
    };
    queryParameters.addAll(uri.queryParameters);
    return Uri(
      scheme: uri.scheme,
      fragment: uri.fragment,
      path: uri.path,
      host: uri.host,
      port: uri.port,
      queryParameters: queryParameters,
      userInfo: uri.userInfo,
    );
  }

  String wsConnectionStatus = 'No Websocket Connection';

  Future<String?> getData(String url, {Map<String, String>? headers}) async {
    final uri = _addKeyToUri(url);
    print(PrintPens.orangePen('[GET]: Calling uri: $uri'));
    http.Response response;

    try {
      response = await httpClient.get(uri, headers: headers);
      if (backendServerDead) {
        backendServerDead = false;
        notifyListeners();
      }
      if (response.statusCode >= 200 && response.statusCode < 300) {
        print(PrintPens.orangePen('[GET]: Received response for: $uri'));
        return response.body;
      } else {
        print(response.statusCode);
        return null;
      }
    } catch (e) {
      print("[GET ERROR]: Calling uri: $uri: ${e}");
      print(e);
    }
  }

  Future<String?> postData(String url, Map<String, String> postData) async {
    final uri = _addKeyToUri(url);
    Map<String, String> headers = HashMap();
    headers['Accept'] = 'application/json';

    print(PrintPens.orangePen('[POST]: Calling uri: $uri'));
    try {
      /* [body] sets the body of the request. It can be a [String], a [List] or a [Map<String, String>]. If it's a String, it's encoded using [encoding] and used as the body of the request. The content-type of the request will default to "text/plain".

        If [body] is a List, it's used as a list of bytes for the body of the request.

        If [body] is a Map, it's encoded as form fields using [encoding]. The content-type of the request will be set to "application/x-www-form-urlencoded"; this cannot be overridden.

        [encoding] defaults to [utf8].*/
      final response = await httpClient.post(
        uri,
        body: postData,
      );
      if (backendServerDead) {
        backendServerDead = false;
        notifyListeners();
      }

      if (response.statusCode >= 200 && response.statusCode < 300) {
        print(PrintPens.orangePen('[POST]: Received response for: $uri'));
        return response.body;
      } else {
        print(PrintPens.peachPen(
            'App need to handle HTTP Response Status Code: ${response.statusCode}'));
        return null;
      }

      // } on XMLHttpRequestError catch (e) {
      //   print(e.message);
    } catch (e) {
      backendServerDead = true;
      notifyListeners();
      print("[POST ERROR]: Calling uri: $uri: ${e}");
      print(
          'May need to restart python server as issue when closing this app that kills the socket and errors in flask app');
      channels.forEach((element) => element.tryReconnect());
    }
  }
}

class MarketStateViewer extends SocketIoMixin with HttpRequestMixin {
  factory MarketStateViewer.create() {
    _instance ??= MarketStateViewer._privateConstruct();
    return _instance!;
  }

  static const socketIoUrl = SocketIoMixin.socketIoUrl;

  bool loadingEntities = false;

  MarketStateViewer._privateConstruct() {
    onTransaction = _transactionEmitterController.stream.asBroadcastStream();
    onSimulationProgress =
        _simulationProgressEmitterController.stream.asBroadcastStream();

    onInit();
    if (webSocketConnected) {
      wsConnectionStatus = globalNspChannel.connectionStatus;
    }

    // checkClientAcceptsWSEventNames().then((inSync) {
    //   eventNamesClientSendsToServerSynced = inSync;
    //   notifyListeners();
    // });

    // eventNamesServerSendsToClientSynced = true;
    // checkServerResponseWSEventNames().then((inSync) {
    //   eventNamesServerSendsToClientSynced = inSync;
    //   notifyListeners();
    // });
  }

  @override
  void dispose() {
    onDispose();
    super.dispose();
  }

  // Stream<TransactionModel> registerWSSTransactionConn() {
  //   _transactionEmitterController.onListen = () {
  //     onTransactionsListenerAdded();
  //   };

  //   _transactionEmitterController.onCancel = () {
  //     if (!_transactionEmitterController.hasListener) {
  //       channel.sink.close();
  //       onAllTransactionsListenersCancelled();
  //     }
  //   };

  //   return _transactionEmitterController.stream.asBroadcastStream();
  // }

  // Stream<SimulationProgressData> registerWSSSimulationProgressStream() {
  //   _simulationProgressEmitterController.onCancel = () {};
  //   _simulationProgressEmitterController.onCancel = () {};

  //   return _simulationProgressEmitterController.stream.asBroadcastStream();
  // }

  Future<bool> checkServerResponseWSEventNames() async {
    final eventNamesResponse =
        await getData('$apiUrl/ws/event-response-names-cat');
    if (eventNamesResponse != null) {
      final data = Map<String, dynamic>.from(jsonDecode(eventNamesResponse));
      final eventNamesList = data['data'] as List<String>;

      bool allMatchServerInFlutter = true;
      // Check all event names according to server are accounted for in flutter front end
      for (final event in eventNamesList) {
        allMatchServerInFlutter =
            !WebSocketServerResponseEvent.all_members.contains(event);
      }

      bool allMatchFlutterOnServer = true;
      // Check all event names according to flutter front end are accounted for on server
      for (final event in WebSocketServerResponseEvent.all_members) {
        allMatchFlutterOnServer = !eventNamesList.contains(event);
      }
      return (allMatchFlutterOnServer && allMatchServerInFlutter);
    } else {
      return false;
    }
  }

  Future<bool> checkClientAcceptsWSEventNames() async {
    final eventNamesResponse = await getData('$apiUrl/ws/event-names-cat');
    if (eventNamesResponse != null) {
      final data = Map<String, dynamic>.from(jsonDecode(eventNamesResponse));
      final eventNamesList = data['data'] as List<String>;

      bool allMatchServerInFlutter = true;
      // Check all event names according to server are accounted for in flutter front end
      for (final event in eventNamesList) {
        allMatchServerInFlutter =
            !WebSocketClientEvent.all_members.contains(event);
      }

      bool allMatchFlutterOnServer = true;
      // Check all event names according to flutter front end are accounted for on server
      for (final event in WebSocketClientEvent.all_members) {
        allMatchFlutterOnServer = !eventNamesList.contains(event);
      }
      return (allMatchFlutterOnServer && allMatchServerInFlutter);
    } else {
      return false;
    }
  }

  void onTransactionsListenerAdded() {
    // add handlers
  }

  void onAllTransactionsListenersCancelled() {}

  static MarketStateViewer? _instance;

  @override
  Future<LoadSalesForItem> loadSalesForItem(String itemName) async {
    final data = await getData('$apiUrl/item-sales?item-name=$itemName');
    return _loadSalesForItem(itemName, data);
  }

  @override
  Future<LoadTransactionsForEntityResult> loadTransactions(
      String entityId) async {
    final data = await getData('$apiUrl/transactions?entityid=$entityId');
    return _loadTransactions(entityId, data);
  }

  @override
  void testWsConnMemory() async {
    final data = await getData('$apiUrl/test-ws-event-memory');
    return;
  }

  @override
  Future<LoadEntitiesResult> loadEntities() async {
    if (_EntityCatalog.isEmpty && !loadingEntities) {
      loadingEntities = true;
      try {
        final data = await postData('$apiUrl/init', {
          'retailer_name': 'Tescos',
          'retailer_strategy': 'COMPETITIVE',
          'retailer_sustainability': 'AVERAGE',
        });
        _loadEntities(data);
      } finally {
        loadingEntities = false;
      }
      _requestPurchaseSpeed();
    }
    return _EntityCatalog;
  }

  @override
  Future<EntityModel?> loadEntity(InstitutionModel owner) async {
    final data =
        await postData('$apiUrl/entity', {'name': owner.name, 'id': owner.id});
    return _loadEntity(data);
  }

  _requestPurchaseSpeed() async {
    // _emitToWSServer(jsonEncode(
    //     <String, dynamic>{'type': 'get purchase delay', 'data': 'null'}));
    emitToWSServer(type: 'get purchase delay', data: 'null');
  }

  @override
  void updatePurchaseDelaySpeed(double newSpeed) async {
    if (globalNspChannel.isClosed == false) {
      emitToWSServer(
          type: WebSocketClientEvent.change_purchase_delay, data: newSpeed);
      _requestPurchaseSpeed();
    }
  }

  @override
  void updateRetailerParamsHTTP(String simulationId, String retailerName,
      {double? strategy, double? sustainabilityRating}) async {
    var options = {
      'simulation_id': simulationId,
      'retailer_name': retailerName,
    };
    if (strategy != null) {
      options['retailer_strategy'] = '$strategy';
    }
    if (sustainabilityRating != null) {
      options['retailer_sustainability'] = '$sustainabilityRating';
    }
    var response = await postData('$apiUrl/adjust-retailer', options);
  }

  @override
  void updateRetailerParamsWS(String simulationId, String retailerName,
      {double? strategy, double? sustainabilityRating}) {
    var options = {
      'simulation_id': simulationId,
      'retailer_name': retailerName,
    };
    if (strategy != null) {
      options['retailer_strategy'] = '$strategy';
    }
    if (sustainabilityRating != null) {
      options['retailer_sustainability'] = '$sustainabilityRating';
    }
    if (globalNspChannel.isClosed == false) {
      emitToWSServer(
          type: WebSocketClientEvent.change_retailer_strategy, data: options);
    }
  }

  @override
  Future<void> startIsolatedSimIteration() async {
    final response = await postData('$apiUrl/run', {});
    // print(response);
    //TODO P2: Load the results into all entity detail cards.
  }

  @override
  Future<RunSimulationResponseModel?> startFullSimulation(
      double convergenceThreshold, int maxN) async {
    final response = await postData('$apiUrl/run-full-sim', {
      'convergence_threshold': "$convergenceThreshold",
      'maxN': "$maxN",
    });
    await Future.delayed(Duration(seconds: 3));

    print(PrintPens.orangePen('pinging the client'));
    globalNspChannel.emit('ping', 'PINGING');
    return _loadSimulationEnvironment(response);
    // print(response);
    //TODO P2: Load the results into all entity detail cards.
  }

  @override
  Future<AppTransactionsStateModel> loadAppTransactionsState() async {
    final response = await getData('$apiUrl/transactionsState');
    return _loadAppTransactionsState(response);
  }
}

class MarketStateViewerMock extends IMarketStateViewer {
  factory MarketStateViewerMock.create() {
    _instance ??= MarketStateViewerMock._privateConstruct();
    return _instance!;
  }

  final randomGenerator = math.Random();

  bool _keepStreamingTransactons = true;

  MarketStateViewerMock._privateConstruct() {
    purchaseDelaySeconds = 2.0;
    _keepStreamingTransactons = true;
    onTransaction = regularTransactionMockCreatorSync(
            Duration(milliseconds: (purchaseDelaySeconds * 1000.0).round()))
        .stream
        .asBroadcastStream();
    // onSimulationProgress =

    eventNamesClientSendsToServerSynced = true;
    eventNamesServerSendsToClientSynced = true;
  }

  @override
  void updatePurchaseDelaySpeed(double newSpeed) async {
    purchaseDelaySeconds = newSpeed;
    _keepStreamingTransactons = false;
    await Future.delayed(Duration(seconds: 1));
    _keepStreamingTransactons = true;
    onTransaction = regularTransactionMockCreatorSync(
            Duration(milliseconds: (purchaseDelaySeconds * 1000.0).round()))
        .stream
        .asBroadcastStream();
  }

  @override
  void testWsConnMemory() {
    return;
  }

  Stream<TransactionModel> regularTransactionMockCreator(Duration interval,
      [int? maxCount]) async* {
    int i = 0;
    while (true) {
      await Future.delayed(interval);
      if (_EntityCatalog.isNotEmpty) {
        var t = TransactionModel(
          accountFrom: BankAccountModelLight(
            "account_from_id_please_set",
            owner: InstitutionModel(
                name: _EntityCatalog.customers[0].name,
                id: _EntityCatalog.customers[0].id),
            bank: InstitutionModel(name: "AMEX_BANK", id: 'AMEX_BANK_ID'),
            fiatCurrency: 'GBP',
            balance: BankAccountViewModel.dummy(),
          ),
          accountTo: BankAccountModelLight(
            "account_to_id_please_set",
            owner: InstitutionModel(
                name: _EntityCatalog.retailers[0].name,
                id: _EntityCatalog.retailers[0].id),
            bank: InstitutionModel(name: "AMEX_BANK", id: 'AMEX_BANK_ID'),
            fiatCurrency: 'GBP',
            balance: BankAccountViewModel.dummy(),
          ),
          money: CostModel(1.0, 'GBP'),
          ether: EtherPaymentModel(
              ether: CoinModel(0.0001),
              gas: CoinModel(0.000001),
              money: CostModel(0.0, 'GBP')),
          greenPoints: GreenPointsPaymentModel(
            greenPoints: CoinDetailModel(
                amount: 5.0,
                tokenValueInPeggedCurrency: 0.01,
                valueInPeggedCurrency: CostModel(0.05, 'GBP'),
                peggedCurrency: 'GBP'),
            gas: CoinModel(0.00000025),
            money: CostModel(0.0, 'GBP'),
          ),
        );
        yield t;
        _updateEntityBalancesMock(t);
        if (i == maxCount) break;
      }
    }
  }

  StreamController<TransactionModel> regularTransactionMockCreatorSync(
      Duration interval,
      [int? maxCount]) {
    bool ticking = false;
    Timer? controllerLoop;
    StreamController<TransactionModel>? controller;
    int counter = 0;
    void tick(Timer timer) {
      ticking = true;
      if (controller == null) {
        timer.cancel();
        ticking = false;
        return;
      }
      if (_EntityCatalog.isNotEmpty) {
        var iCust = randomGenerator.nextInt(_EntityCatalog.customers.length);
        var iRetlr = randomGenerator.nextInt(_EntityCatalog.retailers.length);
        var t = TransactionModel(
          accountFrom: BankAccountModelLight(
            "account_from_id_please_set",
            owner: InstitutionModel(
                name: _EntityCatalog.customers[iCust].name,
                id: _EntityCatalog.customers[iCust].id),
            bank: InstitutionModel(name: "AMEX_BANK", id: 'AMEX_BANK_ID'),
            fiatCurrency: 'GBP',
            balance: BankAccountViewModel.dummy(),
          ),
          accountTo: BankAccountModelLight(
            "account_to_id_please_set",
            owner: InstitutionModel(
                name: _EntityCatalog.retailers[iRetlr].name,
                id: _EntityCatalog.retailers[iRetlr].id),
            bank: InstitutionModel(name: "AMEX_BANK", id: 'AMEX_BANK_ID'),
            fiatCurrency: 'GBP',
            balance: BankAccountViewModel.dummy(),
          ),
          money: CostModel(1.0, 'GBP'),
          ether: EtherPaymentModel(
              ether: CoinModel(0.0001),
              gas: CoinModel(0.000001),
              money: CostModel(0.0, 'GBP')),
          greenPoints: GreenPointsPaymentModel(
            greenPoints: CoinDetailModel(
                amount: 5.0,
                tokenValueInPeggedCurrency: 0.01,
                valueInPeggedCurrency: CostModel(0.05, 'GBP'),
                peggedCurrency: 'GBP'),
            gas: CoinModel(0.00000025),
            money: CostModel(0.0, 'GBP'),
          ),
        );
        controller.add(t); // Ask stream to send transaction values as event.;
        _updateEntityBalancesMock(t);
        if (maxCount != null && counter >= maxCount) {
          timer.cancel();
          ticking = false;
          controller.close(); // Ask stream to shut down and tell listeners.
        }
      }
    }

    controller = StreamController<TransactionModel>(onCancel: () {
      if (ticking) {
        controllerLoop?.cancel();
        ticking = false;
      }
    }, onListen: () {
      if (!ticking) {
        controllerLoop = Timer.periodic(interval, tick);
      }
    });

    return controller;
  }

  Future<void> _updateEntityBalancesMock(TransactionModel transaction) async {
    if (_EntityCatalog.isNotEmpty) {
      final fromEntity = await loadEntity(transaction.accountFrom.owner);
      final toEntity = await loadEntity(transaction.accountTo.owner);
      CostModel? addMoney;
      if (transaction.money.amount != 0) {
        addMoney = transaction.money;
      }
      double? addGP;
      if (transaction.greenPoints.greenPoints.amount != 0) {
        addGP = transaction.greenPoints.greenPoints.amount;
      }
      if (fromEntity != null) {
        _updateEntity(fromEntity, addMoney: addMoney, addGP: addGP);
        _updateEntityInCatalog(fromEntity);
      }

      if (transaction.money.amount != 0) {
        addMoney = CostModel(
            transaction.money.amount * -1, transaction.money.currency);
      }
      if (addGP != null) {
        addGP *= -1;
      }
      if (toEntity != null) {
        _updateEntity(toEntity, addMoney: addMoney, addGP: addGP);
        _updateEntityInCatalog(toEntity);
      }

      notifyListeners();
    }
  }

  String wsConnectionStatus = 'Mock ws -> N/A';

  static MarketStateViewerMock? _instance;

  @override
  Future<LoadSalesForItem> loadSalesForItem(String itemName) async {
    var data = await rootBundle.loadString('mock_data/sales_for_item.json');
    return _loadSalesForItem(itemName, data);
  }

  @override
  Future<LoadTransactionsForEntityResult> loadTransactions(
      String entityId) async {
    var data =
        await rootBundle.loadString('mock_data/transactions_for_entity.json');
    return _loadTransactions(entityId, data);
  }

  @override
  Future<void> startIsolatedSimIteration() async {
    throw Exception('Not implemented for Mock Service yet.');
  }

  @override
  Future<void> pollUpdates() async {
    throw Exception('Not implemented for Mock Service yet.');
  }

  @override
  Future<LoadEntitiesResult> loadEntities() async {
    if (_EntityCatalog.isEmpty) {
      var data = await rootBundle.loadString('mock_data/entities.json');
      _loadEntities(data);
      // _EntityCatalog = LoadEntitiesResult(
      //     retailers: (dataMap['retailers'] as Map<String, dynamic>)
      //         .values
      //         .map((element) =>
      //             RetailerModel.fromJson(element as Map<String, dynamic>))
      //         .toList(),
      //     customers: (dataMap['customers'] as Map<String, dynamic>)
      //         .values
      //         .map((element) =>
      //             CustomerModel.fromJson(element as Map<String, dynamic>))
      //         .toList());
    }
    return _EntityCatalog;
  }

  @override
  Future<RunSimulationResponseModel?> startFullSimulation(
      double convergenceThreshold, int maxN) async {
    throw Exception('Not implemented for Mock Service yet.');
    // final response = await postData('$apiUrl/run-full-sim', {
    //   'convergence_threshold': "0.1",
    //   'maxN': "20",
    // });
    // print(response);
    //TODO P2: Load the results into all entity detail cards.
  }

  void _updateEntity(EntityModel entity, {CostModel? addMoney, double? addGP}) {
    if (_EntityCatalog.customers
        .where((element) => element.id == entity.id)
        .toList()
        .isNotEmpty) {
      var customer = _EntityCatalog.customers
          .firstWhere((element) => element.id == entity.id);
      _EntityCatalog.customers.remove(customer);
      var greenPointsFactor =
          customer.balance.greenPointsMonetaryValue.amount > 0
              ? customer.balance.greenPoints /
                  customer.balance.greenPointsMonetaryValue.amount
              : 0.0;
      if (addMoney != null) {
        customer = CustomerModel(
          balance: BankAccountViewModel(
            viewCurrency: customer.balance.viewCurrency,
            underlyingCurrency: customer.balance.underlyingCurrency,
            combinedBalance: CostModel(
                customer.balance.combinedBalance.amount + addMoney.amount,
                customer.balance.combinedBalance.currency),
            greenPoints: customer.balance.greenPoints,
            greenPointsMonetaryValue: customer.balance.greenPointsMonetaryValue,
            moneyBalance: CostModel(
                customer.balance.moneyBalance.amount + addMoney.amount,
                customer.balance.moneyBalance.currency),
          ),
          balanceMoney: CostModel(
              customer.balanceMoney.amount + addMoney.amount,
              customer.balanceMoney.currency),
          bank: customer.bank,
          name: customer.name,
          basket: customer.basket,
          id: customer.id,
          purchaseHistory: customer.purchaseHistory,
        );
      }
      if (addGP != null) {
        customer = CustomerModel(
          balance: BankAccountViewModel(
            viewCurrency: customer.balance.viewCurrency,
            underlyingCurrency: customer.balance.underlyingCurrency,
            combinedBalance: CostModel(
                customer.balance.combinedBalance.amount +
                    (addGP * greenPointsFactor),
                customer.balance.combinedBalance.currency),
            greenPoints: customer.balance.greenPoints + addGP,
            greenPointsMonetaryValue: CostModel(
                customer.balance.greenPointsMonetaryValue.amount +
                    (addGP * greenPointsFactor),
                customer.balance.greenPointsMonetaryValue.currency),
            moneyBalance: CostModel(customer.balance.moneyBalance.amount,
                customer.balance.moneyBalance.currency),
          ),
          balanceMoney: CostModel(
              customer.balanceMoney.amount, customer.balanceMoney.currency),
          bank: customer.bank,
          name: customer.name,
          basket: customer.basket,
          id: customer.id,
          purchaseHistory: customer.purchaseHistory,
        );
      }
      _EntityCatalog.customers.add(customer);
    } else if (_EntityCatalog.retailers
        .where((element) => element.id == entity.id)
        .toList()
        .isNotEmpty) {
      var retailer = _EntityCatalog.retailers
          .firstWhere((element) => element.id == entity.id);
      _EntityCatalog.retailers.remove(retailer);
      var greenPointsFactor =
          retailer.balance.greenPointsMonetaryValue.amount > 0
              ? retailer.balance.greenPoints /
                  retailer.balance.greenPointsMonetaryValue.amount
              : 0.0;
      if (addMoney != null) {
        retailer = RetailerModel(
          balance: BankAccountViewModel(
            viewCurrency: retailer.balance.viewCurrency,
            underlyingCurrency: retailer.balance.underlyingCurrency,
            combinedBalance: CostModel(
                retailer.balance.combinedBalance.amount + addMoney.amount,
                retailer.balance.combinedBalance.currency),
            greenPoints: retailer.balance.greenPoints,
            greenPointsMonetaryValue: retailer.balance.greenPointsMonetaryValue,
            moneyBalance: CostModel(
                retailer.balance.moneyBalance.amount + addMoney.amount,
                retailer.balance.moneyBalance.currency),
          ),
          balanceMoney: CostModel(
              retailer.balanceMoney.amount + addMoney.amount,
              retailer.balanceMoney.currency),
          strategy: RetailerStrategy.COMPETITIVE,
          sustainability: RetailerSustainability.AVERAGE,
          bank: retailer.bank,
          name: retailer.name,
          id: retailer.id,
          salesHistory: retailer.salesHistory,
          totalSales: retailer.totalSales,
        );
      }
      if (addGP != null) {
        retailer = RetailerModel(
          balance: BankAccountViewModel(
            viewCurrency: retailer.balance.viewCurrency,
            underlyingCurrency: retailer.balance.underlyingCurrency,
            combinedBalance: CostModel(
                retailer.balance.combinedBalance.amount +
                    (addGP * greenPointsFactor),
                retailer.balance.combinedBalance.currency),
            greenPoints: retailer.balance.greenPoints + addGP,
            greenPointsMonetaryValue: CostModel(
                retailer.balance.greenPointsMonetaryValue.amount +
                    (addGP * greenPointsFactor),
                retailer.balance.greenPointsMonetaryValue.currency),
            moneyBalance: CostModel(retailer.balance.moneyBalance.amount,
                retailer.balance.moneyBalance.currency),
          ),
          balanceMoney: CostModel(
              retailer.balanceMoney.amount, retailer.balanceMoney.currency),
          strategy: RetailerStrategy.COMPETITIVE,
          sustainability: RetailerSustainability.AVERAGE,
          bank: retailer.bank,
          name: retailer.name,
          id: retailer.id,
          salesHistory: retailer.salesHistory,
          totalSales: retailer.totalSales,
        );
      }
      _EntityCatalog.retailers.add(retailer);
    }
  }

  @override
  Future<EntityModel?> loadEntity(InstitutionModel owner) async {
    if (_EntityCatalog.customers
        .where((element) => element.id == owner.id)
        .toList()
        .isNotEmpty) {
      var customer = _EntityCatalog.customers
          .firstWhere((element) => element.id == owner.id);
      return customer;
    } else if (_EntityCatalog.retailers
        .where((element) => element.id == owner.id)
        .toList()
        .isNotEmpty) {
      var retailer = _EntityCatalog.retailers
          .firstWhere((element) => element.id == owner.id);
      return retailer;
    }
  }

  @override
  Future<AppTransactionsStateModel> loadAppTransactionsState() async {
    var data = await rootBundle.loadString('mock_data/appTransactions.json');
    return _loadAppTransactionsState(data);
  }

  @override
  void updateRetailerParamsHTTP(String simulationId, String retailerName,
      {double? strategy, double? sustainabilityRating}) {
    if (strategy != null) {
      _updateRetailerStrategy(retailerName, strategy);
    }
    if (sustainabilityRating != null) {
      _updateRetailerSustainabilityRating(retailerName, sustainabilityRating);
    }
  }

  @override
  void updateRetailerParamsWS(String simulationId, String retailerName,
      {double? strategy, double? sustainabilityRating}) {
    updateRetailerParamsHTTP(simulationId, retailerName,
        strategy: strategy, sustainabilityRating: sustainabilityRating);
  }
}

class MarketStateViewerFactory {
  factory MarketStateViewerFactory.create([bool mock = true]) {
    if (mock) {
      _instance ??= MarketStateViewerFactory._privateConstruct(
          null, MarketStateViewerMock.create());
    } else {
      _instance ??= MarketStateViewerFactory._privateConstruct(
          MarketStateViewer.create(), null);
    }
    return _instance!;
  }

  MarketStateViewerFactory._privateConstruct(
    this.realInstance,
    this.mockInstance,
  );

  static MarketStateViewerFactory? _instance;

  final MarketStateViewer? realInstance;
  final MarketStateViewerMock? mockInstance;
}

class AggregatedRetailers {
  final BankAccountViewModel balance;
  final CostModel balanceMoney;
  final List<SaleModel> salesHistory;
  final SalesAggregationModel totalSales;

  final List<String> retailerNames;

  String get combinedNames => retailerNames.join(', ');

  AggregatedRetailers(
      {required this.balance,
      required this.balanceMoney,
      required this.salesHistory,
      required this.totalSales,
      this.retailerNames = const <String>['']});

  static AggregatedRetailers zero() => AggregatedRetailers(
      balance: BankAccountViewModel.dummy(),
      balanceMoney: CostModel(0.0, 'GBP'),
      salesHistory: <SaleModel>[],
      totalSales: SalesAggregationModel(
        totalCostByCcy: {},
        totalMoneySentByCcy: {},
        totalGPIssued: 0.0,
        numItemsIssued: 0,
        itemCountMap: {},
      ));
}

class LoadEntitiesResult {
  final List<RetailerModel> retailers;
  final List<CustomerModel> customers;
  final AggregatedRetailers retailersCluster;

  LoadEntitiesResult(
      {required this.retailers,
      required this.customers,
      required this.retailersCluster});

  bool get isEmpty => retailers.isEmpty && customers.isEmpty;

  bool get isNotEmpty => !isEmpty;
}

class LoadTransactionsForEntityResult {
  final List<TransactionModel> transactionsFromEntity;
  final List<TransactionModel> transactionsToEntity;

  LoadTransactionsForEntityResult(
      {required this.transactionsFromEntity,
      required this.transactionsToEntity});

  bool get isEmpty =>
      transactionsFromEntity.isEmpty && transactionsToEntity.isEmpty;

  bool get isNotEmpty => !isEmpty;
}

class LoadSalesForItem {
  final List<SaleModel> salesForItem;

  LoadSalesForItem({required this.salesForItem});

  bool get isEmpty => salesForItem.isEmpty;

  bool get isNotEmpty => !isEmpty;
}

class SimulationProgressData {
  SimulationProgressData({required this.iterationNumber, required dynamic data})
      : runningSum = SimulationProgressDataSeries(
            salesCount:
                Map<String, num>.from(data["running_sum"]["sales_count"]),
            greenPointsIssued: Map<String, num>.from(
                data["running_sum"]["green_points_issued"])),
        runningAverage = SimulationProgressDataSeries(
            salesCount:
                Map<String, num>.from(data["running_average"]["sales_count"]),
            greenPointsIssued: Map<String, num>.from(
                data["running_average"]["green_points_issued"])),
        runningVariance = SimulationProgressDataSeries(
            salesCount:
                Map<String, num>.from(data["running_variance"]["sales_count"]),
            greenPointsIssued: Map<String, num>.from(
                data["running_variance"]["green_points_issued"]));

  final SimulationProgressDataSeries runningSum;
  final SimulationProgressDataSeries runningAverage;
  final SimulationProgressDataSeries runningVariance;
  final int iterationNumber;
}

class SimulationProgressDataSeries {
  final Map<String, num> salesCount;
  final Map<String, num> greenPointsIssued;

  const SimulationProgressDataSeries(
      {required this.salesCount, required this.greenPointsIssued});
}
