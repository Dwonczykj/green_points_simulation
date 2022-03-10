import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/material.dart';
import '../model/models.dart';
import '../../utils/number_formatting.dart';

class BalancesChart<T extends EntityModel> extends StatelessWidget {
  BalancesChart({
    Key? key,
    required this.entities,
    required this.chartTitle,
    this.domainFn,
    required this.measureFn,
    this.colorFn,
  })
      : super(key: key);

  final List<T> entities;
  final String chartTitle;
  String Function(T model, int? i)? domainFn;
  num? Function(T model, int? i) measureFn;
  charts.Color Function(T model, int? i)? colorFn;

  @override
  Widget build(BuildContext context) {
    
    List<charts.Series<T, String>> series = [
      charts.Series(
        id: chartTitle,
          data: entities,
        domainFn: (seriesItem, i) =>
            domainFn != null ? domainFn!(seriesItem, i) : seriesItem.name,
        // measureFn: (seriesItem, _) => CurrencyNumberFormat.fromCostModel(seriesItem.balanceMoney).format(seriesItem.balanceMoney.amount),
        measureFn: (seriesItem, i) => measureFn(seriesItem, i),
        colorFn: (seriesItem, i) => colorFn != null
            ? colorFn!(seriesItem, i)
            : charts.ColorUtil.fromDartColor(Colors.blue),
      ),
      
    ];

    return Container(
      height: 400,
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
                child: charts.BarChart(series, animate: true),
              )
            ],
          ),
        ),
      ),
    );
  }
}
