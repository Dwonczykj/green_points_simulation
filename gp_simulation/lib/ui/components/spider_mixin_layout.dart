import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:tuple/tuple.dart';

abstract class SpiderLayoutMixin {
  // This class is intended to be used as a mixin, and should not be
  // extended directly.
  // factory SpiderLayoutMixin._() => null;

  double _getStartPos(double posPcnt, double consumerRadiusPcnt) {
    return (((posPcnt +
                (consumerRadiusPcnt *
                    0.5)) // Add Half width of consumer icon to take us from 0.0 to centre of consumer as start for the cash animation.
            *
            2.0 -
        1.0));
  }

  double _getCurPos(double posPcnt, double consumerRadiusPcnt) {
    return (((posPcnt +
                (consumerRadiusPcnt *
                    0.5)) // Add Half width of consumer icon to take us from 0.0 to centre of consumer as start for the cash animation.
            *
            2.0 -
        1.0));
  }

  Tuple2<double, double> getPointPercentage(
      int pointNumber, int numberOfPoints, double consumerRadiusPcnt) {
    var marginInPcnt = math.min(
        1,
        math.max(0,
            consumerRadiusPcnt)); //TODO P2: Confirm that we are happy to get %margin from width
    numberOfPoints = math.max(1, numberOfPoints);
    double divisor = numberOfPoints.toDouble() / 2.0;
    double X = pointNumber.toDouble() / divisor;
    X *= 4.0; // 1 in [0,4]
    X = math.min(8, math.max(0, X));
    X = (X + 2) % 8; //Rotate all points 90 degrees anti clockwise

    Tuple2<double, double>? point;
    if (0.0 <= X && X < 1) {
      point = Tuple2(
          1.0 * (1.0 - marginInPcnt), (0.5 * (1.0 - marginInPcnt)) - (X * 0.5));
    } else if (X < 2) {
      X = X - 1.0;
      point = Tuple2((1.0 * (1.0 - marginInPcnt)) - (X * 0.5), 0);
    } else if (X < 3) {
      X = X - 2.0;
      point = Tuple2((0.5 * (1.0 - marginInPcnt)) - (X * 0.5), 0);
    } else if (X < 4) {
      X = X - 3.0;
      point = Tuple2(0, 0.0 + (X * 0.5));
    } else if (X < 5) {
      X = X - 4.0;
      point = Tuple2(0, (0.5 * (1.0 - marginInPcnt)) + (X * 0.5));
    } else if (X < 6) {
      X = X - 5.0;
      point = Tuple2(0.0 + (X * 0.5), 1.0 * (1.0 - marginInPcnt));
    } else if (X < 7) {
      X = X - 6.0;
      point = Tuple2(
          (0.5 * (1.0 - marginInPcnt)) + (X * 0.5), 1.0 * (1.0 - marginInPcnt));
    } else if (X <= 8) {
      X = X - 7.0;
      point = Tuple2(
          1.0 * (1.0 - marginInPcnt), (1.0 * (1.0 - marginInPcnt)) - (X * 0.5));
    } else {
      throw ArgumentError.value(X, 'Unreachable code, X in [0,8)');
    }

    return Tuple2(_getStartPos(point.item1, consumerRadiusPcnt),
        _getStartPos(point.item2, consumerRadiusPcnt));
  }

  Alignment getPointAlignment(
      int pointNumber, int numberOfPoints, double consumerRadiusPcnt) {
    var point =
        getPointPercentage(pointNumber, numberOfPoints, consumerRadiusPcnt);
    return Alignment(point.item1, point.item2);
  }

  List<Tuple2<double, double>> getPointsPercentages(
      int numberOfPoints, double consumerRadiusPcnt) {
    List<Tuple2<double, double>> points = [];
    var range = List<int>.generate(numberOfPoints, (i) => i);

    for (int i in range) {
      points.add(getPointPercentage(i, numberOfPoints, consumerRadiusPcnt));
    }
    return points;
  }
}
