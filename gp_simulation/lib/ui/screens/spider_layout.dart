import 'dart:math' as math;
import 'dart:ui';

import 'package:flutter/material.dart';

class SpiderLayout extends StatefulWidget {
  @override
  _SpiderLayoutState createState() => _SpiderLayoutState();
}

class _SpiderLayoutState extends State<SpiderLayout>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  double numCircles = 5.0;
  bool showDots = false, showPath = true;

  var _containerWidgetKey = GlobalKey();

  late Size _containerWidgetSize;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: Duration(seconds: 3),
    );
    _controller.value = 1.0;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Spider Layout'),
      ),
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.max,
          children: <Widget>[
            Expanded(
                child: Center(
              child: Container(
                  key: _containerWidgetKey,
                  decoration:
                      BoxDecoration(border: Border.all(color: Colors.red)),
                  child: LayoutBuilder(builder: (context, constraints) {
                    return Positioned(
                      top: 0,
                      left: 0.0,
                      child: Text(
                          'Width: ${constraints.minWidth}, Height: ${constraints.minHeight}'),
                    );
                  })),
            )),
          ],
        ),
      ),
    );
  }
}
