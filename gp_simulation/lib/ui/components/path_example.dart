import 'dart:math' as math;
import 'dart:ui';
import 'dart:ui' as UI;

import 'package:flutter/material.dart';


class PathExample extends StatelessWidget {
  const PathExample({Key? key}) : super(key: key);

  CustomPainter _drawLine(BuildContext context) {
    return LinePainter();
  }

  CustomPainter _drawDashedLine(BuildContext context) {
    return DashedLinePainter();
  }

  CustomPainter _drawCubic(BuildContext context) {
    return CubicPainter();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      child: CustomPaint(
        painter: _drawCubic(context),
      ),
    );
  }
}

class LinePainter extends CustomPainter {
  final double progress; // How far to draw line accross width of screen.

  LinePainter({this.progress = 0.5});

  Paint _paint = Paint()
    ..color = Colors.black
    ..strokeWidth = 4.0
    ..style = PaintingStyle.stroke
    ..strokeJoin = StrokeJoin.round;

  @override
  void paint(Canvas canvas, Size size) {
    var path = Path();
    path.moveTo(0, size.height / 2);
    path.lineTo(size.width * progress, size.height / 2);
    canvas.drawPath(path, _paint);
  }

  @override
  bool shouldRepaint(LinePainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}

class DashedLinePainter extends CustomPainter {
  final double progress; // How far to draw line accross width of screen.

  DashedLinePainter({this.progress = 0.5});

  Paint _paint = Paint()
    ..color = Colors.black
    ..strokeWidth = 4.0
    ..style = PaintingStyle.stroke
    ..strokeJoin = StrokeJoin.round;

  @override
  void paint(Canvas canvas, Size size) {
    var path = Path()
      ..moveTo(0, size.height / 2)
      ..lineTo(size.width * progress, size.height / 2);

    Path dashPath = Path();

    double dashWidth = 10.0;
    double dashSpace = 5.0;
    double distance = 0.0;

    for (var pathMetric in path.computeMetrics()) {
      while (distance < pathMetric.length) {
        dashPath.addPath(
          pathMetric.extractPath(distance, distance + dashWidth),
          Offset.zero,
        );
        distance += dashWidth;
        distance += dashSpace;
      }
    }
    canvas.drawPath(dashPath, _paint);
  }

  @override
  bool shouldRepaint(DashedLinePainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}

class CubicPainter extends CustomPainter {
  CubicPainter();

  Paint _paint = Paint()
    ..color = Colors.green
    ..strokeWidth = 4.0
    ..style = PaintingStyle.stroke
    ..strokeJoin = StrokeJoin.round;

  @override
  void paint(Canvas canvas, Size size) {
    Paint paint = Paint()
      ..color = Colors.red
      ..style = PaintingStyle.stroke
      ..strokeWidth = 8.0;

    Path path = Path();
    path.cubicTo(size.width / 4, 3 * size.height / 4, 3 * size.width / 4,
        size.height / 4, size.width, size.height);
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(CubicPainter oldDelegate) {
    return true;
  }
}


