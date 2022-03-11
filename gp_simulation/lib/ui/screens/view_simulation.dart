import 'dart:async';
import 'dart:math' as math;

import 'package:charts_flutter/flutter.dart' as charts;
import 'package:logging/logging.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webtemplate/ui/network/market_state_viewer.dart';
import 'package:webtemplate/ui/screens/i_page_wrapper.dart';
import 'package:webtemplate/utils/string_extensions.dart';

enum ViewAggregationType { runningSum, runningAverage, runningVariance }
enum ViewMeasureType { salesCount, greenPointsIssued }

class ViewSimulationPage extends StatelessWidget {
  const ViewSimulationPage({Key? key}) : super(key: key);
  static const title = 'Retailer Simulation Results';

  @override
  Widget build(BuildContext context) {
    return IPageWrapper(
        title: title,
        childGetter: (marketStateViewer, snapshot) =>
            ViewSimulation(marketStateViewer: marketStateViewer));
  }
}

class ViewSimulation extends StatefulWidget {
  const ViewSimulation({Key? key, required this.marketStateViewer})
      : super(key: key);

  final IMarketStateViewer marketStateViewer;

  @override
  _ViewSimulationState createState() => _ViewSimulationState();
}

//TODO: Design Spec: Add ability to filter a particular retailer line on the graph and then view historical sims to see the effects of tweaking the retailer's parameters.
class _ViewSimulationState extends State<ViewSimulation> {
  StreamSubscription<dynamic>? _subscription;

  var chartData = <charts.Series<IterationDataPoint, int>>[];
  final log = Logger('_ViewSimulationState');
  List<String> runningSimulationsWithIds = <String>[];
  late List<String>? retailerNames = null;
  late Map<String, Color>? retailerColorMap = null;
  late SimulationDataCache? data = null;
  var viewAggType = ViewAggregationType.runningAverage;
  ViewMeasureType viewMeasType = ViewMeasureType.salesCount;
  var backingData = <String,
      Map<String, Map<String, charts.Series<IterationDataPoint, int>>>>{};
  String connectionStatus = 'N/A';

  List<charts.Series<IterationDataPoint, int>> get chartDataGetter =>
      backingData.entries
          .where((element) => element.key == viewAggType.name)
          .expand((element) => element.value.entries
              .where((subMeas) => subMeas.key == viewMeasType.name)
              .expand((measType) => measType.value.entries
                  .map((retailerName) => retailerName.value)
                  .toList()))
          .toList();
  String get title =>
      ('Retailer ${viewMeasType.name.toSentenceCaseFromCamelCase()}');

  void registerWSSNotifactions() {
    _subscription = widget.marketStateViewer.onSimulationProgress.listen(
      (SimulationProgressData? wsMessage) {
        if (wsMessage != null) {
          if (retailerNames == null) {
            retailerNames = wsMessage.runningAverage.salesCount.keys.toList();
            retailerColorMap = Map<String, Color>.fromEntries(retailerNames!
                .map((rname) => MapEntry<String, Color>(
                    rname,
                    Color((math.Random().nextDouble() * 0xFFFFFF).toInt())
                        .withOpacity(1.0))));
            data = SimulationDataCache(wsMessage);
          } else {
            data!.append(wsMessage);
          }

          setState(() {
            backingData = data!.mapAggType((aggType, seriesColn) =>
                seriesColn.map((seriesName, seriesByRetailer) =>
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

            chartData = backingData.entries
                .where((element) => element.key == viewAggType.name)
                .expand((element) => element.value.entries
                    .where((subMeas) => subMeas.key == viewMeasType.name)
                    .expand((subMeas) => subMeas.value.entries
                        .map((retailerName) => retailerName.value)
                        .toList()))
                .toList();
          });
        }
      },
      onDone: () {
        log.info('Transaction stream closed!');
      },
    );
  }

  @override
  void initState() {
    registerWSSNotifactions();
    widget.marketStateViewer.addListener(_listenSocket);
  }

  @override
  void dispose() {
    super.dispose();
    widget.marketStateViewer.removeListener(_listenSocket);
    _subscription!.cancel();
  }

  static List<charts.Series<IterationDataPoint, int>> _createSampleData() {
    const data = [
      IterationDataPoint(0, 'ASDA', 5, 'ASDA Sales'),
      IterationDataPoint(1, 'ASDA', 25, 'ASDA Sales'),
      IterationDataPoint(2, 'ASDA', 100, 'ASDA Sales'),
      IterationDataPoint(3, 'ASDA', 75, 'ASDA Sales'),
    ];

    return [
      charts.Series<IterationDataPoint, int>(
        id: 'Dummy Data',
        colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
        domainFn: (IterationDataPoint sales, _) => sales.iterationNumber,
        measureFn: (IterationDataPoint sales, _) => sales.datapoint,
        data: data,
      )
    ];
  }

  _listenSocket() {
    setState(() {
      connectionStatus = widget.marketStateViewer.connectionStatus;
    });
  }

  @override
  Widget build(BuildContext context) {
    final marketStateService = widget.marketStateViewer;
    // return Scaffold(
    //       appBar: AppBar(
    //       backgroundColor: Theme.of(context).bottomAppBarColor,
    //       title: Text(title),
    //       actions: <Widget>[
    //         Padding(
    //           padding: const EdgeInsets.only(right: 8.0),
    //           child: Column(
    //               mainAxisAlignment: MainAxisAlignment.center,
    //               children: marketStateService.webSocketConnected
    //                   ? [
    //                       Icon(Icons.wifi, size: 25),
    //                       Text(marketStateService.connectionStatus),
    //                     ]
    //                   : [
    //                       Icon(Icons.wifi_off, size: 25),
    //                       Text(marketStateService.connectionStatus),
    //                     ]),
    //         )
    //       ],
    //       ),
    //       body: SafeArea(
    //         child:
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        Expanded(
            child: Center(
          child: Stack(
            alignment: Alignment.center,
            children: <Widget>[
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: <Widget>[
                  Column(
                    children: <Widget>[
                      Padding(
                        padding: EdgeInsets.only(left: 24.0),
                        child: Text(
                            'Measure: ${viewMeasType.name.toSentenceCaseFromCamelCase()}'),
                      ),
                      Align(
                        alignment: Alignment.topLeft,
                        child: SizedBox(
                          width: ViewMeasureType.values.length * 100,
                          height: 40,
                          child: Slider(
                            value: viewMeasType.index.toDouble(),
                            label: viewMeasType.name,
                            divisions: (ViewMeasureType.values.length - 1),
                            min: 0.0,
                            max: (ViewMeasureType.values.length - 1).toDouble(),
                            onChangeEnd: (value) {
                              var i = value.round();
                              setState(() {
                                viewMeasType = ViewMeasureType.values[i];
                                chartData = backingData.entries
                                    .where((element) =>
                                        element.key == viewAggType.name)
                                    .expand((element) => element.value.entries
                                        .where((subMeas) =>
                                            subMeas.key == viewMeasType.name)
                                        .expand((subEl) => subEl.value.entries
                                            .map((retailerName) =>
                                                retailerName.value)
                                            .toList()))
                                    .toList();
                              });
                            },
                            onChanged: (double value) {
                              // setState({});
                            },
                          ),
                        ),
                      ),
                    ],
                  ),
                  Column(
                    children: <Widget>[
                      Padding(
                        padding: EdgeInsets.only(left: 24.0),
                        child: Text(
                            'Aggregation: ${viewAggType.name.toSentenceCaseFromCamelCase()}'),
                      ),
                      Align(
                        alignment: Alignment.topRight,
                        child: SizedBox(
                          width: ViewAggregationType.values.length * 100,
                          height: 40,
                          child: Slider(
                            value: viewAggType.index.toDouble(),
                            label: viewAggType.name,
                            divisions: (ViewAggregationType.values.length - 1),
                            min: 0.0,
                            max: (ViewAggregationType.values.length - 1)
                                .toDouble(),
                            onChangeEnd: (value) {
                              var i = value.round();
                              setState(() {
                                viewAggType = ViewAggregationType.values[i];
                                chartData = backingData.entries
                                    .where((element) =>
                                        element.key == viewAggType.name)
                                    .expand((element) => element.value.entries
                                        .expand((subEl) => subEl.value.entries
                                            .where((subMeas) =>
                                                subMeas.key ==
                                                viewMeasType.name)
                                            .map((retailerName) =>
                                                retailerName.value)
                                            .toList()))
                                    .toList();
                              });
                            },
                            onChanged: (double value) {
                              // setState({});
                            },
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              // SimpleLineChart.withSampleData(),
              chartData.isNotEmpty
                  ? charts.LineChart(
                      chartDataGetter, //TODO P1: See if still works with the getter -> [this.chartDataGetter]
                      // customSeriesRenderers: [],
                      animate:
                          true, //TODO P1: Also filter SalesCount vs GPIssues with a slider
                      animationDuration: const Duration(
                          milliseconds:
                              50), //TODO: Improve the potential speed of a simulation.
                      defaultInteractions: true,
                      // Add the legend behavior to the chart to turn on legends.
                      // This example shows how to change the position and justification of
                      // the legend, in addition to altering the max rows and padding.
                      behaviors: [
                        charts.SeriesLegend(
                          // Positions for "start" and "end" will be left and right respectively
                          // for widgets with a build context that has directionality ltr.
                          // For rtl, "start" and "end" will be right and left respectively.
                          // Since this example has directionality of ltr, the legend is
                          // positioned on the right side of the chart.
                          position: charts.BehaviorPosition.end,
                          // For a legend that is positioned on the left or right of the chart,
                          // setting the justification for [endDrawArea] is aligned to the
                          // bottom of the chart draw area.
                          outsideJustification:
                              charts.OutsideJustification.endDrawArea,
                          // By default, if the position of the chart is on the left or right of
                          // the chart, [horizontalFirst] is set to false. This means that the
                          // legend entries will grow as new rows first instead of a new column.
                          horizontalFirst: false,
                          // By setting this value to 2, the legend entries will grow up to two
                          // rows before adding a new column.
                          // desiredMaxRows: 2,
                          // By setting this value to 2, the legend entries will grow up to two
                          // rows before adding a new column.
                          desiredMaxColumns: 2,
                          // This defines the padding around each legend entry.
                          cellPadding:
                              new EdgeInsets.only(right: 4.0, bottom: 4.0),
                          // Render the legend entry text with custom styles.
                          entryTextStyle: charts.TextStyleSpec(
                              color: charts.ColorUtil.fromDartColor(
                                  Theme.of(context)
                                          .primaryTextTheme
                                          .displaySmall
                                          ?.color ??
                                      Colors.lime),
                              // fontFamily: 'Georgia',
                              fontSize: 16),
                        ),
                      ],
                      domainAxis: const charts.AxisSpec<num>(
                          renderSpec: charts.SmallTickRendererSpec(
                              labelStyle: charts.TextStyleSpec(
                                  fontSize: 12, color: charts.Color.white)),
                          showAxisLine: true),
                      primaryMeasureAxis: const charts.NumericAxisSpec(
                          renderSpec: charts.SmallTickRendererSpec(
                              labelStyle: charts.TextStyleSpec(
                                  fontSize: 12, color: charts.Color.white)),
                          showAxisLine: true),
                    )
                  : const FlutterLogo(
                      size: 100.0,
                      duration: Duration(seconds: 5),
                      curve: Curves.bounceInOut),
              Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: <Widget>[
                  Align(
                      alignment: Alignment.bottomCenter,
                      child: RaisedButton(
                        child: const Text('Run Simulation'),
                        onPressed: () {
                          marketStateService
                              .startFullSimulation(0.1, 500)
                              .then((value) {
                            if (value != null) {
                              setState(() {
                                runningSimulationsWithIds
                                    .add(value.simulationId);
                              });
                            }
                          });
                        },
                      )),
                  Padding(
                    padding: EdgeInsets.only(left: 4.0),
                    child: Text(''),
                  ),
                ],
              )
            ],
          ),
        ))
      ],
    );
    // ));
  }
}

class IterationDataPoint {
  final String retailer;
  final num? datapoint;
  final int iterationNumber;
  final String seriesName;
  const IterationDataPoint(
      this.iterationNumber, this.retailer, this.datapoint, this.seriesName);
}

class SimulationDataCache {
  final Map<String, SimulationDataCache_SeriesCollection> data;

  void append(SimulationProgressData message) {
    data['runningSum']?.append(message.runningSum, message.iterationNumber);
    data['runningAverage']
        ?.append(message.runningAverage, message.iterationNumber);
    data['runningVariance']
        ?.append(message.runningVariance, message.iterationNumber);
  }

  Map<String, T> mapAggType<T>(
      T Function(
              String aggType, SimulationDataCache_SeriesCollection seriesColn)
          func) {
    return data.map((aggType, seriesColn) =>
        MapEntry<String, T>(aggType, func(aggType, seriesColn)));
  }

  SimulationDataCache(SimulationProgressData initialMessage)
      : data = {
          'runningSum': SimulationDataCache_SeriesCollection(
              initialMessage.runningSum, initialMessage.iterationNumber),
          'runningAverage': SimulationDataCache_SeriesCollection(
              initialMessage.runningAverage, initialMessage.iterationNumber),
          'runningVariance': SimulationDataCache_SeriesCollection(
              initialMessage.runningVariance, initialMessage.iterationNumber),
        };
}

class SimulationDataCache_SeriesCollection {
  Map<String, T> map<T>(
      T Function(
              String aggType, Map<String, List<IterationDataPoint>> seriesColn)
          func) {
    return data.map((aggType, seriesColn) =>
        MapEntry<String, T>(aggType, func(aggType, seriesColn)));
  }

  final Map<String, Map<String, List<IterationDataPoint>>> data;

  SimulationDataCache_SeriesCollection(
      SimulationProgressDataSeries series, int firstIterationNumber)
      : data = {
          'salesCount': series.salesCount.map((rname, value) => MapEntry(
                  rname, <IterationDataPoint>[
                IterationDataPoint(
                    firstIterationNumber, rname, value, 'salesCount')
              ])),
          'greenPointsIssued': series.greenPointsIssued.map((rname, value) =>
              MapEntry(rname, <IterationDataPoint>[
                IterationDataPoint(
                    firstIterationNumber, rname, value, 'greenPointsIssued')
              ])),
        };

  void append(SimulationProgressDataSeries series, int iterationNumber) {
    data['salesCount']?.forEach((rname, s) {
      s.add(IterationDataPoint(
          iterationNumber, rname, series.salesCount[rname], 'salesCount'));
    });
    data['greenPointsIssued']?.forEach((rname, s) {
      s.add(IterationDataPoint(iterationNumber, rname,
          series.greenPointsIssued[rname], 'greenPointsIssued'));
    });
  }
}

// AggregationType -> WhatCalculated -> RetailerName -> LatestPoint
// AggregationType -> WhatCalculated -> RetailerName -> charts.Series(pointsHistory)
