import 'package:flutter/material.dart';
import 'package:webtemplate/ui/network/network.dart';
import 'package:webtemplate/utils/number_formatting.dart';

import '../model/models.dart';

class RetailerClusterDetailCard extends StatelessWidget {
  const RetailerClusterDetailCard({Key? key, required this.retailerCluster})
      : super(key: key);

  final AggregatedRetailers retailerCluster;

  @override
  Widget build(BuildContext context) {
    return Card(
        elevation: 4.0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(6.0),
        ),
        child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Padding(
                padding: const EdgeInsets.only(left: 8.0),
                child: Text(
                  retailerCluster.combinedNames,
                  style: Theme.of(context).textTheme.headline3,
                ),
              ),
              const SizedBox(
                height: 8.0,
              ),
              Padding(
                padding: const EdgeInsets.only(left: 8.0),
                child: Text(
                  'Balance: ' +
                      CurrencyNumberFormat(
                              retailerCluster.balanceMoney.currency,
                              "#,##0.00",
                              "en_US")
                          .format(retailerCluster.balanceMoney.amount),
                  style: Theme.of(context).textTheme.headline4,
                ),
              ),
            ]));
  }
}
