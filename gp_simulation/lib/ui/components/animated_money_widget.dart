import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:tuple/tuple.dart';

class AnimatedMoneyCotainer extends StatefulWidget {
  AnimatedMoneyCotainer(
      {Key? key,
      required this.index,
      required this.point,
      required double consumerRadiusPcnt,
      required int numConsumers})
      : consumerRadiusPcnt = math.min(1.0, math.max(0.0, consumerRadiusPcnt)),
        numConsumers = math.max(0, numConsumers),
        super(key: key);

  final Tuple2<double, double> point;
  final int index;
  double consumerRadiusPcnt;
  int numConsumers;

  @override
  _AnimatedMoneyCotainerState createState() => _AnimatedMoneyCotainerState();
}

class _AnimatedMoneyCotainerState extends State<AnimatedMoneyCotainer> {
  late List<Tuple2<double, double>> _points;
  int _index = 0;
  List<Alignment> _alignments = [];

  @override
  void initState() {
    super.initState();
    _index = widget.index;
    var p1 = Tuple2(
        _getStartPos(widget.point.item1, widget.consumerRadiusPcnt),
        _getStartPos(widget.point.item2, widget.consumerRadiusPcnt));
    var p2 =
        Tuple2(_getCurPos(widget.point.item1, widget.consumerRadiusPcnt),
        _getCurPos(widget.point.item2, widget.consumerRadiusPcnt));
    _alignments = [
      Alignment(p1.item1, p1.item2),
      Alignment(p2.item1, p2.item2)
    ];
  }

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

  @override
  Widget build(BuildContext context) {
    return AnimatedMoney(
        consumerRadiusPcnt: widget.consumerRadiusPcnt,
        alignment: _alignments[widget.index % _alignments.length]);
  }
}

class AnimatedMoney extends StatelessWidget {
  const AnimatedMoney(
      {Key? key, required this.consumerRadiusPcnt, required this.alignment})
      : super(key: key);

  final double consumerRadiusPcnt;
  final AlignmentGeometry alignment;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, constraints) {
      // var p1 = Tuple2(
      //     _getStartPos(widget.point.item1), _getCurPos(widget.point.item2));
      // var p2 = Tuple2(
      //     _getCurPos(widget.point.item1), _getCurPos(widget.point.item2));
      // var _alignments = [
      //   Alignment(p1.item1, p1.item2),
      //   Alignment(p2.item1, p2.item2)
      // ];
      // TODO: Workout how to update the state on this...
      return AnimatedAlign(
        alignment:
            alignment, //if this changes, animation will occur on paint to update.
        duration: Duration(seconds: 6),
        curve: Curves.fastOutSlowIn,
        child: SizedBox(
            width: 40.0,
            height: 40.0,
            child: SvgPicture.asset('images/noun-money-4563489.svg',
                height: consumerRadiusPcnt * constraints.maxHeight,
                width: consumerRadiusPcnt * constraints.maxWidth,
                color: Color.fromARGB(255, 14, 109, 61),
                semanticsLabel: 'A £ Note')),
      );
    });
  }
}
