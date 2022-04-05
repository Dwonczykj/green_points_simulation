import 'dart:html';

import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webtemplate/navigation/app_router.gr.dart';
import 'package:webtemplate/ui/components/components.dart';
import 'package:webtemplate/ui/network/network.dart';

import '../model/models.dart';
import '../screens/view_simulation.dart';
import '../../utils/indexed_iterable.dart';

class ConfigRetailerDialog extends StatefulWidget {
  ConfigRetailerDialog({
    Key? key,
    required this.fullScreen,
  }) : super(key: key);

  bool fullScreen;

  @override
  State<ConfigRetailerDialog> createState() => _ConfigRetailerDialogState();
}

class _ConfigRetailerDialogState extends State<ConfigRetailerDialog> {
  String _controlRetailerName = '';
  double _strategy = RetailerStrategy.COMPETITIVE;
  double _sustainabilityBaseline = RetailerSustainability.AVERAGE;

  GemberAppConfig configOptionsDTO(AppStateManager appStateMgr) {
    return GemberAppConfig(
      BASKET_FULL_SIZE: appStateMgr.basketSizeForNextSim,
      NUM_SHOP_TRIPS_PER_ITERATION: appStateMgr.numTripsToShopsForNextSim,
      NUM_CUSTOMERS: appStateMgr.numCustomersForNextSim,
      maxN: appStateMgr.maxN,
      convergenceTH: appStateMgr.convergenceThreshold,
      strategy: _strategy,
      sustainabilityBaseline: _sustainabilityBaseline,
      controlRetailerName: _controlRetailerName,
    );
  }

  @override
  Widget build(BuildContext context) {
    final appStateMgr = Provider.of<AppStateManager>(context, listen: true);

    // appStateMgr.updateNextSimConfigNoNotifiy(configOptions: configOptionsDTO);
    // final marketStateViewer = Provider.of<IMarketStateViewer>(context);
    final autoRouter = AutoRouter.of(context);
    // final routeBelow = autoRouter.current.parent;
    // if((routeBelow?.name ?? '').contains('CustomerViewRouter')){

    // }
    setState(() {
      _controlRetailerName =
          appStateMgr.controlRetailer ?? _controlRetailerName;
      _strategy = appStateMgr.retailerStrategy;
      _sustainabilityBaseline = appStateMgr.retailerSustainability;
    });

    return widget.fullScreen
        ? getFullScreen(context, appStateMgr, autoRouter, onClose: () {
            appStateMgr
                .loadEntitiesWithParams(
                    configOptions: configOptionsDTO(appStateMgr))
                .then((ents) {
              autoRouter.popAndPush(ViewSimulationRoute());
            });
          })
        : getPopover(
            context,
            appStateMgr,
            autoRouter,
            onClose: () {
              appStateMgr
                  .loadEntitiesWithParams(
                      configOptions: configOptionsDTO(appStateMgr))
                  .then((ents) {
                autoRouter.pop();
              });
            },
          );
  }

  List<Widget> getDialogChildren(
      BuildContext context, AppStateManager appStateMgr, StackRouter router,
      {required void Function() onClose}) {
    var _retailerNamesToInd = <String, String>{
      ...{'': ''},
      ...Map.fromEntries((appStateMgr.retailerNames ?? <String>[])
          .mapIndexed((e, i) => MapEntry(e, '$e')))
    };
    return <Widget>[
      ConfigDialogDrowdown<String>(
          appStateMgr: appStateMgr,
          label: 'Demonstrative Retailer',
          value: _controlRetailerName,
          hint: Text('*', style: Theme.of(context).textTheme.bodySmall),
          onChanged: (String? value) {
            print('setting retailer to $value');
            setState(() {
              _controlRetailerName = value ?? '';
            });

            appStateMgr.updateNextSimConfig(
                controlRetailerName: _retailerNamesToInd.entries
                    .firstWhere((element) => element.value == value)
                    .key);
          },
          labelsToValuesMap: _retailerNamesToInd),
      ConfigDialogDrowdown(
        appStateMgr: appStateMgr,
        label: ConfigOptionsLabels.strategy,
        value: _strategy,
        onChanged: (double? val) {
          val ??= RetailerStrategy.COMPETITIVE;
          setState(() {
            _strategy = val!;
          });
          appStateMgr.updateNextSimConfig(strategy: val);
        },
        labelsToValuesMap: RetailerStrategy.values,
      ),
      ConfigDialogDrowdown(
        appStateMgr: appStateMgr,
        label: ConfigOptionsLabels.sustainabilityBaseline,
        value: _sustainabilityBaseline,
        onChanged: (double? val) {
          val ??= RetailerSustainability.AVERAGE;
          setState(() {
            _sustainabilityBaseline = val!;
          });
          appStateMgr.updateNextSimConfig(sustainabilityBaseline: val);
        },
        labelsToValuesMap: RetailerSustainability.values,
      ),
      Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: ElevatedButton(
                child: Text('Done',
                    style: Theme.of(context).textTheme.labelMedium),
                onPressed: onClose),
          )
        ],
      )
    ];
  }

  Widget getFullScreen(
      BuildContext context, AppStateManager appStateMgr, StackRouter router,
      {required void Function() onClose}) {
    return Center(
        child: Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children:
          getDialogChildren(context, appStateMgr, router, onClose: onClose),
    ));
  }

  Widget getPopover(
      BuildContext context, AppStateManager appStateMgr, StackRouter router,
      {required void Function() onClose}) {
    return SimpleDialog(
      title: Stack(
        children: [
          Align(
            alignment: Alignment.center,
            child: Text('Configuration',
                style: Theme.of(context)
                    .textTheme
                    .titleSmall
                    ?.copyWith(color: Colors.red)),
          ),
          Padding(
            padding: EdgeInsets.only(right: 8.0),
            child: Tooltip(
              message: appStateMgr.runningSimulation
                  ? 'Simulation running'
                  : 'Simulation ready',
              child: Chip(
                elevation: 20,
                padding: EdgeInsets.all(8),
                backgroundColor: appStateMgr.runningSimulation
                    ? Color.fromARGB(255, 224, 118, 18)
                    : Colors.greenAccent[100],
                shadowColor: Theme.of(context).backgroundColor,
                // avatar: CircleAvatar(
                //   backgroundImage: NetworkImage(
                //       "https://www.freepik.com/premium-vector/cute-dog-head-avatar_4888042.htm"), //NetworkImage
                // ), //CircleAvatar
                label: Text(
                  '',
                  style: TextStyle(fontSize: 20),
                ), //Text
              ),
            ),
          )
        ],
      ),
      children:
          getDialogChildren(context, appStateMgr, router, onClose: onClose),
    );
  }
}
