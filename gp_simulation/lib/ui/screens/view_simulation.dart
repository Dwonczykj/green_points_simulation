import 'dart:async';
import 'dart:math' as math;

import 'package:charts_flutter/flutter.dart' as charts;
import 'package:logging/logging.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webtemplate/ui/network/market_state_viewer.dart';
import 'package:webtemplate/ui/screens/i_page_wrapper.dart';
import 'package:webtemplate/utils/string_extensions.dart';

import '../components/components.dart';
import '../model/models.dart';

class ViewSimulationPage extends StatelessWidget {
  const ViewSimulationPage({Key? key}) : super(key: key);
  static const title = 'Retailer Simulation Results';

  @override
  Widget build(BuildContext context) {
    return IPageWrapper(
        title: title,
        childGetter: (marketStateViewer, appStateManager) => ViewSimulation(
              marketStateViewer: marketStateViewer,
              appStateManager: appStateManager,
            ));
  }
}

class ViewSimulation extends StatefulWidget {
  const ViewSimulation(
      {Key? key,
      required this.marketStateViewer,
      required this.appStateManager})
      : super(key: key);

  final IMarketStateViewer marketStateViewer;
  final AppStateManager appStateManager;

  @override
  _ViewSimulationState createState() => _ViewSimulationState();
}

class _ViewSimulationState extends State<ViewSimulation> {
  final log = Logger('_ViewSimulationState');
  List<String> runningSimulationsWithIds = <String>[];

  // List<String>? get retailerNames => widget.appStateManager.retailerNames;
  // Map<String, Color>? get retailerColorMap =>
  //     widget.appStateManager.retailerColorMap;
  SimulationDataCache? get data => widget.appStateManager.simulationDataCache;

  ViewAggregationType get viewAggType => widget.appStateManager.viewAggType;
  ViewMeasureType get viewMeasType => widget.appStateManager.viewMeasType;

  String get connectionStatus => widget.appStateManager.connectionStatus;

  Map<String, Map<String, Map<String, charts.Series<IterationDataPoint, int>>>>?
      get backingData =>
          widget.appStateManager.simulationRunningMetricsChartBackingData;

  List<charts.Series<IterationDataPoint, int>> get chartDataGetter =>
      backingData?.entries
          .where((element) => element.key == viewAggType.name)
          .expand((element) => element.value.entries
              .where((subMeas) => subMeas.key == viewMeasType.name)
              .expand((measType) => measType.value.entries
                  .map((retailerName) => retailerName.value)
                  .toList()))
          .toList() ??
      <charts.Series<IterationDataPoint, int>>[];

  String get title =>
      ('Retailer ${viewMeasType.name.toSentenceCaseFromCamelCase()}');

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    super.dispose();
  }

  // static List<charts.Series<IterationDataPoint, int>> _createSampleData() {
  //   const data = [
  //     IterationDataPoint(0, 'ASDA', 5, 'ASDA Sales'),
  //     IterationDataPoint(1, 'ASDA', 25, 'ASDA Sales'),
  //     IterationDataPoint(2, 'ASDA', 100, 'ASDA Sales'),
  //     IterationDataPoint(3, 'ASDA', 75, 'ASDA Sales'),
  //   ];

  //   return [
  //     charts.Series<IterationDataPoint, int>(
  //       id: 'Dummy Data',
  //       colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
  //       domainFn: (IterationDataPoint sales, _) => sales.iterationNumber,
  //       measureFn: (IterationDataPoint sales, _) => sales.datapoint,
  //       data: data,
  //     )
  //   ];
  // }

  @override
  Widget build(BuildContext context) {
    var configureRetailerButtonLabel =
        widget.appStateManager.controlRetailer ?? 'Retailer';
    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      // crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        Align(
          alignment: Alignment.topRight,
          child: Flex(
            direction: Axis.vertical,
            mainAxisAlignment: MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.end,
            children: <Widget>[
              ConfigDialogDrowdown(
                appStateMgr: widget.appStateManager,
                label: 'Aggregation',
                value: widget.appStateManager.viewAggType,
                onChanged: (ViewAggregationType? value) {
                  widget.appStateManager.updateAggregationType(
                      value ?? ViewAggregationType.runningAverage);
                },
                labelsToValuesMap: Map<String, ViewAggregationType>.fromEntries(
                    ViewAggregationType.values
                        .map((v) => MapEntry(getAggregationUILabel(v), v))),
              ),
              ConfigDialogDrowdown(
                appStateMgr: widget.appStateManager,
                label: 'Performance measure',
                value: widget.appStateManager.viewMeasType,
                onChanged: (ViewMeasureType? value) {
                  widget.appStateManager
                      .updateMeasureType(value ?? ViewMeasureType.sales_count);
                },
                labelsToValuesMap: Map<String, ViewMeasureType>.fromEntries(
                    ViewMeasureType.values
                        .map((v) => MapEntry(getMeasureUILabel(v), v))),
              ),
            ],
          ),
        ),
        Expanded(
            child: Center(
          child: Stack(
            alignment: Alignment.center,
            children: <Widget>[
              
              // SimpleLineChart.withSampleData(),
              chartDataGetter.isNotEmpty
                  ? charts.LineChart(
                      chartDataGetter,
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
                          widget.appStateManager
                              .runFullSimulation()
                              .then((simId) {
                            if (simId != null) {
                              setState(() {
                                runningSimulationsWithIds.add(simId);
                              });
                            }
                          });
                        },
                      )),
                  Padding(
                    padding: EdgeInsets.only(left: 4.0, right: 4.0),
                    child: Text(''),
                  ),
                  Align(
                      alignment: Alignment.bottomCenter,
                      child: ElevatedButton(
                        child: Text('Configure $configureRetailerButtonLabel'),
                        onPressed: () {
                          _openConfigPopup(context);
                        },
                      )),
                ],
              )
            ],
          ),
        ))
      ],
    );
  }

  void _openConfigPopup(BuildContext context) {
    showDialog<String>(
      context: context,
      builder: (BuildContext context) =>
          ConfigRetailerDialog(fullScreen: false),
    );
  }
}





// AggregationType -> WhatCalculated -> RetailerName -> LatestPoint
// AggregationType -> WhatCalculated -> RetailerName -> charts.Series(pointsHistory)
