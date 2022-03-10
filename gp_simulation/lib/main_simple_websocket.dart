import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/io.dart';
import 'package:flutter/material.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    const title = 'WebSocket Demo';
    return const MaterialApp(
      title: title,
      home: MyHomePage(
        title: title,
      ),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({
    Key? key,
    required this.title,
  }) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final TextEditingController _controller = TextEditingController();
  // https://dev.to/vibalijoshi/how-you-can-use-websockets-with-flutter-ipn
  // final _channel = IOWebSocketChannel.connect(
  //   Uri.parse(
  //       'wss://ws.postman-echo.com/socketio'), // https://blog.postman.com/introducing-postman-websocket-echo-service/
  // );
  // static const web_socket_name = 'wss://ws.postman-echo.com/raw';
  // static const web_socket_name = 'wss://ws.postman-echo.com/socketio';
  static const web_socket_name = 'ws://127.0.0.1:8443/websocket';
  final _channel = WebSocketChannel.connect(
    Uri.parse(_MyHomePageState
        .web_socket_name), // https://blog.postman.com/introducing-postman-websocket-echo-service/
  );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Form(
              child: TextFormField(
                controller: _controller,
                decoration: const InputDecoration(labelText: 'Send a message'),
              ),
            ),
            const SizedBox(height: 24),
            StreamBuilder(
              stream: _channel.stream,
              builder: (context, snapshot) {
                return Text(snapshot.hasData ? '${snapshot.data}' : '');
              },
            ),
            const SizedBox(height: 24),
            const Text('Socket endpoint: ${_MyHomePageState.web_socket_name}')
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _sendMessage,
        tooltip: 'Send message',
        child: const Icon(Icons.send),
      ), // This trailing comma makes auto-formatting nicer for build methods.
    );
  }

  void _sendMessage() {
    if (_controller.text.isNotEmpty) {
      _channel.sink
          .add(jsonEncode({'type': 'message', 'data': _controller.text}));
    }
  }

  @override
  void dispose() {
    _channel.sink.close();
    _controller.dispose();
    super.dispose();
  }
}
