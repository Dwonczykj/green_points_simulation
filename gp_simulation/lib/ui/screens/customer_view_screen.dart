import 'dart:async';
import 'dart:math' as math;
import 'dart:ui';

import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:provider/provider.dart';
import 'package:quiver/iterables.dart';
import 'package:tuple/tuple.dart';
import 'package:charts_flutter/flutter.dart' as charts;

import '../components/components.dart';
import '../model/models.dart';
import 'package:webtemplate/ui/network/network.dart';
import 'package:webtemplate/utils/indexed_iterable.dart';

import 'i_page_wrapper.dart';

class CustomerViewScreenPage extends StatelessWidget {
  const CustomerViewScreenPage({Key? key}) : super(key: key);
  static const title = 'Green point flow simulation';

  @override
  Widget build(BuildContext context) {
    return IPageWrapper(
        title: title,
        childGetter: (marketStateViewer, snapshot) => snapshot.hasData &&
                snapshot.data!.customers.isNotEmpty &&
                snapshot.data!.retailers.isNotEmpty
            ? CustomersView(
                marketStateViewer: marketStateViewer,
                customers: snapshot.data!.customers,
                retailers: snapshot.data!.retailers,
                retailersCluster: snapshot.data!.retailersCluster,
              )
            : const Placeholder());
  }
}

class CustomersView extends StatefulWidget {
  const CustomersView({
    Key? key,
    required this.customers,
    required this.retailers,
    required this.retailersCluster,
    required this.marketStateViewer,
  }) : super(key: key);

  final List<CustomerModel> customers;
  final List<RetailerModel> retailers;
  final AggregatedRetailers retailersCluster;
  final IMarketStateViewer marketStateViewer;

  int get numCustomers => customers.length;
  int get numRetailers => retailers.length;

  @override
  _CustomersViewState createState() => _CustomersViewState();
}

class _CustomersViewState extends State<CustomersView>
    with SpiderLayoutMixin, SingleTickerProviderStateMixin {
  late AnimationController _controller;
  // late List<Tuple2<double, double>> _consumerPositions;

  bool showDots = false, showPath = true;

  double customerRadiusPcnt = 0.15;
  double retailerRadiusPcnt = 0.15;

  int numCustomers = 1;

  int _index = 0;

  TransactionModel? _transactionLatest;
  TransitionJourney? _transactionJourney;

  final List<Tuple2<TransactionModel, TransitionJourney>>
      _transactionsLatestList = <Tuple2<TransactionModel, TransitionJourney>>[];

  StreamSubscription<TransactionModel>? _subscription;

  final maxAnimationDurationSecs = 3.0;

  int _totalTransactions = 0;

  late Map<String, Alignment> _alignmentMap;

  int _selectedIndex = 0;

  bool retailerClusterExpanded = false;

  @override
  void initState() {
    super.initState();
    numCustomers = widget.numCustomers;
    _updateAlignmentMap();
    registerTransactionNotifactions();
  }

  void _updateAlignmentMap() {
    _alignmentMap = Map<String, Alignment>.fromEntries(widget.customers
        .mapIndexed((e, i) => AlignedEntity(
            entity: e,
            alignment: getPointAlignment(
                i, widget.customers.length, customerRadiusPcnt)))
        .map(
          (alignedEntity) => MapEntry<String, Alignment>(
              alignedEntity.entity.id, alignedEntity.alignment),
        ))
      ..addAll(
          <String, Alignment>{"RETAILER_CLUSTER": const Alignment(0.0, 0.0)})
      ..addAll(Map<String, Alignment>.fromEntries(
          widget.retailers.mapIndexed((e, i) {
        var alignment =
            getPointAlignment(i, widget.retailers.length, retailerRadiusPcnt);
        return AlignedEntity(
          entity: e,
          alignment: retailerClusterExpanded
              ? Alignment(alignment.x * 1.0, alignment.y * 1.0)
              : const Alignment(0, 0),
        );
      }).map(
        (alignedEntity) => MapEntry<String, Alignment>(
            alignedEntity.entity.id, alignedEntity.alignment),
      )));
  }

  void registerTransactionNotifactions() {
    _subscription = widget.marketStateViewer.onTransaction.listen(
      (TransactionModel? transaction) {
        if (transaction != null) {
          if (_alignmentMap.containsKey(transaction.accountFrom.owner.id) &&
              _alignmentMap.containsKey(transaction.accountTo.owner.id)) {
            var tj = TransitionJourney(
              start: _alignmentMap[transaction.accountFrom.owner.id]!,
              end: _alignmentMap[transaction.accountTo.owner.id]!,
            );
            _transactionsLatestList.add(Tuple2(transaction, tj));
            setState(() {
              _transactionLatest = transaction;
              _totalTransactions = _totalTransactions++;
              //TODO P1: Store a list of all the entities and there corresponding locations (Alignments in the Consumer screen) ->
              //  Use these locations to draw rather than having them locate themselves
              _transactionJourney = tj;
            });
          } else {
            print(
                'Transaction occured between entities that we did not pull from the backend.');
          }
        }
        if (_transactionLatest != null) {
          // append a money_send_widget to the tree is done in builder by checking if _transcationLatest is null
        }
      },
      onDone: () {
        print('Transaction stream closed!');
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final marketStateService = widget.marketStateViewer;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.max,
      children: <Widget>[
        Expanded(
          child: Center(
            child: Stack(fit: StackFit.expand, children: <Widget>[
              ...widget.customers
                  .mapIndexed((customer, i) => CustomerWidget(
                        customer: customer,
                        customerInd: i,
                        numCustomers: widget.customers.length,
                        consumerRadiusPcnt: customerRadiusPcnt,
                        alignment: _alignmentMap[customer.id] ??
                            const Alignment(0.0, 0.0),
                      ))
                  .toList(),
              RetailerClusterWidget(
                retailersCluster: widget.retailersCluster,
                underlyingRetailers: widget.retailers,
                filteredRetailerInd: null,
                retailerRadiusPcnt: retailerRadiusPcnt,
                customerRadiusPcnt: customerRadiusPcnt,
                onRetailerClusterExpandedStateChanged: (expanded) {
                  setState(() {
                    retailerClusterExpanded = expanded;
                  });
                  _updateAlignmentMap();
                },
                alignmentMap: _alignmentMap,
                alignmentCluster: _alignmentMap["RETAILER_CLUSTER"] ??
                    const Alignment(0.0, 0.0),
              ),
              ...(_transactionsLatestList
                  .map((e) => MoneySendAnimationWidget(
                        consumerRadiusPcnt: customerRadiusPcnt,
                        startingAlignmentForAnimation: e.item2.start,
                        endingAlignmentForAnimation: e.item2.end,
                        transaction: e,
                        durationSecs: marketStateService.purchaseDelaySeconds,
                        onAnimationCompleted: (tran) {
                          _transactionsLatestList.remove(tran);
                        },
                      ))
                  .toList()),
            ]),
          ),
        ),
        Row(children: [
          const Padding(
            padding: EdgeInsets.only(left: 24.0),
            child: Text('Transaction spacing'),
          ),
          Slider(
            value: marketStateService.purchaseDelaySeconds,
            min: 0.0,
            max: maxAnimationDurationSecs,
            onChangeEnd: (value) {
              marketStateService.updatePurchaseDelaySpeed(value);
            },
            onChanged: (double value) {
              // setState({});
            },
          ),
          const Padding(
            padding: EdgeInsets.only(left: 24.0),
            child: Text('Customer \'Stickyness\''),
          ),
          Slider(
            value: marketStateService.customerStickyness,
            min: 0.0,
            max: 3.0,
            onChangeEnd: (value) {
              marketStateService.customerStickyness = value;
            },
            onChanged: (double value) {
              // setState({});
            },
          ),
        ]),
        Center(
          child: RaisedButton(
            child: Text('Run Simulation'),
            onPressed: () {
              // marketStateService.testWsConnMemory();
              marketStateService.startIsolatedSimIteration();
            },
          ),
        ),
        StackedBalancesChart(
          chartTitle: 'Retailer Sales',
          series: widget.retailersCluster.totalSales.totalCostByCcy.keys
              .map((ccy) => charts.Series(
                    id: 'Retailer Sales [$ccy component]',
                    data: widget.retailers
                        .sortCopy((a, b) => a.name.compareTo(b.name)),
                    domainFn: (RetailerModel seriesItem, int? i) =>
                        seriesItem.name,
                    measureFn: (RetailerModel seriesItem, int? i) =>
                        seriesItem.totalSales.totalCostByCcy[ccy]?.amount,
                    colorFn: (RetailerModel seriesItem, int? i) => charts
                        .MaterialPalette
                        .blue
                        .shadeDefault, //TODO: Use theme to colour charts -> Theme.of(context).
                    // colorFn: (RetailerModel seriesItem, int? i) =>
                    //     charts.ColorUtil.fromDartColor(Colors
                    //         .grey),
                  ))
              .toList(), //TODO show strategy dict from entities
        )
      ],
    );
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }

  // Iterable<Widget> createMoneySVGAtPosition({int durationSecs = 5}) {
  //   return _points.map((point) => MoneySendAnimationWidget(
  //       consumerRadiusPcnt: consumerRadiusPcnt,
  //       alignmentForAnimation: Alignment(point.item1, point.item2)));
  // }

  // Iterable<Widget> createCustomerSVGAtPosition(List<CustomerModel> customers) {
  //   return customers.mapIndexed((customer, i) => CustomerWidget(
  //         customer: customer,
  //         customerInd: i,
  //         numCustomers: widget.customers.length,
  //         consumerRadiusPcnt: consumerRadiusPcnt,
  //       ));
  // }
}

// class SpiderPoint {
//   SpiderPoint();

//   final double startX;
//   final double startY;

//   final AlignmentGeometry alignment;
// }

// class ConsumerPainter extends CustomPainter {
//   ConsumerPainter(this.consumerRadius, this.pointPercentages,
//       {this.numConsumers = 1.0,
//       this.moneyProgress = 0.5,
//       this.showDots = true,
//       this.showPath = true});

//   final double numConsumers, moneyProgress;
//   bool showDots, showPath;

//   var myPaint = Paint()
//     ..color = Colors.purple
//     ..style = PaintingStyle.stroke
//     ..strokeWidth = 5.0;

//   final double consumerRadius;
//   final List<Tuple2<double, double>> pointPercentages;

//   @override
//   void paint(Canvas canvas, Size size) {
//     /*TODO P1: Wrap the Canvas in a stack that we can place the positioned Widgets on,
//       as we dont need to paint them, just to use teh animation builder to position them.
//       Then draw the line paths onto the canvas as poc*/
//     var path = createLinesToCentre(size);
//     PathMetrics pathMetrics = path.computeMetrics();
//     for (PathMetric pathMetric in pathMetrics) {
//       Path extractPath = pathMetric.extractPath(
//         0.0,
//         pathMetric.length * moneyProgress,
//       );
//       if (showPath) {
//         canvas.drawPath(extractPath, myPaint);
//       }
//       if (showDots) {
//         try {
//           var metric = extractPath.computeMetrics().first;
//           final offset = metric.getTangentForOffset(metric.length)!.position;
//           canvas.drawCircle(offset, 8.0, Paint());
//         } catch (e) {}
//       }
//     }
//   }

//   Path createLinesToCentre(Size size) {
//     var path = Path();
//     int n = numConsumers.toInt();

//     var points = pointPercentages;

//     points.forEach((p) {
//       // TODO P4: Refactor this logic into a private method or nested function.
//       var startPosX = ((p.item1 + consumerRadius * 0.5) * size.width);
//       var startPosY = ((p.item2 + consumerRadius * 0.5) * size.height);
//       var curPosX = (50.0 - ((p.item1 + consumerRadius * 0.5) * size.width));
//       var curPosY = (50.0 - ((p.item2 + consumerRadius * 0.5) * size.height));

//       var subPath = Path();
//       subPath.moveTo(startPosX, startPosY);
//       subPath.lineTo(curPosX, curPosY);
//       path.addPath(subPath, Offset(0, 0));
//     });

//     return path;
//   }

//   @override
//   bool shouldRepaint(ConsumerPainter oldDelegate) {
//     return numConsumers != oldDelegate.numConsumers ||
//         moneyProgress != oldDelegate.moneyProgress ||
//         showDots != oldDelegate.showDots ||
//         showPath != oldDelegate.showPath;
//   }
// }
