import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:logging/logging.dart';
import 'package:charts_flutter/flutter.dart' as charts;

import '../network/network.dart';
import 'all_models.dart';
import 'simulation_data_cache.dart';

enum ViewAggregationType { runningSum, runningAverage, runningVariance }
enum ViewMeasureType { salesCount, greenPointsIssued }

/// An enum to switch between different types of tests to run in the simulation environment to demonstrate different features of how Gember Points work.
enum ScenarioTest {
  /// Test: Default non testing live simulation mode:
  realLifeSimulation,

  /// Test that creates n uniform retailers that all offer the same items and have the same sustainability rating. Idea is to see if a retailer's GP issuing strategy effects it sales and how...
  strategyEffectOnUniformRetailers,

  /// Test that creates n uniform retailers that all offer the same items and have the same GP issueing strategy. Idea is to see whether improving the sustainability and conscientiousness of a retailers supply chain and products effects its sales.
  improvingItemSustainability,
}

abstract class AppStateManagerProperties {
  List<String> runningSimulationsWithIds = <String>[];
  List<String>? retailerNames;
  Map<String, Color>? retailerColorMap;
  SimulationDataCache? simulationDataCache;

  String _connectionStatus = 'N/A';
  String get connectionStatus => _connectionStatus;

  bool _initialised = false;
  bool get initialised => _initialised;

  // set initialised(bool initialised) {
  //   _initialised = initialised;
  // }

  LoadEntitiesResult? entities;

  List<ScenarioTest> tests = <ScenarioTest>[
    ScenarioTest.realLifeSimulation,
    ScenarioTest.strategyEffectOnUniformRetailers,
    ScenarioTest.improvingItemSustainability,
  ];

  ScenarioTest _selectedScenarioTest = ScenarioTest.realLifeSimulation;
  ScenarioTest get selectedScenarioTest => _selectedScenarioTest;

  late final IMarketStateViewer marketStateViewerInst;

  final log = Logger('AppStateManager');

  RunSimulationResponseModel? _runningSimDetails;

  bool get runningSimulation => marketStateViewerInst.simulationInProgress;

  bool get httpCallInProgress => marketStateViewerInst.httpCallInProgress;

  int basketSizeForNextSim = 2;

  int numTripsToShopsForNextSim = 1;

  int numCustomersForNextSim = 4;

  int maxN = 1;

  double convergenceThreshold = 0.0;

  bool get _simConfigValid => (basketSizeForNextSim != null &&
      numTripsToShopsForNextSim != null &&
      numCustomersForNextSim != null);

  GemberAppConfig? get simulationConfig => _simConfigValid
      ? GemberAppConfig(
          BASKET_FULL_SIZE: basketSizeForNextSim,
          NUM_SHOP_TRIPS_PER_ITERATION: numTripsToShopsForNextSim,
          NUM_CUSTOMERS: numCustomersForNextSim,
          maxN: maxN,
          convergenceTH: convergenceThreshold)
      : null;

  ViewAggregationType _viewAggType = ViewAggregationType.runningAverage;
  ViewMeasureType _viewMeasType = ViewMeasureType.salesCount;
  ViewAggregationType get viewAggType => _viewAggType;
  ViewMeasureType get viewMeasType => _viewMeasType;

  var simulationRunningMetricsChartBackingData = <String,
      Map<String, Map<String, charts.Series<IterationDataPoint, int>>>>{};
}

class AppStateManager extends ChangeNotifier with AppStateManagerProperties {
  AppStateManager._privateConstructor(BuildContext context,
      {required IMarketStateViewer marketStateViewer}) {
    _instance = this;
    _initialised = false;
    // marketStateViewer = Provider.of<IMarketStateViewer>(context, listen: true);
    marketStateViewerInst = marketStateViewer;
    marketStateViewerInst.addListener(_listenSocket);
    marketStateViewerInst.initialiseGemberPointsApp();
  }

  static AppStateManager? _instance;

  factory AppStateManager.getInstance(
          BuildContext context, IMarketStateViewer marketStateViewer) =>
      AppStateManager._instance ??
      AppStateManager._privateConstructor(context,
          marketStateViewer: marketStateViewer);

  _listenSocket() {
    _connectionStatus = marketStateViewerInst.connectionStatus;
    notifyListeners();
  }

  Future<LoadEntitiesResult> loadEntitiesWithParams(
      {required GemberAppConfig configOptions}) {
    return marketStateViewerInst
        .loadEntities(configOptions: configOptions)
        .then((e) {
      entities = e;
      _initialised = true;
      notifyListeners();
      return e;
    });
  }

  /**
   * starts a single iteration to demonstrate how a single iteration would run.
   */
  Future<String?> runSingleIteration() async {
    if (simulationConfig != null) {
      return marketStateViewerInst
          .runIsolatedSimIteration(
            configOptions: simulationConfig!,
          )
          .then(_loadSimulationDetails);
    }
  }

  /**
   * starts a continuous simulation to represent a real life scenario in which we 
   * can tweak simulation parameters during the simulation to see how to affects sales charts etc...
   */
  Future<String?> runRealtimeSimulation() async {
    if (simulationConfig != null) {
      return marketStateViewerInst
          .runRealTimeScenario(
            configOptions: simulationConfig!,
          )
          .then(_loadSimulationDetails);
    }
  }

  String? _loadSimulationDetails(RunSimulationResponseModel? simDetails) {
    _runningSimDetails = simDetails;
    return simDetails?.simulationId;
  }

  /**
   * runs one full simulation using the current simulation configuration 
   * set in the state of the [AppStateManager]
   */
  Future<String?> runFullSimulation() async {
    if (simulationConfig != null) {
      return marketStateViewerInst
          .runFullSimulation(
            configOptions: simulationConfig!,
            maxN: maxN,
            convergenceThreshold: convergenceThreshold,
          )
          .then(_loadSimulationDetails);
    }
  }

  void updateNextSimConfig({required GemberAppConfig configOptions}) {
    basketSizeForNextSim = configOptions.BASKET_FULL_SIZE;
    numTripsToShopsForNextSim = configOptions.NUM_SHOP_TRIPS_PER_ITERATION;
    numCustomersForNextSim = configOptions.NUM_CUSTOMERS;
    maxN = configOptions.maxN;
    convergenceThreshold = configOptions.convergenceTH;
    notifyListeners();
  }

  /// update the Aggregation type that is focused on in the app.
  /// i.e. to focus on the running average or the running variance of a simulation.
  void updateAggregationType(ViewAggregationType newAgg) {
    _viewAggType = newAgg;
    notifyListeners();
  }

  /// update the retailer performance measure to view.
  /// i.e. to focus on the Sales Volume or the Volume of Gember Points issued.
  void updateMeasureType(ViewMeasureType newMeasurementFocus) {
    _viewMeasType = newMeasurementFocus;
    notifyListeners();
  }

  //todo 1 add set and get handlers for all the above properties and make into private fields.
  //todo 1.1 add notifiyListeners when any setter is used, move the fields getters and setters to a mixin so that the _private fields are not exposed to the class methods iether.

  StreamSubscription<dynamic>? _subscription;

  @override
  void dispose() {
    _subscription?.cancel();
    marketStateViewerInst.removeListener(_listenSocket);
    super.dispose();
  }

  void registerWSSNotifactions() {
    _subscription = marketStateViewerInst.onSimulationProgress.listen(
      (SimulationProgressData? wsMessage) {
        if (wsMessage != null) {
          if (retailerNames == null) {
            retailerNames = wsMessage.runningAverage.salesCount.keys.toList();
            retailerColorMap = Map<String, Color>.fromEntries(retailerNames!
                .map((rname) => MapEntry<String, Color>(
                    rname,
                    Color((math.Random().nextDouble() * 0xFFFFFF).toInt())
                        .withOpacity(1.0))));
            simulationDataCache = SimulationDataCache(wsMessage);
          } else {
            simulationDataCache!.append(wsMessage);
          }

          simulationRunningMetricsChartBackingData = simulationDataCache!
              .mapAggType((aggType, seriesColn) => seriesColn.map((seriesName,
                      seriesByRetailer) =>
                  seriesByRetailer.map((rname, datapoints) => MapEntry(
                      rname,
                      charts.Series<IterationDataPoint, int>(
                        id: '$rname $seriesName ($aggType)',
                        seriesCategory: aggType,
                        labelAccessorFn: (datapoint, _) =>
                            '$rname $seriesName ($aggType)',
                        colorFn: (_, __) => charts.ColorUtil.fromDartColor(
                            retailerColorMap?[rname] ??
                                const Color.fromRGBO(100, 100, 100, 1)),
                        domainFn: (datapoint, _) => datapoint.iterationNumber,
                        measureFn: (datapoint, _) => datapoint.datapoint,
                        data: datapoints,
                      )))));
        }
      },
      onDone: () {
        log.info('Transaction stream closed!');
      },
    );
  }
}
