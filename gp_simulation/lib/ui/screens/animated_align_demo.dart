import 'package:flutter/material.dart';
import 'dart:math' as math;

import 'package:flutter/painting.dart';

class AnimatedAlignDemo extends StatefulWidget {
  @override
  _AnimatedAlignDemoState createState() => _AnimatedAlignDemoState();
}

class _AnimatedAlignDemoState extends State<AnimatedAlignDemo> {
  static const _alignments = [
    // Alignment.topLeft,
    Alignment.topRight,
    Alignment.bottomLeft,
    //   Alignment.bottomRight,
  ];

  var _index = 0;

  AlignmentGeometry get _alignment => _alignments[_index % _alignments.length];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        elevation: 0.0,
        backgroundColor: Colors.white,
        title: Text(
          'Animated Align',
          style: TextStyle(
            color: Colors.black,
          ),
        ),
        centerTitle: true,
      ),
      body: Container(
        padding: EdgeInsets.all(15),
        child: Stack(
          alignment: Alignment.bottomCenter,
          children: <Widget>[
            AnimatedAlignDemoAligner(alignment: _alignment),
            ButtonTheme(
              minWidth: 100,
              height: 50,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(30),
              ),
              child: RaisedButton(
                color: Colors.purple.withOpacity(0.6),
                onPressed: () {
                  setState(() {
                    _index++; //NOTE: Thie changes the value of the _alignment getter which tells the widget to animate itself.
                  });
                },
                child: Text(
                  'Click Me',
                  style: TextStyle(
                      fontFamily: 'Roboto Medium',
                      fontSize: 15.0,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.3,
                      color: Colors.white),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class AnimatedAlignDemoAligner extends StatelessWidget {
  const AnimatedAlignDemoAligner({
    Key? key,
    required AlignmentGeometry alignment,
  })  : _alignment = alignment,
        super(key: key);

  final AlignmentGeometry _alignment;

  @override
  Widget build(BuildContext context) {
    return AnimatedAlign(
      alignment: _alignment,
      duration: Duration(seconds: 6),
      curve: Curves.easeInOutBack,
      child: SizedBox(
          width: 100.0,
          height: 100.0,
          child: Image.asset(
            'images/pluginIcon.png',
            height: 40,
          )),
    );
  }
}
