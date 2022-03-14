import 'package:flutter/material.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:webtemplate/ui/network/network.dart';

import '../model/all_models.dart';

/// Sample ordinal data type.
class OrdinalSales {
  final String year;
  final int sales;

  OrdinalSales(this.year, this.sales);
}

class DummyScreen extends StatelessWidget {
  const DummyScreen(
      {Key? key, required this.retailers, required this.retailerCluster})
      : super(key: key);

  final List<RetailerModel> retailers;
  final AggregatedRetailers retailerCluster;

  Widget _getDummyWidget() {
    /// Create series list with multiple series

    // return charts.BarChart(
    //   _createSampleData(),
    //   animate: false,
    //   barGroupingType: charts.BarGroupingType.groupedStacked,
    // );
    var l3 = _createSampleData();
    final l2 = _createSampleDataObjs();
    final d2 = l2
        .map(
          (e) => {'domain': e.year, 'measure': e.sales},
        )
        .toList();
    final d = retailerCluster.totalSales.totalCostByCcy.keys
        .map((ccy) => retailers
            .map((seriesItem) => {
                  'domain': seriesItem.name,
                  'measure': seriesItem.totalSales.totalCostByCcy[ccy]?.amount
                })
            .toList())
        .toList();
    final l = retailerCluster.totalSales.totalCostByCcy.keys
        .map((ccy) => charts.Series(
              id: 'Retailer Sales [$ccy component]',
              data: retailers,
              domainFn: (RetailerModel seriesItem, int? i) => seriesItem.name,
              measureFn: (RetailerModel seriesItem, int? i) =>
                  seriesItem.totalSales.totalCostByCcy[ccy]?.amount.round() ??
                  0.0,
            ))
        .toList();
    return charts.BarChart(
      l,
      animate: false,
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
      // barGroupingType: charts.BarGroupingType.stacked,
    );
  }

  static List<OrdinalSales> _createSampleDataObjs() {
    final desktopSalesDataA = [
      new OrdinalSales('X2014', 5),
      new OrdinalSales('X2015', 25),
      new OrdinalSales('X2016', 100),
      new OrdinalSales('X2017', 75),
    ];

    final tableSalesDataA = [
      new OrdinalSales('X2014', 25),
      new OrdinalSales('X2015', 50),
      new OrdinalSales('X2016', 10),
      new OrdinalSales('X2017', 20),
    ];

    final mobileSalesDataA = [
      new OrdinalSales('X2014', 10),
      new OrdinalSales('X2015', 15),
      new OrdinalSales('X2016', 50),
      new OrdinalSales('X2017', 45),
    ];

    final desktopSalesDataB = [
      new OrdinalSales('X2014', 5),
      new OrdinalSales('X2015', 25),
      new OrdinalSales('X2016', 100),
      new OrdinalSales('X2017', 75),
    ];

    final tableSalesDataB = [
      new OrdinalSales('X2014', 25),
      new OrdinalSales('X2015', 50),
      new OrdinalSales('X2016', 10),
      new OrdinalSales('X2017', 20),
    ];

    final mobileSalesDataB = [
      new OrdinalSales('X2014', 10),
      new OrdinalSales('X2015', 15),
      new OrdinalSales('X2016', 50),
      new OrdinalSales('X2017', 45),
    ];

    return mobileSalesDataB;
  }

  static List<charts.Series<OrdinalSales, String>> _createSampleData() {
    final desktopSalesDataA = [
      new OrdinalSales('X2014', 5),
      new OrdinalSales('X2015', 25),
      new OrdinalSales('X2016', 100),
      new OrdinalSales('X2017', 75),
    ];

    final tableSalesDataA = [
      new OrdinalSales('X2014', 25),
      new OrdinalSales('X2015', 50),
      new OrdinalSales('X2016', 10),
      new OrdinalSales('X2017', 20),
    ];

    final mobileSalesDataA = [
      new OrdinalSales('X2014', 10),
      new OrdinalSales('X2015', 15),
      new OrdinalSales('X2016', 50),
      new OrdinalSales('X2017', 45),
    ];

    final desktopSalesDataB = [
      new OrdinalSales('X2014', 5),
      new OrdinalSales('X2015', 25),
      new OrdinalSales('X2016', 100),
      new OrdinalSales('X2017', 75),
    ];

    final tableSalesDataB = [
      new OrdinalSales('X2014', 25),
      new OrdinalSales('X2015', 50),
      new OrdinalSales('X2016', 10),
      new OrdinalSales('X2017', 20),
    ];

    final mobileSalesDataB = [
      new OrdinalSales('X2014', 10),
      new OrdinalSales('X2015', 15),
      new OrdinalSales('X2016', 50),
      new OrdinalSales('X2017', 45),
    ];

    return [
      new charts.Series<OrdinalSales, String>(
        id: 'Desktop A',
        // seriesCategory: 'A',
        domainFn: (OrdinalSales sales, _) => sales.year,
        measureFn: (OrdinalSales sales, _) => sales.sales,
        data: desktopSalesDataA,
      ),
      new charts.Series<OrdinalSales, String>(
        id: 'Tablet A',
        // seriesCategory: 'A',
        domainFn: (OrdinalSales sales, _) => sales.year,
        measureFn: (OrdinalSales sales, _) => sales.sales,
        data: tableSalesDataA,
      ),
      // new charts.Series<OrdinalSales, String>(
      //   id: 'Mobile A',
      //   seriesCategory: 'A',
      //   domainFn: (OrdinalSales sales, _) => sales.year,
      //   measureFn: (OrdinalSales sales, _) => sales.sales,
      //   data: mobileSalesDataA,
      // ),
      // new charts.Series<OrdinalSales, String>(
      //   id: 'Desktop B',
      //   seriesCategory: 'B',
      //   domainFn: (OrdinalSales sales, _) => sales.year,
      //   measureFn: (OrdinalSales sales, _) => sales.sales,
      //   data: desktopSalesDataB,
      // ),
      // new charts.Series<OrdinalSales, String>(
      //   id: 'Tablet B',
      //   seriesCategory: 'B',
      //   domainFn: (OrdinalSales sales, _) => sales.year,
      //   measureFn: (OrdinalSales sales, _) => sales.sales,
      //   data: tableSalesDataB,
      // ),
      // new charts.Series<OrdinalSales, String>(
      //   id: 'Mobile B',
      //   seriesCategory: 'B',
      //   domainFn: (OrdinalSales sales, _) => sales.year,
      //   measureFn: (OrdinalSales sales, _) => sales.sales,
      //   data: mobileSalesDataB,
      // ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.red,
        title: Text("World of Warcraft Subscribers"),
      ),
      body: Center(child: _getDummyWidget()),
    );
  }
}
