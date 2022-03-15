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
      return Scaffold(
          appBar: AppBar(
            backgroundColor:
                marketStateService.connectionStatus.toLowerCase() == 'connected'
                    ? Theme.of(context).bottomAppBarColor
                    : Color.fromARGB(160, 248, 64, 51),
            title: Text(widget.title),
            actions: <Widget>[
              Padding(
                padding: const EdgeInsets.only(right: 8.0),
                child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children:
                        marketStateService.connectionStatus.toLowerCase() ==
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
                    _openConfigPopup(context);
                  },
                ),
              ),
            ],
          ),
          body: appStateManager.initialised
              ? FutureBuilder<LoadEntitiesResult>(
                  future: appStateManager.loadEntitiesWithParams(
                      configOptions: appStateManager.simulationConfig!),
                  initialData: LoadEntitiesResult(
                    customers: <CustomerModel>[],
                    retailers: <RetailerModel>[],
                    retailersCluster: AggregatedRetailers.zero(),
                    // basketFullSize: 1,
                    // numShopTrips: 1,
                  ),
                  builder: (context, snapshot) {
                    if (snapshot.hasData &&
                        snapshot.data!.customers.isNotEmpty &&
                        snapshot.data!.retailers.isNotEmpty) {
                      return SafeArea(
                    child: widget.childGetter(
                        marketStateService, appStateManager, snapshot),
                      );
                    } else {
                      return ConfigDialog(fullScreen: true);
                    }
                  })
              // : Container(
              //   alignment: Alignment.center,
              //   child: const SizedBox(
              //     height: 150,
              //     width: 150,
              //     child: FlutterLogo(),
              //   )),
              : ConfigDialog(
                  fullScreen:
                      true)); //TODO: This needs to be a full page dialog to work...
    });
  }

  // var _selected = "";

  // void _displayDialog(BuildContext context) async {
  //   _selected = await showDialog(
  //     context: context,
  //     builder: (BuildContext context) {
  //       return Expanded(
  //         child: SimpleDialog(
  //           title: Text('Choose food'),
  //           children: [
  //             SimpleDialogOption(
  //               onPressed: () {
  //                 Navigator.pop(context, "Pizza");
  //               },
  //               child: const Text('Pizza'),
  //             ),
  //             SimpleDialogOption(
  //               onPressed: () {
  //                 Navigator.pop(context, "Burger");
  //               },
  //               child: const Text('Burger'),
  //             ),
  //           ],
  //           elevation: 10,
  //           //backgroundColor: Colors.green,
  //         ),
  //       );
  //     },
  //   );

  //   setState(() {
  //     _selected = _selected;
  //   });
  // }

  // Widget getFullScreenConfig(BuildContext context){
  //   return ConfigDialog(fullScreen: true);
  // }

  void _openConfigPopup(BuildContext context) {
    //https://gallery.flutter.dev/#/demo/dialog
    showDialog<String>(
      context: context,
      builder: (BuildContext context) => ConfigDialog(fullScreen: false),
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
