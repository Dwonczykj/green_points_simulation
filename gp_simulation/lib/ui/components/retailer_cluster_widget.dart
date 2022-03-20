import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:webtemplate/ui/components/components.dart';
import 'package:webtemplate/ui/components/retailer_tile_widget.dart';
import 'package:webtemplate/ui/model/all_models.dart';
import 'package:webtemplate/utils/indexed_iterable.dart';

import '../network/network.dart';
import 'retailer_cluster_detail_card.dart';
import 'show_more_popup.dart';
import 'spider_mixin_layout.dart';

class RetailerClusterWidget extends StatefulWidget with SpiderLayoutMixin {
  RetailerClusterWidget({
    Key? key,
    required this.retailersCluster,
    required this.underlyingRetailers,
    required this.filteredRetailerInd,
    required this.alignmentCluster,
    required this.alignmentMap,
    required this.retailerRadiusPcnt,
    required this.customerRadiusPcnt,
    this.onRetailerClusterExpandedStateChanged,
  }) : super(key: key);

  final AggregatedRetailers retailersCluster;
  final Iterable<RetailerModel> underlyingRetailers;
  final int? filteredRetailerInd;
  final AlignmentGeometry alignmentCluster;
  final Map<String, Alignment> alignmentMap;
  final double retailerRadiusPcnt;
  final double customerRadiusPcnt;
  final void Function(bool expanded)? onRetailerClusterExpandedStateChanged;

  // Alignment get alignment => const Alignment(0.0, 0.0);

  @override
  State<RetailerClusterWidget> createState() => _RetailerClusterWidgetState();
}

class _RetailerClusterWidgetState extends State<RetailerClusterWidget> {
  final clusterWidgetKey = GlobalKey(debugLabel: 'Retailed cluster key');

  // Map<String, GlobalKey> get gkey => Map<String, GlobalKey>.fromEntries(
  //     widget.underlyingRetailers.map((retailer) => MapEntry<String, GlobalKey>(
  //         retailer.id, GlobalKey(debugLabel: '${retailer.name} global key'))));

  ShowMoreTextPopup? popup;

  bool expanded = false;

  void _performDataSanityCheck(BuildContext context) {
    var checkRetailerIdsInAlignmentMap = widget.underlyingRetailers
        .map((underlyingRetailer) =>
            widget.alignmentMap.keys.contains(underlyingRetailer.id))
        .any((element) => element);
    if (!checkRetailerIdsInAlignmentMap) {
      throw Exception(
          'Alignment map doesnt contain Ids to all underlying retailers.');
    }
  }

  @override
  Widget build(BuildContext context) {
    _performDataSanityCheck(context);
    return LayoutBuilder(builder: (context, constraints) {
      return Align(
          alignment: widget.alignmentCluster,
          child: Builder(builder: (context) {
            return SizedBox(
              height: math.max(
                  widget.retailerRadiusPcnt * constraints.maxHeight,
                  math.min(
                      constraints.maxHeight - (2.0 * widget.customerRadiusPcnt),
                      200)),
              width: math.max(
                  widget.retailerRadiusPcnt * constraints.maxWidth,
                  math.min(
                      constraints.maxWidth - (2.0 * widget.customerRadiusPcnt),
                      200)),
              child: Stack(
                children: widget.underlyingRetailers
                    .take(5)
                    .mapIndexed(
                      (retailer, i) => AnimatedAlign(
                        duration: const Duration(seconds: 1),
                        alignment: expanded
                            ? widget.alignmentMap[retailer.id]!
                            : widget.alignmentMap[
                                retailer.id]!, //const Alignment(0, 0),
                        curve: Curves.decelerate,
                        child: RetailerTileWidget(
                          retailer: retailer,
                          displayLabel: expanded,
                          boxConstraints: constraints,
                          retailerRadiusPcnt: widget.retailerRadiusPcnt,
                          onLongTap: () {
                            setState(() {
                              final newState = !expanded;
                              if (widget
                                      .onRetailerClusterExpandedStateChanged !=
                                  null) {
                                widget.onRetailerClusterExpandedStateChanged!(
                                    newState);
                              }
                              setState(() {
                                expanded = newState;
                              });
                            });
                          },
                          onDoubleTap: () {
                            final newState = !expanded;
                            if (widget.onRetailerClusterExpandedStateChanged !=
                                null) {
                              widget.onRetailerClusterExpandedStateChanged!(
                                  newState);
                            }
                            setState(() {
                              expanded = newState;
                            });
                          },
                        ),
                      ),
                    )
                    .toList(),
              ),
            );
          }));
    });
  }

  void showClusterDetails(
      {required AggregatedRetailers retailersCluster, required GlobalKey key}) {
    popup = ShowMoreTextPopup(context,
        text: retailersCluster.combinedNames,
        child: RetailerClusterDetailCard(
          retailerCluster: retailersCluster,
        ),
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
