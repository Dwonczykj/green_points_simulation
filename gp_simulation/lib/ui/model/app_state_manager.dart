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
enum ViewMeasureType {
  sales_count,
  green_points_issued,
  market_share,
  total_sales_revenue,
  total_sales_revenue_less_GP,
  totalSalesRevenueByItem
}

String getMeasureDTOLabel(ViewMeasureType measType) {
  if (measType == ViewMeasureType.sales_count) {
    return 'sales_count';
  } else if (measType == ViewMeasureType.green_points_issued) {
    return 'green_points_issued';
  } else if (measType == ViewMeasureType.market_share) {
    return 'market_share';
  } else if (measType == ViewMeasureType.total_sales_revenue) {
    return 'total_sales_revenue';
  } else if (measType == ViewMeasureType.total_sales_revenue_less_GP) {
    return 'total_sales_revenue_less_gp';
  } else if (measType == ViewMeasureType.totalSalesRevenueByItem) {
    return 'total_sales_revenue_by_item';
  } else {
    throw TypeError();
  }
}

String getAggregationDTOLabel(ViewAggregationType aggType) {
  if (aggType == ViewAggregationType.runningSum) {
    return 'running_sum';
  } else if (aggType == ViewAggregationType.runningAverage) {
    return 'running_average';
  } else if (aggType == ViewAggregationType.runningVariance) {
    return 'running_variance';
  } else {
    throw TypeError();
  }
}

String getMeasureUILabel(ViewMeasureType measType) {
  if (measType == ViewMeasureType.sales_count) {
    return 'Sales Vol.';
  } else if (measType == ViewMeasureType.green_points_issued) {
    return 'Gember pts issued';
  } else if (measType == ViewMeasureType.market_share) {
    return 'Market Share %';
  } else if (measType == ViewMeasureType.total_sales_revenue) {
    return 'Total Sales Revenue';
  } else if (measType == ViewMeasureType.total_sales_revenue_less_GP) {
    return 'Total Sales Revenue net GP';
  } else if (measType == ViewMeasureType.totalSalesRevenueByItem) {
    return 'Total Sales Revenue by item';
  } else {
    throw TypeError();
  }
}

String getAggregationUILabel(ViewAggregationType aggType) {
  if (aggType == ViewAggregationType.runningSum) {
    return 'cum. sum';
  } else if (aggType == ViewAggregationType.runningAverage) {
    return 'run. average';
  } else if (aggType == ViewAggregationType.runningVariance) {
    return 'run. variance';
  } else {
    throw TypeError();
  }
}

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
  List<String> _simulationComparisonHistoryIds = <String>[];
  SimulationComparisonHistory? simulationComparisonHistory;
  GemberProgressBar _simulationProgressBar = GemberProgressBar(i: 0, N: 1);
  GemberProgressBar get simulationProgressBar => _simulationProgressBar;
  List<String>? _retailerNames;

  List<String>? get retailerNames => _retailerNames;

  set retailerNames(List<String>? retailerNames) {
    _retailerNames = retailerNames;
    retailerColorMap = Map<String, Color>.fromEntries(retailerNames!.map(
        (rname) => MapEntry<String, Color>(
            rname,
            Color((math.Random().nextDouble() * 0xFFFFFF).toInt())
                .withOpacity(1.0))));
  }

  Map<String, Color>? retailerColorMap;

  String _connectionStatus = 'N/A';
  String get connectionStatus => _connectionStatus;

  bool _initialised = false;
  bool get initialised => _initialised;
  bool _initialising = false;
  bool get initialising => _initialising;

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
  final _simulationComparisonHistory = <String, RunSimulationResponseModel>{};

  bool get runningSimulation => marketStateViewerInst.simulationInProgress;

  bool get httpCallInProgress => marketStateViewerInst.httpCallInProgress;

  int basketSizeForNextSim = 2;

  int numTripsToShopsForNextSim = 1;

  int numCustomersForNextSim = 4;

  int maxN = 4;

  double convergenceThreshold = 0.0;

  String? _controlRetailer;

  String? get controlRetailer => _controlRetailer;

  double _retailerStrategy = RetailerStrategy.COMPETITIVE;

  double get retailerStrategy => _retailerStrategy;

  double _retailerSustainability = RetailerSustainability.AVERAGE;

  double get retailerSustainability => _retailerSustainability;

  bool get _simConfigValid => (basketSizeForNextSim != null &&
      numTripsToShopsForNextSim != null &&
      numCustomersForNextSim != null);

  GemberAppConfig? get simulationConfig => _simConfigValid
      ? GemberAppConfig(
          BASKET_FULL_SIZE: basketSizeForNextSim,
          NUM_SHOP_TRIPS_PER_ITERATION: numTripsToShopsForNextSim,
          NUM_CUSTOMERS: numCustomersForNextSim,
          maxN: maxN,
          convergenceTH: convergenceThreshold,
          strategy: retailerStrategy,
          sustainabilityBaseline: retailerSustainability,
          controlRetailerName: controlRetailer,
        )
      : null;

  ViewAggregationType _viewAggType = ViewAggregationType.runningAverage;
  ViewMeasureType _viewMeasType = ViewMeasureType.sales_count;
  ViewAggregationType get viewAggType => _viewAggType;
  String get viewAggTypeDTOLabel => getAggregationDTOLabel(_viewAggType);
  ViewMeasureType get viewMeasType => _viewMeasType;
  String get viewMeasTypeDTOLabel => getMeasureDTOLabel(_viewMeasType);

  var _simulationRunningMetricsChartBackingData = <String, dynamic>{};
  // var _simulationRunningMetricsChartBackingData = <String,Map<String, Map<String, charts.Series<IterationDataPoint, int>>>>{};

  List<WebCall> wsCallHist = <WebCall>[];
}

class AppStateManager extends ChangeNotifier with AppStateManagerProperties {
  static SimulationDataCache? _simulationDataCache;

  SimulationDataCache? get simulationDataCache => _simulationDataCache;

  AppStateManager._privateConstructor(
      {required IMarketStateViewer marketStateViewer}) {
    _instance = this;
    _initialised = false;
    marketStateViewerInst = marketStateViewer;
    marketStateViewerInst.addListener(_listenSocket);
    if (marketStateViewerInst is MarketStateViewer) {
      (marketStateViewerInst as MarketStateViewer)
          .callHistoryStream
          .listen((event) {
        wsCallHist.add(event);
      });
    }
    marketStateViewerInst.initialiseGemberPointsApp().then((appLoaded) {
      if (appLoaded) {
        return marketStateViewerInst.loadRetailerNames();
      } else {
        return Future.value(null);
      }
    }).then(
      (retailerNamesHttp) {
        retailerNames = retailerNamesHttp ?? <String>[];
        notifyListeners();
      },
    );

    registerWSSNotifactions();
  }

  static AppStateManager? _instance;

  factory AppStateManager.getInstance(IMarketStateViewer marketStateViewer) =>
      AppStateManager._instance ??
      AppStateManager._privateConstructor(marketStateViewer: marketStateViewer);

  _listenSocket() {
    _connectionStatus = marketStateViewerInst.connectionStatus;
    notifyListeners();
  }

  Future<LoadEntitiesResult> loadEntitiesWithParams(
      {required GemberAppConfig configOptions}) {
    _initialising = true;
    return marketStateViewerInst
        .loadEntities(configOptions: configOptions)
        .then((e) {
      entities = e;
      _initialising = false;
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
    if (simDetails != null) {
      var config = simDetails.simulationData.simulationConfig;
      _simulationComparisonHistory[config.toString()] = simDetails;
    }
    notifyListeners();
    return simDetails?.simulationId;
  }

  bool isRunningSim(String simulationId) =>
      runningSimulationsWithIds.contains(simulationId);

  bool addCompletedSimulation(SimulationResult simulation) {
    final removed = runningSimulationsWithIds.remove(simulation.simulationId);
    _simulationComparisonHistoryIds.add(simulation.simulationId);
    return removed;
  }

  bool changeControlRetailer(String? retailerNameOrNull) {
    var retailerExistsOrIsNull = true;
    if (retailerNameOrNull != null) {
      if ((entities?.isNotEmpty ?? false) &&
          (entities?.retailersCluster.retailerNames
                  .contains(retailerNameOrNull) ??
              false)) {
        retailerExistsOrIsNull = true;
      } else {
        retailerExistsOrIsNull = false;
      }
    }
    if (retailerExistsOrIsNull) {
      _controlRetailer = retailerNameOrNull;
    }
    return retailerExistsOrIsNull;
  }

  void refreshSimulationComparisonHistory() {
    if (_controlRetailer != null) {
      marketStateViewerInst.getSimulationComparisonHistory(
        simulationIds: _simulationComparisonHistoryIds,
        retailerName: _controlRetailer!,
        measureType: viewMeasTypeDTOLabel,
      );
    }
  }

  Map<String, Map<String, Map<String, charts.Series<IterationDataPoint, int>>>>?
      get simulationRunningMetricsChartBackingData =>
          _mapChartBackingData(filterRetailerName: controlRetailer);

  /**
   * runs one full simulation using the current simulation configuration 
   * set in the state of the [AppStateManager]
   */
  Future<String?> runFullSimulation() async {
    if (simulationConfig != null) {
      log.fine('Run full sim with config: $simulationConfig');
      return marketStateViewerInst
          .runFullSimulation(
            configOptions: simulationConfig!,
          )
          .then(_loadSimulationDetails);
    }
  }

  void updateNextSimConfig({
    int? basketFullSize,
    int? numTripsPerIteration,
    int? numCustomers,
    int? maximumNIterations,
    double? convergenceTH,
    double? strategy,
    double? sustainabilityBaseline,
    String? controlRetailerName,
  }) {
    GemberAppConfig allConfigOptions = GemberAppConfig(
      BASKET_FULL_SIZE: basketFullSize ?? basketSizeForNextSim,
      NUM_SHOP_TRIPS_PER_ITERATION:
          numTripsPerIteration ?? numTripsToShopsForNextSim,
      NUM_CUSTOMERS: numCustomers ?? numCustomersForNextSim,
      maxN: maximumNIterations ?? maxN,
      convergenceTH: convergenceTH ?? convergenceThreshold,
      strategy: strategy ?? retailerStrategy,
      sustainabilityBaseline: sustainabilityBaseline ?? retailerSustainability,
      controlRetailerName: controlRetailerName ?? controlRetailer,
    );
    print('value changed to $allConfigOptions');
    updateNextSimConfigNoNotifiy(configOptions: allConfigOptions);
    notifyListeners();
  }

  void updateNextSimConfigNoNotifiy({required GemberAppConfig configOptions}) {
    basketSizeForNextSim = configOptions.BASKET_FULL_SIZE;
    numTripsToShopsForNextSim = configOptions.NUM_SHOP_TRIPS_PER_ITERATION;
    numCustomersForNextSim = configOptions.NUM_CUSTOMERS;
    maxN = configOptions.maxN;
    convergenceThreshold = configOptions.convergenceTH;
    changeControlRetailer(configOptions.controlRetailerName);
    _retailerStrategy = configOptions.strategy;
    _retailerSustainability = configOptions.sustainabilityBaseline;
  }

  /// update the Aggregation type that is focused on in the app.
  /// i.e. to focus on the running average or the running variance of a simulation.
  void updateAggregationType(ViewAggregationType newAgg) {
    _viewAggType = newAgg;
  }

  /// update the retailer performance measure to view.
  /// i.e. to focus on the Sales Volume or the Volume of Gember Points issued.
  void updateMeasureType(ViewMeasureType newMeasurementFocus) {
    _viewMeasType = newMeasurementFocus;
    notifyListeners();
  }

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
          _simulationProgressBar = GemberProgressBar(
              i: wsMessage.iterationNumber, N: wsMessage.maxNIterations);

          retailerNames ??= wsMessage.runningAverage.salesCount.keys.toList();

          _simulationDataCache ??= SimulationDataCache(wsMessage);
          _simulationDataCache!.append(wsMessage);
          notifyListeners();
          //TODO: Emphasize the lines of the retailer in focus and show a comparison history of this retailer

          // _simulationRunningMetricsChartBackingData = simulationDataCache!
          //     .mapAggType((aggType, seriesColn) => seriesColn.map((seriesName,
          //             seriesByRetailer) =>
          //         seriesByRetailer.map((rname, datapoints) => MapEntry(
          //             rname,
          //             charts.Series<IterationDataPoint, int>(
          //               id: '$rname $seriesName ($aggType)',
          //               seriesCategory: aggType,
          //               labelAccessorFn: (datapoint, _) =>
          //                   '$rname $seriesName ($aggType)',
          //               colorFn: (_, __) => charts.ColorUtil.fromDartColor(
          //                   retailerColorMap?[rname] ??
          //                       const Color.fromRGBO(100, 100, 100, 1)),
          //               domainFn: (datapoint, _) => datapoint.iterationNumber,
          //               measureFn: (datapoint, _) => datapoint.datapoint,
          //               data: datapoints,
          //             )))));
        }
      },
      onDone: () {
        log.info('Transaction stream closed!');
      },
    );
  }

  Map<String, Map<String, Map<String, charts.Series<IterationDataPoint, int>>>>? _mapChartBackingData(
          {String? filterRetailerName}) =>
      _simulationDataCache?.mapAggType((aggType, seriesColn) => seriesColn.map(
          (seriesName, seriesByRetailer) => Map.fromEntries(
              seriesByRetailer.entries.where((retAndConfNameToPointsList) =>
                  retAndConfNameToPointsList.value.retailerName == filterRetailerName ||
                  filterRetailerName == null)).map((retailerName, datapoints) => MapEntry(
              datapoints.seriesLabel,
              charts.Series<IterationDataPoint, int>(
                id: datapoints.seriesLabel,
                seriesCategory: aggType,
                labelAccessorFn: (datapoint, _) =>
                    '$retailerName $seriesName ($aggType)',
                colorFn: (_, __) => charts.ColorUtil.fromDartColor(
                    retailerColorMap?[retailerName] ??
                        Color((math.Random().nextDouble() * 0xFFFFFF).toInt())
                            .withOpacity(1.0)),
                domainFn: (datapoint, _) => datapoint.iterationNumber,
                measureFn: (datapoint, _) => datapoint.datapoint,
                data: datapoints.points,
              )))));
}

class GemberProgressBar {
  GemberProgressBar({required this.i, required this.N});

  final int i;
  final int N;

  @override
  String toString() {
    return '$i/$N';
  }
}
