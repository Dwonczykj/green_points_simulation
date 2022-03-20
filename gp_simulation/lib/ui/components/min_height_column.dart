import 'dart:html';

import 'package:flutter/material.dart';

class MinHeightColumn extends Column {
  // To change column to Flex, just add a direction parameter, add to the super and check the constraints that we built below.
  MinHeightColumn({
    Key? key,
    MainAxisAlignment mainAxisAlignment = MainAxisAlignment.start,
    MainAxisSize mainAxisSize = MainAxisSize.max,
    CrossAxisAlignment crossAxisAlignment = CrossAxisAlignment.center,
    TextDirection? textDirection,
    VerticalDirection verticalDirection = VerticalDirection.down,
    TextBaseline? textBaseline,
    required List<Widget> childrenWithHeightSetForMinHeight,
  }) : super(
            key: key,
            mainAxisAlignment: mainAxisAlignment,
            mainAxisSize: mainAxisSize,
            crossAxisAlignment: crossAxisAlignment,
            textDirection: textDirection,
            verticalDirection: verticalDirection,
            textBaseline: textBaseline,
            children: childrenWithHeightSetForMinHeight);
  // final List<Widget> childrenWithHeightSetForMinHeight;
  @override
  Widget build(BuildContext context) {
    return DefaultTextStyle(
      style: Theme.of(context).textTheme.bodyText2!,
      child: LayoutBuilder(
        builder: (BuildContext context, BoxConstraints viewportConstraints) {
          return SingleChildScrollView(
            child: ConstrainedBox(
              constraints: BoxConstraints(
                minHeight: viewportConstraints.maxHeight,
              ),
              child: IntrinsicHeight(
                child: Column(
                  key: key,
                  children: children,
                  crossAxisAlignment: crossAxisAlignment,
                  mainAxisAlignment: mainAxisAlignment,
                  mainAxisSize: mainAxisSize,
                  textBaseline: textBaseline,
                  textDirection: textDirection,
                  verticalDirection: verticalDirection,
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
