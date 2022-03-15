import 'dart:html';

import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
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

  static const labels = <String, String>{
    ConfigOptions.fullBasketSize: 'full basket size',
    ConfigOptions.numTripsToShops: '# trips to shops',
    ConfigOptions.numCustomers: '# customers',
    ConfigOptions.maxN: 'max # iterations',
    ConfigOptions.convergenceTH: 'condition for convergence of sim',
  };

  static int get count => labels.length;

  static String getLabel(String option) => labels[option]!;
}

class ConfigDialog extends StatelessWidget {
  ConfigDialog({
    Key? key,
    required this.fullScreen,
  }) : super(key: key);

  bool fullScreen;

  Map<String, num> configOptions = <String, num>{
    ConfigOptions.getLabel(ConfigOptions.fullBasketSize): 2,
    ConfigOptions.getLabel(ConfigOptions.numTripsToShops): 3,
    ConfigOptions.getLabel(ConfigOptions.numCustomers): 4,
    ConfigOptions.getLabel(ConfigOptions.maxN): 2,
    ConfigOptions.getLabel(ConfigOptions.convergenceTH): 0.0,
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
      );

  @override
  Widget build(BuildContext context) {
    final appStateMgr = Provider.of<AppStateManager>(context);
    final marketStateViewer = Provider.of<IMarketStateViewer>(context);
    // final autoRouter = AutoRouter.of(context);

    return fullScreen
        ? getFullScreen(context, appStateMgr)
        : getPopover(context, appStateMgr);
  }

  Widget getPopover(BuildContext context, AppStateManager appStateMgr) {
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
                avatar: CircleAvatar(
                  backgroundImage: NetworkImage(
                      "https://pbs.twimg.com/profile_images/1304985167476523008/QNHrwL2q_400x400.jpg"), //NetwordImage
                ), //CircleAvatar
                label: Text(
                  '',
                  style: TextStyle(fontSize: 20),
                ), //Text
              ),
            ),
          )
        ],
      ),
      children: getDialogChildren(context, appStateMgr),
    );
  }

  List<Widget> getDialogChildren(
      BuildContext context, AppStateManager appStateMgr) {
    return <Widget>[
      Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: <Widget>[
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Text(
              'Aggregation',
              style: Theme.of(context).textTheme.labelSmall,
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: DropdownButton(
              items: const [
                DropdownMenuItem(
                  child: Text(
                    'Average',
                  ),
                  value: ViewAggregationType.runningAverage,
                ),
                DropdownMenuItem(
                  child: Text(
                    'Variance',
                  ),
                  value: ViewAggregationType.runningVariance,
                ),
                DropdownMenuItem(
                  child: Text(
                    'Cum. Sum',
                  ),
                  value: ViewAggregationType.runningSum,
                ),
              ],
              // onTap: (){
              //   showItems()
              // } ,
              onChanged: (ViewAggregationType? value) {
                appStateMgr.updateAggregationType(
                    value ?? ViewAggregationType.runningAverage);
              },
            ),
          )
        ],
      ),
      Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: <Widget>[
          Text(
            'Performance measure',
            style: Theme.of(context).textTheme.labelSmall,
          ),
          DropdownButton(
            items: const [
              DropdownMenuItem(
                child: Text(
                  'Sales Vol.',
                ),
                value: ViewMeasureType.salesCount,
              ),
              DropdownMenuItem(
                child: Text(
                  'Gember Points issued',
                ),
                value: ViewMeasureType.greenPointsIssued,
              ),
            ],
            onChanged: (ViewMeasureType? value) {
              appStateMgr
                  .updateMeasureType(value ?? ViewMeasureType.salesCount);
            },
          )
        ],
      ),
      ...(configOptions.entries.map((configOpt) {
        return ConstrainedBox(
          constraints: BoxConstraints(maxWidth: 200),
          child: NumberInput(
            label: configOpt.key,
            value: '${configOpt.value}',
            allowDecimal: false,
            disabled: appStateMgr.runningSimulation,
            onChanged: (num val) {
              configOptions[configOpt.key] = val;
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
              child:
                  Text('Done', style: Theme.of(context).textTheme.labelMedium),
              onPressed: () {
                appStateMgr
                    .loadEntitiesWithParams(configOptions: configOptionsDTO)
                    .then((ents) {
                  // Navigator.of(context).pop(); // fix this with autorouter using a route if thats how it is showing?...
                  // WE are meant to push another route to the stack to show a dialog: https://api.flutter.dev/flutter/material/AlertDialog-class.html
                });
              },
            ),
          )
        ],
      )
    ];
  }

  Widget getFullScreen(BuildContext context, AppStateManager appStateMgr) {
    return Center(
        // alignment: Alignment.center,
        // // height: MediaQuery.of(context).size.height,
        // height: 400,
        // // width: MediaQuery.of(context).size.width,
        // width: 400,
        // padding: EdgeInsets.all(8.0),
        child: Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: getDialogChildren(context, appStateMgr),
      // children: getDialogChildren(context, appStateMgr),
    ));
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
