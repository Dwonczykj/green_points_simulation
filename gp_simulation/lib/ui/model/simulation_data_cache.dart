import '../network/network.dart';
import 'all_models.dart';

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

class IterationDataPoint {
  final String retailer;
  final num? datapoint;
  final int iterationNumber;
  final String seriesName;
  const IterationDataPoint(
      this.iterationNumber, this.retailer, this.datapoint, this.seriesName);
}
