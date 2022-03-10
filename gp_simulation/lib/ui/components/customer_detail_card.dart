import 'package:flutter/material.dart';
import '../model/models.dart';

class CustomerDetailCard extends StatelessWidget {
  const CustomerDetailCard({Key? key, required this.customer})
      : super(key: key);

  final CustomerModel customer;

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
                  customer.name,
                  style: Theme.of(context).textTheme.headline3,
                ),
              ),
              const SizedBox(
                height: 8.0,
              ),
              Padding(
                padding: const EdgeInsets.only(left: 8.0),
                child: Text(
                  customer.bank.name,
                  style: Theme.of(context).textTheme.headline4,
                ),
              ),
            ]));
  }
}
