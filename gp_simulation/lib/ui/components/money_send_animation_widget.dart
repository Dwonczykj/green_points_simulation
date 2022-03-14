import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:tuple/tuple.dart';

import '../model/all_models.dart';
import 'spider_mixin_layout.dart';

class MoneySendAnimationWidget extends StatelessWidget with SpiderLayoutMixin {
  MoneySendAnimationWidget(
      {Key? key,
      // required this.point1,
      // required this.point2,
      required this.consumerRadiusPcnt,
      required this.startingAlignmentForAnimation,
      required this.endingAlignmentForAnimation,
      required this.transaction,
      this.onAnimationCompleted,
      this.durationSecs = 5})
      : super(key: key);

  final double consumerRadiusPcnt;
  // final Tuple2<double, double> point1;
  // final Tuple2<double, double> point2;
  final AlignmentGeometry startingAlignmentForAnimation;
  final AlignmentGeometry endingAlignmentForAnimation;
  final Tuple2<TransactionModel, TransitionJourney> transaction;
  void Function(Tuple2<TransactionModel, TransitionJourney> a)?
      onAnimationCompleted;
  final double durationSecs;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, constraints) {
      // var p1 = point1; // Tuple2(_getStartPos(point.item1, consumerRadiusPcnt), _getStartPos(point.item2, consumerRadiusPcnt));

      // //BUG: This is currently the same point, when alignment is changed the function should be passed the new point for the money to travel to:
      // var p2 = point2; // Tuple2(_getCurPos(point.item1, consumerRadiusPcnt), _getCurPos(point.item2, consumerRadiusPcnt));

      // var _alignments = [
      //   Alignment(p1.item1, p1.item2),
      //   Alignment(p2.item1, p2.item2)
      // ];
      //DONE: 1. Have the widget using an animation on an infinite loop where we pass point2 in the constructor and animate between p1 and p2.
      //DONE: Add Retailers to view.
      //DONE: Don't move money widget in consumer as money is a separate object belonging to society (i.e. whole system that can then also be posessed by the retailer).
      //TODO P1: Update the MoneySendAnimationWidget to use an AnimationBuilder instead so that we can control when to animate more closely.
      //TODO: 1. Convert the AnimateAlign widget to have a controller so that i am able to reset the view without needing to animate the money back to the consumer./
      //TODO: 2. Have the widget animate once when it is first drawn, representing the money widget being added to the tree, moving to retailer and then hiding.
      //TODO: 3. Have consumer parent dynamically add MoneyAnimWidget children to stack upon processing a new transaction. Consumer should then remove widgets too.
      //NOTE: The reason that AnimateAlign works by creating an animation when the alignment prop changes is that in flutter, a widget updates when the props on the widget change, not by calling handleevent functions ideally.

      // What we can also do is:
      // 1. Add a notification handler on the serviceclass void transactionReceived(Message message) { ...myCode to update the Consumer view screen which will consume updates from teh service class using the Consumer Widget }
      // 2. The consumer widget will then control the money widgets by creating a money widget whenever there is a new message using the information on the message to decide where to send teh money.
      // Put something like the following on the ServiceClass which stores the last transaction on the state. Then the notifyListeners() would be called from the service class to notify the homescreen to get the most recent transaction from the provider: ServiceClass
      /*
      void registerNotification() async {
        //...

        if (settings.authorizationStatus == AuthorizationStatus.authorized) {
          print('User granted permission');

          // For handling the received notifications
          FirebaseMessaging.onMessage.listen((RemoteMessage message) {
            // Parse the message received
            PushNotification notification = PushNotification(
              title: message.notification?.title,
              body: message.notification?.body,
            );

            setState(() {
              _notificationInfo = notification;
              _totalNotifications++;
            });
          });
        } else {
          print('User declined or has not accepted permission');
        }
      }
      */
      return AnimatedAlignJD(
        startingAlignment: startingAlignmentForAnimation,
        endingAlignment: endingAlignmentForAnimation,
        duration: Duration(milliseconds: (durationSecs * 1000.0).round()),
        curve: Curves.fastOutSlowIn,
        allowReverse: false,
        child: SizedBox(
            width: 40.0,
            height: 40.0,
            child: SvgPicture.asset('images/noun-money-4563489.svg',
                height: consumerRadiusPcnt * 0.5 * constraints.maxHeight,
                width: consumerRadiusPcnt * 0.5 * constraints.maxWidth,
                color: Color.fromARGB(255, 14, 109, 61),
                semanticsLabel: 'A £ Note [${transaction.item1.id}]')),
      );
    });
  }
}

class AnimatedAlignJD extends StatefulWidget {
  const AnimatedAlignJD({
    Key? key,
    required this.startingAlignment,
    required this.endingAlignment,
    this.child,
    this.heightFactor,
    this.widthFactor,
    this.curve = Curves.linear,
    required this.duration,
    required this.allowReverse,
    this.onEnd,
  }) : super(key: key);

  /// How to align the child.
  ///
  /// The x and y values of the [Alignment] control the horizontal and vertical
  /// alignment, respectively. An x value of -1.0 means that the left edge of
  /// the child is aligned with the left edge of the parent whereas an x value
  /// of 1.0 means that the right edge of the child is aligned with the right
  /// edge of the parent. Other values interpolate (and extrapolate) linearly.
  /// For example, a value of 0.0 means that the center of the child is aligned
  /// with the center of the parent.
  ///
  /// See also:
  ///
  ///  * [Alignment], which has more details and some convenience constants for
  ///    common positions.
  ///  * [AlignmentDirectional], which has a horizontal coordinate orientation
  ///    that depends on the [TextDirection].
  final AlignmentGeometry startingAlignment;

  /// How to align the child.
  ///
  /// The x and y values of the [Alignment] control the horizontal and vertical
  /// alignment, respectively. An x value of -1.0 means that the left edge of
  /// the child is aligned with the left edge of the parent whereas an x value
  /// of 1.0 means that the right edge of the child is aligned with the right
  /// edge of the parent. Other values interpolate (and extrapolate) linearly.
  /// For example, a value of 0.0 means that the center of the child is aligned
  /// with the center of the parent.
  ///
  /// See also:
  ///
  ///  * [Alignment], which has more details and some convenience constants for
  ///    common positions.
  ///  * [AlignmentDirectional], which has a horizontal coordinate orientation
  ///    that depends on the [TextDirection].
  final AlignmentGeometry endingAlignment;

  /// The widget below this widget in the tree.
  ///
  /// {@macro flutter.widgets.ProxyWidget.child}
  final Widget? child;

  /// If non-null, sets its height to the child's height multiplied by this factor.
  ///
  /// Must be greater than or equal to 0.0, defaults to null.
  final double? heightFactor;

  /// If non-null, sets its width to the child's width multiplied by this factor.
  ///
  /// Must be greater than or equal to 0.0, defaults to null.
  final double? widthFactor;

  final Curve curve;

  final Duration duration;

  /// If set to true, allows the widget to reverse.
  final bool allowReverse;

  /// Called when each animation transtion ends.
  final void Function(AnimationStatus status, bool? atEndAlignment)? onEnd;

  @override
  _AnimatedAlignJDState createState() => _AnimatedAlignJDState();
}

// class _AnimatedAlignJDState extends State<AnimatedAlignJD>
//     with SingleTickerProviderStateMixin {
//   late AnimationController _controller;

//   @override
//   void initState() {
//     super.initState();
//     _controller = AnimationController(
//       duration: widget.duration,
//       vsync: this,
//       value: widget.alignment.resolve(TextDirection.ltr).x,
//       animationBehavior: AnimationBehavior.normal,
//     )..repeat();
//   }

//   @override
//   void dispose() {
//     _controller.dispose();
//     super.dispose();
//   }

//   @override
//   Widget build(BuildContext context) {
//     return AnimatedBuilder(
//       animation: _controller,
//       child: widget.child,
//       builder: (BuildContext context, Widget? child) {
//         return Transform.translate(
//           offset: const Offset(50, 50),
//           child: child,
//         );
//       },
//     );
//   }
// }

class _AnimatedAlignJDState extends State<AnimatedAlignJD>
    with TickerProviderStateMixin {
// Using `late final` for [lazy initialization](https://dart.dev/null-safety/understanding-null-safety#lazy-initialization).
  late final AnimationController _controller = AnimationController(
    duration: widget.duration,
    vsync: this,
  )..forward();
  // late AnimationController _controller2;

  late final Animation<AlignmentGeometry> _animation = Tween<AlignmentGeometry>(
    begin: widget.startingAlignment,
    end: widget.endingAlignment,
  ).animate(
    CurvedAnimation(
      parent: _controller,
      curve: widget.curve,
    ),
  );

  bool _visible = true;

  @override
  void initState() {
    _visible = true;
    // _controller2 = AnimationController(
    //   duration: widget.duration,
    //   vsync: this,
    // );
    // if (widget.allowReverse) {
    //   _controller2
    //     ..repeat(reverse: true)
    //     ..forward();
    // } else {
    //   _controller2.forward();
    // }
    _animation.addStatusListener(hideCompletedAnimations);
    _animation.addStatusListener(_onEnd);
    super.initState();
  }

  void _onEnd(AnimationStatus status) {
    if (widget.onEnd != null) {
      var f = widget.onEnd!;
      f(status, _animation.value == widget.endingAlignment);
    }
  }

  void hideCompletedAnimations(AnimationStatus status) {
    // if (widget.allowReverse) {
    //   return;
    // }
    if (status == AnimationStatus.completed ||
        status == AnimationStatus.dismissed) {
      setState(() {
        _visible = false;
      });
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _animation.removeStatusListener(hideCompletedAnimations);
    _animation.removeStatusListener(_onEnd);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Visibility(
      visible: _visible,
      child: AlignTransition(
        alignment: _animation,
        child: widget.child ??
            const Padding(
              padding: EdgeInsets.all(8),
              child: FlutterLogo(size: 150.0),
            ),
        heightFactor: widget.heightFactor,
        widthFactor: widget.widthFactor,
      ),
    );
  }
}

// class _AnimatedAlignJDState extends State<AnimatedAlignJD> {
//   @override
//   Widget build(BuildContext context) {
//     return AnimatedAlign(
//       alignment: widget.alignment,
//       child: widget.child,
//       heightFactor: widget.heightFactor,
//       widthFactor: widget.widthFactor,
//       curve: widget.curve,
//       duration: widget.duration,
//     );
//   }
// }

class MyStatefulWidget extends StatefulWidget {
  const MyStatefulWidget({Key? key}) : super(key: key);

  @override
  State<MyStatefulWidget> createState() => _MyStatefulWidgetState();
}

/// AnimationControllers can be created with `vsync: this` because of TickerProviderStateMixin.
class _MyStatefulWidgetState extends State<MyStatefulWidget>
    with TickerProviderStateMixin {
// Using `late final` for [lazy initialization](https://dart.dev/null-safety/understanding-null-safety#lazy-initialization).
  late final AnimationController _controller = AnimationController(
    duration: const Duration(seconds: 2),
    vsync: this,
  )..repeat(reverse: true);
  late final Animation<AlignmentGeometry> _animation = Tween<AlignmentGeometry>(
    begin: Alignment.bottomLeft,
    end: Alignment.center,
  ).animate(
    CurvedAnimation(
      parent: _controller,
      curve: Curves.decelerate,
    ),
  );

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      child: AlignTransition(
        alignment: _animation,
        child: const Padding(
          padding: EdgeInsets.all(8),
          child: FlutterLogo(size: 150.0),
        ),
      ),
    );
  }
}
