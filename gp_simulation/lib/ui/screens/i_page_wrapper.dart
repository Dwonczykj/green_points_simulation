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
              return Scaffold(
                  appBar: AppBar(
                    backgroundColor:
                        marketStateService.connectionStatus.toLowerCase() ==
                                'connected'
                            ? Theme.of(context).bottomAppBarColor
                            : Color.fromARGB(160, 248, 64, 51),
                    title: Text(widget.title),
                    actions: <Widget>[
                      Padding(
                        padding: const EdgeInsets.only(right: 8.0),
                        child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: marketStateService.connectionStatus
                                        .toLowerCase() ==
                                    'connected'
                                ? [
                                    Icon(Icons.wifi, size: 25),
                                    Text(marketStateService.connectionStatus),
                                  ]
                                : [
                                    Icon(Icons.wifi_off, size: 25),
                                    Text(marketStateService.connectionStatus),
                                  ]),
                      )
                    ],
                  ),
                  body: SafeArea(
                    child: widget.childGetter(marketStateService, snapshot),
                  ));
              // return widget.childGetter(marketStateService, snapshot);
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
