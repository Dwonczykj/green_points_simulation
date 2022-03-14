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
  }) : super(key: key);

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
    final autoRouter = AutoRouter.of(context);

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
      children: <Widget>[
        SizedBox(
          height: 24,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              const Text('Aggregation'),
              DropdownButton(
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
                onChanged: (ViewAggregationType? value) {
                  appStateMgr.updateAggregationType(
                      value ?? ViewAggregationType.runningAverage);
                },
              )
            ],
          ),
        ),
        const SizedBox(
          height: 8.0,
        ),
        SizedBox(
          height: 24,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              const Text('Performance measure'),
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
        ),
        Container(
          alignment: Alignment.center,
          child: ListView.builder(
            itemBuilder: (context, index) {
              var configOpt = configOptions.entries.toList()[index];
              return SizedBox(
                  height: 24,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.start,
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      NumberInput(
                        label: configOpt.key,
                        value: configOpt.value.toString(),
                        allowDecimal: false,
                        disabled: appStateMgr.runningSimulation,
                        onChanged: (num val) {
                          // marketStateViewer.loadEntitiesAndInitApp(
                          //     configOptions: configOptionsDTO);
                          appStateMgr.updateNextSimConfig(
                              configOptions: configOptionsDTO);
                        },
                      )
                    ],
                  ));
            },
            itemCount: ConfigOptions.count,
          ),
        )
      ],
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
