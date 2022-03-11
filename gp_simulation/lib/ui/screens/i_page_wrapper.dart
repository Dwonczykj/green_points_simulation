import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../model/models.dart';
import '../network/network.dart';

// import 'package:webtemplate/ui/components/retailer_consumer_spider.dart';

class IPageWrapper extends StatefulWidget {
  const IPageWrapper({Key? key, required this.title, required this.childGetter})
      : super(key: key);

  final String title;
  final Widget Function(IMarketStateViewer marketStateViewer,
      AsyncSnapshot<LoadEntitiesResult> snapshot) childGetter;

  @override
  State<IPageWrapper> createState() => _IPageWrapperState();
}

class _IPageWrapperState extends State<IPageWrapper> {
  int _counter = 0;

  int _selectedIndex = 1;

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<IMarketStateViewer>(
        builder: (context, marketStateService, child) {
      return FutureBuilder<LoadEntitiesResult>(
          future: marketStateService.loadEntitiesAndInitApp(),
          initialData: LoadEntitiesResult(
              customers: <CustomerModel>[],
              retailers: <RetailerModel>[],
              retailersCluster: AggregatedRetailers.zero()),
          builder: (context, snapshot) {
            if (snapshot.hasData &&
                snapshot.data!.customers.isNotEmpty &&
                snapshot.data!.retailers.isNotEmpty) {
              return widget.childGetter(marketStateService, snapshot);
            } else {
              return Container(
                  alignment: Alignment.center,
                  child: const SizedBox(
                    height: 150,
                    width: 150,
                    child: FlutterLogo(),
                  ));
            }
          });
    });
  }
}
