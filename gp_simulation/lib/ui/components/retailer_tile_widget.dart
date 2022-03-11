import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'dart:math' as math;

import '../model/models.dart';
import 'retailer_detail_card.dart';
import 'show_more_popup.dart';

class RetailerTileWidget extends StatefulWidget {
  const RetailerTileWidget({
    Key? key,
    required this.retailer,
    required this.boxConstraints,
    this.onLongTap,
    this.onDoubleTap,
    required this.retailerRadiusPcnt,
  }) : super(key: key);
  final RetailerModel retailer;
  final BoxConstraints boxConstraints;
  final void Function()? onLongTap;
  final void Function()? onDoubleTap;
  final double retailerRadiusPcnt;
  @override
  _RetailerTileWidgetState createState() => _RetailerTileWidgetState();
}

class _RetailerTileWidgetState extends State<RetailerTileWidget> {
  final retailerGlobalKeyOfStflWidget =
      GlobalKey(); // Must be a property on a stateful widget and uses the state to define its global ID.
  ShowMoreTextPopup? popup;
  @override
  Widget build(BuildContext context) {
    return InkWell(
      key: Key(widget.retailer.id),
      child: SvgPicture.asset('images/noun-buildings-4201535.svg',
          key: retailerGlobalKeyOfStflWidget,
          height: widget.retailerRadiusPcnt * widget.boxConstraints.maxHeight,
          width: widget.retailerRadiusPcnt * widget.boxConstraints.maxWidth,
          color: Theme.of(context).iconTheme.color,
          semanticsLabel: 'Retailer: ${widget.retailer.name}'),
      onTap: () {
        showUnderlyingEntityDetails(
          retailer: widget.retailer,
          key: retailerGlobalKeyOfStflWidget,
        );
      },
      onLongPress: () {
        if (widget.onLongTap != null) {
          widget.onLongTap!();
        }
      },
      onDoubleTap: () {
        if (widget.onDoubleTap != null) {
          widget.onDoubleTap!();
        } else if (widget.onLongTap != null) {
          widget.onLongTap!();
        }
      },
      // onHover: (isOver) {
      //   if (isOver) {
      //     if (popup == null || popup!.isVisible == false) {
      //       showEntityDetails(
      //           retailersCluster: widget.retailersCluster);
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
  }

  void showUnderlyingEntityDetails(
      {required RetailerModel retailer, required GlobalKey key}) {
    popup = ShowMoreTextPopup(context,
        text: retailer.name,
        child: RetailerDetailCard(
          retailer: retailer,
        ), //TODO P2 Replace this with a card that allows us to show Retailer info and tweak the params.
        textStyle: Theme.of(context).textTheme.labelMedium,
        height: 100,
        width: 300,
        backgroundColor: Theme.of(context).cardColor,
        padding: EdgeInsets.all(4.0),
        borderRadius: BorderRadius.circular(10.0), onDismiss: () {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text("Dismiss callback!")));
    });

    /// show the popup for specific widget
    popup!.show(
      widgetKey: key,
    );
  }
}
