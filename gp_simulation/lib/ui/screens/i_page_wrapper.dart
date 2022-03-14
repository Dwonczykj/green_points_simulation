import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webtemplate/ui/components/components.dart';
import 'package:webtemplate/ui/model/models.dart';

import '../model/all_models.dart';
import '../network/network.dart';

// import 'package:webtemplate/ui/components/retailer_consumer_spider.dart';

class IPageWrapper extends StatefulWidget {
  const IPageWrapper({Key? key, required this.title, required this.childGetter})
      : super(key: key);

  final String title;
  final Widget Function(
      IMarketStateViewer marketStateViewer,
      AppStateManager appStateManager,
      AsyncSnapshot<LoadEntitiesResult> snapshot) childGetter;

  @override
  State<IPageWrapper> createState() => _IPageWrapperState();
}

class _IPageWrapperState extends State<IPageWrapper> {
  

  @override
  Widget build(BuildContext context) {
    final appStateManager = Provider.of<AppStateManager>(context, listen: true);
    return Consumer<IMarketStateViewer>(
        builder: (context, marketStateService, child) {
      return FutureBuilder<LoadEntitiesResult>(
          future: marketStateService.loadEntitiesAndInitApp(),
          initialData: LoadEntitiesResult(
            customers: <CustomerModel>[],
            retailers: <RetailerModel>[],
            retailersCluster: AggregatedRetailers.zero(),
            basketFullSize: 1,
            numShopTrips: 1,
          ),
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
                      ),
                      Padding(
                        padding: const EdgeInsets.only(right: 8.0),
                        child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: marketStateService.httpCallInProgress
                                ? [
                                    CircularProgressIndicator(
                                        color: Theme.of(context).primaryColor),
                                    // Icon(Icons.cloud_done, size: 25),
                                    // Text(marketStateService.connectionStatus),
                                  ]
                                : [
                                    Icon(Icons.cloud_done, size: 25),
                                    // Text(marketStateService.connectionStatus),
                                  ]),
                      ),
                      Padding(
                        padding: const EdgeInsets.only(right: 8.0),
                        //https://www.fluttercampus.com/guide/223/popup-menu-on-flutter-appbar/
                        child: IconButton(
                          icon: Icon(Icons.settings),
                          color: Colors.grey,
                          iconSize: 25,
                          onPressed: () {
                            _openConfigPopup();
                          },
                        ),
                      ),
                    ],
                  ),
                  body: SafeArea(
                    //TODO: Wrap the child with the config popover
                    child: widget.childGetter(
                        marketStateService, appStateManager, snapshot),
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

  void _openConfigPopup() {
    //https://gallery.flutter.dev/#/demo/dialog
    showDialog<String>(
      context: context,
      builder: (BuildContext context) => ConfigDialog(),
      //   builder: (BuildContext context) => AlertDialog(
      //     title: const Text('AlertDialog Title'),
      //     content: const Text('AlertDialog description'),
      //     actions: <Widget>[
      //       TextButton(
      //         onPressed: () => Navigator.pop(context, 'Cancel'),
      //         child: const Text('Cancel'),
      //       ),
      //       TextButton(
      //         onPressed: () => Navigator.pop(context, 'OK'),
      //         child: const Text('OK'),
      //       ),
      //     ],
      //   ),
    );
  }
}
