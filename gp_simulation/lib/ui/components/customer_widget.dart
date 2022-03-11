import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:tuple/tuple.dart';

import '../model/models.dart';
import 'customer_detail_card.dart';
import 'show_more_popup.dart';
import 'spider_mixin_layout.dart';

class CustomerWidget extends StatefulWidget with SpiderLayoutMixin {
  CustomerWidget({
    Key? key,
    required this.customer,
    required this.customerInd,
    required this.numCustomers,
    required this.consumerRadiusPcnt,
    required this.alignment,
  }) : super(key: key);

  final CustomerModel customer;
  final int customerInd;
  final int numCustomers;
  final double consumerRadiusPcnt;
  final AlignmentGeometry alignment;

  // Tuple2<double, double> get point =>
  //     getPointPercentage(customerInd, numCustomers, consumerRadiusPcnt);
  // Alignment get alignment => getPointAlignment(customerInd, numCustomers, consumerRadiusPcnt);

  @override
  State<CustomerWidget> createState() => _CustomerWidgetState();
}

class _CustomerWidgetState extends State<CustomerWidget> {
  GlobalKey avgAssetRectKey = new GlobalKey(debugLabel: 'Consumer Widget');

  ShowMoreTextPopup? popup;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, constraints) {
      return Align(
          alignment: widget.alignment,
          child: Builder(builder: (context) {
            return InkWell(
              key: Key(widget.customer.name),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  SvgPicture.asset('images/noun-person-4574021.svg',
                      key: avgAssetRectKey,
                      height: widget.consumerRadiusPcnt * constraints.maxHeight,
                      width: widget.consumerRadiusPcnt * constraints.maxWidth,
                      color: Theme.of(context).iconTheme.color,
                      semanticsLabel: 'A consumer'),
                  Text(widget.customer.name,
                      style: Theme.of(context).textTheme.displaySmall),
                ],
              ),
              onTap: () {
                showConsumerDetails(customer: widget.customer);
              },
              // onHover: (isOver) {
              //   if (isOver) {
              //     if (popup == null || popup!.isVisible == false) {
              //       showConsumerDetails(customer: widget.customer);
              //     } else {
              //       ScaffoldMessenger.of(context).showSnackBar(SnackBar(
              //           content: Text("Hover already open!"),
              //           duration: Duration(milliseconds: 1000)));
              //     }
              //   } else {
              //     // popup?.dismiss();
              //     // popup = null;
              //     ScaffoldMessenger.of(context).showSnackBar(SnackBar(
              //         content: Text("Not Hovered!"),
              //         duration: Duration(milliseconds: 100)));
              //   }
              // },
            );
          }));
    });
  }

  void showConsumerDetails({required CustomerModel customer}) {
    popup = ShowMoreTextPopup(context,
        text: customer.name,
        child: CustomerDetailCard(
          customer: customer,
        ),
        textStyle: TextStyle(color: Colors.black),
        height: 100,
        width: 300,
        backgroundColor: Color.fromARGB(179, 74, 90, 90),
        padding: EdgeInsets.all(4.0),
        borderRadius: BorderRadius.circular(10.0), onDismiss: () {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text("Dismiss callback!")));
    });

    /// show the popup for specific widget
    popup!.show(
      widgetKey: avgAssetRectKey,
    );
  }
}
