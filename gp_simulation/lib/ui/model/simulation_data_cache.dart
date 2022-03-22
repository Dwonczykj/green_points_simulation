import '../network/network.dart';
import 'all_models.dart';
import 'app_state_manager.dart';

class SimulationDataCache {
  final Map<String, SimulationDataCache_SeriesCollection> data;

  void append(SimulationProgressData message) {
    data['runningSum']?.append(
        message.runningSum, message.iterationNumber, message.simConfig);
    data['runningAverage']?.append(
        message.runningAverage, message.iterationNumber, message.simConfig);
    data['runningVariance']?.append(
        message.runningVariance, message.iterationNumber, message.simConfig);
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
              initialMessage.runningSum,
              initialMessage.iterationNumber,
              initialMessage.simConfig),
          'runningAverage': SimulationDataCache_SeriesCollection(
              initialMessage.runningAverage,
              initialMessage.iterationNumber,
              initialMessage.simConfig),
          'runningVariance': SimulationDataCache_SeriesCollection(
              initialMessage.runningVariance,
              initialMessage.iterationNumber,
              initialMessage.simConfig),
        };
}

class SimulationDataCache_SeriesCollection {
  Map<String, T> map<T>(
      T Function(String aggType, Map<String, IterationDataPointList> seriesColn)
          func) {
    return data.map((aggType, seriesColn) =>
        MapEntry<String, T>(aggType, func(aggType, seriesColn)));
  }

  final Map<String, Map<String, IterationDataPointList>> data;

  static MapEntry<String, Map<String, IterationDataPointList>> _transformSeries(
      String seriesTypeName,
      Map<String, num> series,
      int firstIterationNumber,
      GemberAppConfig simConfig) {
    return MapEntry(
        seriesTypeName,
        series.map((rname, value) => MapEntry(
            rname,
            IterationDataPointList(rname, seriesTypeName,
                '$rname [${simConfig.toString()}]', <IterationDataPoint>[
              IterationDataPoint(firstIterationNumber, value)
            ]))));
  }

  void _appendSeries(String seriesTypeName, Map<String, num> retailerToNextVal,
      int iterationNumber, GemberAppConfig simConfig) {
    for (var retailerName in retailerToNextVal.keys) {
      var rnameWConfig =
          retailerName; //'$retailerName [${simConfig.toString()}]';
      if (data[seriesTypeName] != null) {
        if (data[seriesTypeName]!.containsKey(rnameWConfig)) {
          data[seriesTypeName]![rnameWConfig]!.add(IterationDataPoint(
              iterationNumber, retailerToNextVal[retailerName]));
        } else {
          data[seriesTypeName]![rnameWConfig] = IterationDataPointList(
              retailerName,
              seriesTypeName,
              '$retailerName [${simConfig.toString()}]', [
            IterationDataPoint(iterationNumber, retailerToNextVal[retailerName])
          ]);
        }
      }
    }
  }

  SimulationDataCache_SeriesCollection(SimulationProgressDataSeries series,
      int firstIterationNumber, GemberAppConfig simConfig)
      : data = Map.fromEntries([
          _transformSeries(ViewMeasureType.sales_count.name, series.salesCount,
              firstIterationNumber, simConfig),
          _transformSeries(ViewMeasureType.green_points_issued.name,
              series.greenPointsIssued, firstIterationNumber, simConfig),
          _transformSeries(ViewMeasureType.market_share.name,
              series.marketShare, firstIterationNumber, simConfig),
          _transformSeries(ViewMeasureType.total_sales_revenue.name,
              series.totalSalesRevenue, firstIterationNumber, simConfig),
          _transformSeries(ViewMeasureType.total_sales_revenue_less_GP.name,
              series.totalSalesRevenueLessGP, firstIterationNumber, simConfig),
        ]);

  void append(SimulationProgressDataSeries series, int iterationNumber,
      GemberAppConfig simConfig) {
    _appendSeries(ViewMeasureType.sales_count.name, series.salesCount,
        iterationNumber, simConfig);
    _appendSeries(ViewMeasureType.green_points_issued.name,
        series.greenPointsIssued, iterationNumber, simConfig);
    _appendSeries(ViewMeasureType.market_share.name, series.marketShare,
        iterationNumber, simConfig);
    _appendSeries(ViewMeasureType.total_sales_revenue.name,
        series.totalSalesRevenue, iterationNumber, simConfig);
    _appendSeries(ViewMeasureType.total_sales_revenue_less_GP.name,
        series.totalSalesRevenueLessGP, iterationNumber, simConfig);
  }
}

class IterationDataPoint {
  // final String retailer;
  final num? datapoint;
  final int iterationNumber;
  // final String seriesName;
  const IterationDataPoint(this.iterationNumber, this.datapoint);
}

class IterationDataPointList {
  final List<IterationDataPoint> points;

  /// the retatailer's name
  final String retailerName;

  /// the measure type of the data
  final String seriesTypeName;

  final String seriesLabel;

  IterationDataPointList(
      this.retailerName, this.seriesTypeName, this.seriesLabel,
      [this.points = const <IterationDataPoint>[]]);

  void add(IterationDataPoint point) {
    points.add(point);
    points.sort((a, b) => a.iterationNumber - b.iterationNumber);
  }
}
