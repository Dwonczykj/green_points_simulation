import 'package:logging/logging.dart';
import 'package:flutter/material.dart';
import 'package:webtemplate/ui/network/market_state_viewer.dart';
import 'package:webtemplate/ui/screens/i_page_wrapper.dart';
import 'package:webtemplate/utils/string_extensions.dart';

import '../model/models.dart';

class DebugPage extends StatelessWidget {
  const DebugPage({Key? key}) : super(key: key);
  static const title = 'Debug';

  @override
  Widget build(BuildContext context) {
    return IPageWrapper(
        title: title,
        childGetter: (marketStateViewer, appStateManager) => DebugView(
              marketStateViewer: marketStateViewer,
              appStateManager: appStateManager,
            ));
  }
}

class DebugView extends StatefulWidget {
  const DebugView(
      {Key? key,
      required this.marketStateViewer,
      required this.appStateManager})
      : super(key: key);

  final IMarketStateViewer marketStateViewer;
  final AppStateManager appStateManager;

  @override
  _DebugViewState createState() => _DebugViewState();
}

class _DebugViewState extends State<DebugView> {
  final log = Logger('_DebugViewState');

  String get title => ('Debug view state');

  MarketStateViewer? get marketStateViewer =>
      (widget.marketStateViewer is MarketStateViewer)
          ? (widget.marketStateViewer as MarketStateViewer)
          : null;

  final _messages = <String>[];

  List<String> get messages =>
      widget.appStateManager.wsCallHist.map(wsEventToString).toList();

  String wsEventToString(WebCall event) {
    final isResponse = event.isResponseCall()
        ? 'RESPONSE ${(event as WebCallResponse).statusCode}'
        : 'REQUEST';
    final reqType = event.requestType.name;
    return '$isResponse $reqType ${event.uri}';
  }

  @override
  void initState() {
    super.initState();
    // marketStateViewer?.callHistoryStream.listen((event) {
    //   _messages.add(wsEventToString(event));
    // });
  }

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          // const Text(
          //   'You have pushed the button this many times:',
          // ),
          // Text(
          //   '$_counter',
          //   style: Theme.of(context).textTheme.headline4,
          // ),
          // const SizedBox(
          //   height: 12.0,
          // ),
          // Text(
          //   messages.isNotEmpty ? messages.last : 'no events',
          //   style: Theme.of(context).textTheme.headline4,
          // ),
          Container(
            alignment: Alignment.center,
            height: 400,
            width: 400,
            child: ListView(
              children: _messages.reversed
                  .take(10)
                  .map(
                    (e) => Text(
                      e,
                      style: Theme.of(context).textTheme.headline4,
                    ),
                  )
                  .toList(),
            ),
          ),
        ],
      ),
    );
  }
}
