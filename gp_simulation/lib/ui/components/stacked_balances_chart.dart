import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/material.dart';
import '../model/all_models.dart';
import '../../utils/number_formatting.dart';

class StackedBalancesChart extends StatelessWidget {
  StackedBalancesChart({
    Key? key,
    required this.chartTitle,
    required this.series,
    this.height,
    this.width,
  }) : super(key: key);

  final String chartTitle;
  final double? height;
  final double? width;
  List<charts.Series<dynamic, String>> series;

  _getChart() {
    return charts.BarChart(
      series,
      animate: true,
      animationDuration: Duration(seconds: 3),
      defaultInteractions: true,
      // behaviors: [

      // ],
      domainAxis: charts.AxisSpec<String>(
          renderSpec: charts.SmallTickRendererSpec(
              labelStyle: charts.TextStyleSpec(
                  fontSize: 12, color: charts.Color.white)),
          showAxisLine: true),
      primaryMeasureAxis: charts.NumericAxisSpec(
          renderSpec: charts.SmallTickRendererSpec(
              labelStyle: charts.TextStyleSpec(
                  fontSize: 12, color: charts.Color.white)),
          showAxisLine: true),
      barRendererDecorator: charts.BarLabelDecorator(
          insideLabelStyleSpec: charts.TextStyleSpec(
              fontSize: 12,
              color: charts.ColorUtil.fromDartColor(
                  Color.fromARGB(255, 228, 207, 18))),
          outsideLabelStyleSpec:
              charts.TextStyleSpec(fontSize: 12, color: charts.Color.white)),
      barGroupingType: charts.BarGroupingType.stacked,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height,
      width: width,
      padding: EdgeInsets.all(20),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Column(
            children: <Widget>[
              Text(
                chartTitle,
                style: Theme.of(context).textTheme.bodyText2,
              ),
              Expanded(
                child: _getChart(),
              )
            ],
          ),
        ),
      ),
    );
  }
}
