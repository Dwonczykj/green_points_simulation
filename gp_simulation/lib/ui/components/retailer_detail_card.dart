import 'package:flutter/material.dart';
import 'package:webtemplate/ui/model/all_models.dart';

import '../../utils/number_formatting.dart';

class RetailerDetailCard extends StatelessWidget {
  const RetailerDetailCard({
    Key? key,
    required this.retailer,
  }) : super(key: key);

  final RetailerModel retailer;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              retailer.name,
              style: Theme.of(context).textTheme.titleMedium,
            )
          ],
        ),
        SizedBox(
          height: 12.0,
        ),
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Sales Vol.:',
              style: Theme.of(context).textTheme.labelMedium,
            ),
            Text(
              '${retailer.totalSales.numItemsIssued}',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
        SizedBox(
          height: 12.0,
        ),
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Sales Profit:',
              style: Theme.of(context).textTheme.labelMedium,
            ),
            Text(
              retailer.totalSales.totalCostByCcy.entries
                  .map((mapEntry) =>
                      CurrencyNumberFormat(mapEntry.key).format(mapEntry.value))
                  .join(', '),
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
        SizedBox(
          height: 12.0,
        ),
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'GP Issued:',
              style: Theme.of(context).textTheme.labelMedium,
            ),
            Text(
              '${retailer.totalSales.totalGPIssued}',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
        SizedBox(
          height: 12.0,
        ),
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Balance:',
              style: Theme.of(context).textTheme.labelMedium,
            ),
            Text(
              retailer.balance.moneyBalance.toString(),
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
        SizedBox(
          height: 12.0,
        ),
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Strategy:',
              style: Theme.of(context).textTheme.labelMedium,
            ),
            Text(
              RetailerStrategy.getLabel(retailer.strategy),
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
        SizedBox(
          height: 12.0,
        ),
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Sustainability rating:',
              style: Theme.of(context).textTheme.labelMedium,
            ),
            Text(
              RetailerSustainability.getLabel(retailer.sustainability),
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
        SizedBox(
          height: 12.0,
        ),
      ]),
    );
  }
}
