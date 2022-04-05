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

class ConfigAppDialog extends StatefulWidget {
  ConfigAppDialog({
    Key? key,
    required this.fullScreen,
  }) : super(key: key);

  bool fullScreen;

  @override
  State<ConfigAppDialog> createState() => _ConfigAppDialogState();
}

class _ConfigAppDialogState extends State<ConfigAppDialog> {
  // String _controlRetailerName = '';
  // double _strategy = RetailerStrategy.COMPETITIVE;
  // double _sustainabilityBaseline = RetailerSustainability.AVERAGE;
  int _maxN = 5;
  double _convergenceTH = 0.0;
  int _numCustomers = 4;
  int _fullBasketSize = 2;
  int _numTripsToShops = 3;

  GemberAppConfig get configOptionsDTO => GemberAppConfig(
        BASKET_FULL_SIZE: _fullBasketSize,
        NUM_SHOP_TRIPS_PER_ITERATION: _numTripsToShops,
        NUM_CUSTOMERS: _numCustomers,
        maxN: _maxN,
        convergenceTH: _convergenceTH,
      );

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
      // _controlRetailerName =
      //     appStateMgr.controlRetailer ?? _controlRetailerName;
      // _strategy = appStateMgr.retailerStrategy;
      // _sustainabilityBaseline = appStateMgr.retailerSustainability;
      _maxN = appStateMgr.maxN;
      _convergenceTH = appStateMgr.convergenceThreshold;
      _numCustomers = appStateMgr.numCustomersForNextSim;
      _fullBasketSize = appStateMgr.basketSizeForNextSim;
      _numTripsToShops = appStateMgr.numTripsToShopsForNextSim;
    });

    return widget.fullScreen
        ? getFullScreen(context, appStateMgr, autoRouter, onClose: () {
            appStateMgr
                .loadEntitiesWithParams(configOptions: configOptionsDTO)
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
                  .loadEntitiesWithParams(configOptions: configOptionsDTO)
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
          .mapIndexed((e, i) => MapEntry(e, '$i')))
    };
    return <Widget>[
      // if ((router.current.parent?.name ?? '').contains('CustomerViewRouter'))
      // ConfigDialogDrowdown(
      //   appStateMgr: appStateMgr,
      //   label: 'Aggregation',
      //   value: appStateMgr.viewAggType,
      //   onChanged: (ViewAggregationType? value) {
      //     appStateMgr.updateAggregationType(
      //         value ?? ViewAggregationType.runningAverage);
      //   },
      //   labelsToValuesMap: Map<String, ViewAggregationType>.fromEntries(
      //       ViewAggregationType.values
      //           .map((v) => MapEntry(getAggregationUILabel(v), v))),
      // ),
      // // if ((router.current.parent?.name ?? '').contains('CustomerViewRouter'))
      // ConfigDialogDrowdown(
      //   appStateMgr: appStateMgr,
      //   label: 'Performance measure',
      //   value: appStateMgr.viewMeasType,
      //   onChanged: (ViewMeasureType? value) {
      //     appStateMgr.updateMeasureType(value ?? ViewMeasureType.sales_count);
      //   },
      //   labelsToValuesMap: Map<String, ViewMeasureType>.fromEntries(
      //       ViewMeasureType.values
      //           .map((v) => MapEntry(getMeasureUILabel(v), v))),
      // ),
      // ConfigDialogDrowdown<String>(
      //     appStateMgr: appStateMgr,
      //     label: 'Demonstrative Retailer',
      //     value: _controlRetailerName,
      //     hint: Text('*', style: Theme.of(context).textTheme.bodySmall),
      //     onChanged: (String? value) {
      //       setState(() {
      //         _controlRetailerName = value ?? '';
      //       });

      //       appStateMgr.updateNextSimConfig(
      //           controlRetailerName: _retailerNamesToInd.entries
      //               .firstWhere((element) => element.value == value)
      //               .key);
      //     },
      //     labelsToValuesMap: _retailerNamesToInd),
      // const Divider(),
      ConstrainedBox(
        constraints: BoxConstraints(maxWidth: 200),
        child: NumberInput(
          label: ConfigOptionsLabels.maxN,
          value: '$_maxN',
          allowDecimal: false,
          disabled: appStateMgr.runningSimulation,
          onChanged: (dynamic val) {
            setState(() {
              _maxN = val;
            });

            appStateMgr.updateNextSimConfig(maximumNIterations: val);
          },
        ),
      ),

      ConstrainedBox(
        constraints: BoxConstraints(maxWidth: 200),
        child: NumberInput(
          label: ConfigOptionsLabels.convergenceTH,
          value: '$_convergenceTH',
          allowDecimal: false, //TODO: Make true
          disabled: appStateMgr.runningSimulation,
          onChanged: (dynamic val) {
            setState(() {
              _convergenceTH = val;
            });

            appStateMgr.updateNextSimConfig(convergenceTH: val);
          },
        ),
      ),
      ConstrainedBox(
        constraints: BoxConstraints(maxWidth: 200),
        child: NumberInput(
          label: ConfigOptionsLabels.numCustomers,
          value: '$_numCustomers',
          allowDecimal: false,
          disabled: appStateMgr.runningSimulation,
          onChanged: (dynamic val) {
            setState(() {
              _numCustomers = val;
            });

            appStateMgr.updateNextSimConfig(numCustomers: val);
          },
        ),
      ),
      ConstrainedBox(
        constraints: BoxConstraints(maxWidth: 200),
        child: NumberInput(
          label: ConfigOptionsLabels.fullBasketSize,
          value: '$_fullBasketSize',
          allowDecimal: false,
          disabled: appStateMgr.runningSimulation,
          onChanged: (dynamic val) {
            setState(() {
              _fullBasketSize = val;
            });

            appStateMgr.updateNextSimConfig(basketFullSize: val);
          },
        ),
      ),
      ConstrainedBox(
        constraints: BoxConstraints(maxWidth: 200),
        child: NumberInput(
          label: ConfigOptionsLabels.numTripsToShops,
          value: '$_numTripsToShops',
          allowDecimal: false,
          disabled: appStateMgr.runningSimulation,
          onChanged: (dynamic val) {
            setState(() {
              _numTripsToShops = val;
            });

            appStateMgr.updateNextSimConfig(numTripsPerIteration: val);
          },
        ),
      ),
      // const Divider(),
      // ConfigDialogDrowdown(
      //   appStateMgr: appStateMgr,
      //   label: ConfigOptionsLabels.strategy,
      //   value: _strategy,
      //   onChanged: (double? val) {
      //     val ??= RetailerStrategy.COMPETITIVE;
      //     setState(() {
      //       _strategy = val!;
      //     });
      //     appStateMgr.updateNextSimConfig(strategy: val);
      //   },
      //   labelsToValuesMap: RetailerStrategy.values,
      // ),
      // ConfigDialogDrowdown(
      //   appStateMgr: appStateMgr,
      //   label: ConfigOptionsLabels.sustainabilityBaseline,
      //   value: _sustainabilityBaseline,
      //   onChanged: (double? val) {
      //     val ??= RetailerSustainability.AVERAGE;
      //     setState(() {
      //       _sustainabilityBaseline = val!;
      //     });
      //     appStateMgr.updateNextSimConfig(sustainabilityBaseline: val);
      //   },
      //   labelsToValuesMap: RetailerSustainability.values,
      // ),
    ];
  }

  Widget getFullScreen(
      BuildContext context, AppStateManager appStateMgr, StackRouter router,
      {required void Function() onClose}) {
    return Center(
        child: Container(
      padding: EdgeInsets.all(24.0),
      width: 300,
      child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
        ...getDialogChildren(context, appStateMgr, router, onClose: onClose),
        const SizedBox(
          height: 24.0,
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
      ]),
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
        children: [
          ...getDialogChildren(context, appStateMgr, router, onClose: onClose),
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
        ]);
  }
}

// SingleChildScrollView(
//           child: ListBody(
//             children: const <Widget>[
//               Text('This is a demo alert dialog.'),
//               Text('Would you like to approve of this message?'),
//             ],
//           ),
//         ),


