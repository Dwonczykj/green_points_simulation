import 'dart:html';

import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webtemplate/navigation/app_router.gr.dart';
import 'package:webtemplate/ui/components/components.dart';
import 'package:webtemplate/ui/network/network.dart';

import '../model/models.dart';
import '../screens/view_simulation.dart';

abstract class ConfigOptions {
  static const String fullBasketSize = 'BASKET_FULL_SIZE';
  static const String numTripsToShops = 'NUM_SHOP_TRIPS_PER_ITERATION';
  static const String numCustomers = 'NUM_CUSTOMERS';
  static const String maxN = 'maxN';
  static const String convergenceTH = 'convergenceTH';
  static const String sustainabilityBaseline = 'sustainabilityBaseline';
  static const String strategy = 'strategy';
  // static const String controlRetailerName = 'controlRetailerName';

  static const labels = <String, String>{
    ConfigOptions.fullBasketSize: 'full basket size',
    ConfigOptions.numTripsToShops: '# trips to shops',
    ConfigOptions.numCustomers: '# customers',
    ConfigOptions.maxN: 'max # iterations',
    ConfigOptions.convergenceTH: 'condition for convergence of sim',
    ConfigOptions.strategy: 'gember points issuing generosity',
    ConfigOptions.sustainabilityBaseline:
        'sustainability rating of retailer supply chain',
    // ConfigOptions.controlRetailerName: 'demonstrative retailer',
  };

  static int get count => labels.length;

  static String getLabel(String option) => labels[option]!;
}

class ConfigDialog extends StatefulWidget {
  ConfigDialog({
    Key? key,
    required this.fullScreen,
  }) : super(key: key);

  bool fullScreen;

  @override
  State<ConfigDialog> createState() => _ConfigDialogState();
}

class _ConfigDialogState extends State<ConfigDialog> {
  String? _controlRetailerName;

  Map<String, num> configOptions = <String, num>{
    ConfigOptions.getLabel(ConfigOptions.strategy):
        RetailerStrategy.COMPETITIVE,
    ConfigOptions.getLabel(ConfigOptions.sustainabilityBaseline):
        RetailerSustainability.AVERAGE,
    ConfigOptions.getLabel(ConfigOptions.maxN): 5,
    ConfigOptions.getLabel(ConfigOptions.convergenceTH): 0.0,
    ConfigOptions.getLabel(ConfigOptions.numCustomers): 4,
    ConfigOptions.getLabel(ConfigOptions.fullBasketSize): 2,
    ConfigOptions.getLabel(ConfigOptions.numTripsToShops): 3,
    // ConfigOptions.getLabel(ConfigOptions.controlRetailerName): '',
  };

  

  GemberAppConfig get configOptionsDTO => GemberAppConfig(
        BASKET_FULL_SIZE:
            configOptions[ConfigOptions.getLabel(ConfigOptions.fullBasketSize)]!
                .toInt(),
        NUM_SHOP_TRIPS_PER_ITERATION: configOptions[
                ConfigOptions.getLabel(ConfigOptions.numTripsToShops)]!
            .toInt(),
        NUM_CUSTOMERS:
            configOptions[ConfigOptions.getLabel(ConfigOptions.numCustomers)]!
                .toInt(),
        maxN:
            configOptions[ConfigOptions.getLabel(ConfigOptions.maxN)]!.toInt(),
        convergenceTH:
            configOptions[ConfigOptions.getLabel(ConfigOptions.convergenceTH)]!
                .toDouble(),
        strategy: configOptions[ConfigOptions.getLabel(ConfigOptions.strategy)]!
            .toDouble(),
        sustainabilityBaseline: configOptions[
                ConfigOptions.getLabel(ConfigOptions.sustainabilityBaseline)]!
            .toDouble(),
        controlRetailerName: _controlRetailerName,
      );

  @override
  Widget build(BuildContext context) {
    final appStateMgr = Provider.of<AppStateManager>(context, listen: true);
    appStateMgr.updateNextSimConfigNoNotifiy(configOptions: configOptionsDTO);
    final marketStateViewer = Provider.of<IMarketStateViewer>(context);
    final autoRouter = AutoRouter.of(context);
    final routeBelow = autoRouter.current.parent;
    // if((routeBelow?.name ?? '').contains('CustomerViewRouter')){

    // }
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
    return <Widget>[
      // if ((router.current.parent?.name ?? '').contains('CustomerViewRouter'))
      ConfigDialogDrowdown(
        appStateMgr: appStateMgr,
        label: 'Aggregation',
        value: appStateMgr.viewAggType,
        onChanged: (ViewAggregationType? value) {
          appStateMgr.updateAggregationType(
              value ?? ViewAggregationType.runningAverage);
        },
        labelsToValuesMap: Map<String, ViewAggregationType>.fromEntries(
            ViewAggregationType.values
                .map((v) => MapEntry(getAggregationUILabel(v), v))),
      ),
      // if ((router.current.parent?.name ?? '').contains('CustomerViewRouter'))
      ConfigDialogDrowdown(
        appStateMgr: appStateMgr,
        label: 'Performance measure',
        value: appStateMgr.viewMeasType,
        onChanged: (ViewMeasureType? value) {
          appStateMgr.updateMeasureType(value ?? ViewMeasureType.sales_count);
        },
        labelsToValuesMap: Map<String, ViewMeasureType>.fromEntries(
            ViewMeasureType.values
                .map((v) => MapEntry(getMeasureUILabel(v), v))),
      ),
      ConfigDialogDrowdown<String>(
        appStateMgr: appStateMgr,
        label: 'Demonstrative Retailer',
        value: appStateMgr.controlRetailer ?? '',
        hint: Text('*', style: Theme.of(context).textTheme.bodySmall),
        onChanged: (String? value) {
          setState(() {
            _controlRetailerName = value;
          });
          appStateMgr.updateNextSimConfig(configOptions: configOptionsDTO);
        },
        labelsToValuesMap: <String, String>{
          ...{'': ''},
          ...Map<String, String>.fromEntries(
              appStateMgr.retailerNames?.map((v) => MapEntry(v, v)) ??
                  <MapEntry<String, String>>[])
        },
      ),
      ...(configOptions.entries.map((configOpt) {
        return ConstrainedBox(
          constraints: BoxConstraints(maxWidth: 200),
          child: NumberInput(
            label: configOpt.key,
            value: '${configOpt.value}',
            allowDecimal: false,
            disabled: appStateMgr.runningSimulation,
            onChanged: (dynamic val) {
              
              setState(() {
                configOptions[configOpt.key] = val;
              });
              
              appStateMgr.updateNextSimConfig(configOptions: configOptionsDTO);
            },
          ),
        );
      })),
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

// SingleChildScrollView(
//           child: ListBody(
//             children: const <Widget>[
//               Text('This is a demo alert dialog.'),
//               Text('Would you like to approve of this message?'),
//             ],
//           ),
//         ),

class ConfigDialogDrowdown<TVal> extends StatelessWidget {
  ConfigDialogDrowdown({
    Key? key,
    required this.appStateMgr,
    required this.label,
    required this.value,
    required this.onChanged,
    required this.labelsToValuesMap,
    this.hint,
    this.disabledHint,
  }) : super(key: key);

  final AppStateManager appStateMgr;
  final String label;
  final TVal value;
  final void Function(TVal? value) onChanged;
  final Map<String, TVal> labelsToValuesMap;
  final Widget? hint;
  final Widget? disabledHint;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: <Widget>[
        Text(
          label,
          style: Theme.of(context).textTheme.labelSmall,
        ),
        DropdownButton(
          value: value,
          hint: hint,
          disabledHint: disabledHint,
          icon: const Icon(Icons.arrow_downward),
          elevation: 16,
          style: TextStyle(
              color: Theme.of(context).buttonTheme.colorScheme?.primary ??
                  Colors.limeAccent[100]),
          underline: Container(
            height: 2,
            color: Theme.of(context).buttonTheme.colorScheme?.secondary ??
                Colors.deepPurpleAccent,
          ),
          // selectedItemBuilder: ,
          items: labelsToValuesMap.entries
              .map((entry) => DropdownMenuItem(
                    child: Text(
                      entry.key,
                    ),
                    value: entry.value,
                  ))
              .toList(),
          // onChanged: (ViewMeasureType? value) {
          //   appStateMgr
          //       .updateMeasureType(value ?? ViewMeasureType.salesCount);
          onChanged: onChanged,
        )
      ],
    );
  }
}
