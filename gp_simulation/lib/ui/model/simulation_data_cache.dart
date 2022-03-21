import '../network/network.dart';
import 'all_models.dart';

class SimulationDataCache {
  final Map<String, SimulationDataCache_SeriesCollection> data;

  void append(SimulationProgressData message) {
    data['runningSum']?.append(
        message.runningSum, message.iterationNumber, message.simConfig);
    data['runningAverage']
        ?.append(
        message.runningAverage, message.iterationNumber, message.simConfig);
    data['runningVariance']
        ?.append(
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

  static MapEntry<String, Map<String, List<IterationDataPoint>>>
      _transformSeries(String seriesName, Map<String, num> series,
          int firstIterationNumber) {
    return MapEntry(
        seriesName,
        series.map((rname, value) => MapEntry(rname, <IterationDataPoint>[
              IterationDataPoint(firstIterationNumber, rname, value, seriesName)
            ])));
  }

  void _appendSeries(String seriesName, Map<String, num> series,
      int iterationNumber, GemberAppConfig simConfig) {
    data[seriesName]?.forEach((rname, s) {
      var ghostName = seriesName;
      if (s.any((element) =>
          element.iterationNumber == iterationNumber &&
          element.seriesName == seriesName)) {
        ghostName = '$seriesName [${simConfig.toString()}]';
      }
      s.add(
          IterationDataPoint(iterationNumber, rname, series[rname], ghostName));
    });
  }

  SimulationDataCache_SeriesCollection(
      SimulationProgressDataSeries series, int firstIterationNumber)
      : data = Map.fromEntries([
          _transformSeries(
              'salesCount', series.salesCount, firstIterationNumber),
          _transformSeries('greenPointsIssued', series.greenPointsIssued,
              firstIterationNumber),
          _transformSeries(
              'marketShare', series.marketShare, firstIterationNumber),
          _transformSeries('totalSalesRevenue', series.totalSalesRevenue,
              firstIterationNumber),
          _transformSeries('totalSalesRevenueLessGP',
              series.totalSalesRevenueLessGP, firstIterationNumber),
        ]);

  void append(SimulationProgressDataSeries series, int iterationNumber,
      GemberAppConfig simConfig) {
    _appendSeries('salesCount', series.salesCount, iterationNumber, simConfig);
    _appendSeries('greenPointsIssued', series.greenPointsIssued,
        iterationNumber, simConfig);
    _appendSeries(
        'marketShare', series.marketShare, iterationNumber, simConfig);
    _appendSeries('totalSalesRevenue', series.totalSalesRevenue,
        iterationNumber, simConfig);
    _appendSeries('totalSalesRevenueLessGP', series.totalSalesRevenueLessGP,
        iterationNumber, simConfig);
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
