import 'dart:convert';

import 'package:ansicolor/ansicolor.dart';
import 'package:webtemplate/utils/ansi_print_colors.dart';

import '../../model/all_models.dart';
import '../service_interface.dart';

class SocketioMessageHandler extends WebSocketMessageHandler {
  SocketioMessageHandler({required String type, required data})
      : super(message: {'type': type, 'data': data});
}

class WebSocketMessageHandler {
  WebSocketMessageHandler({
    required dynamic message,
  }) : _message = message;

  Map<String, dynamic>? _jsonObj;

  final AnsiPen greenPen = AnsiPen()..green();

  Map<String, dynamic> processMessage(dynamic msg) {
    if (_jsonObj != null) {
      return _jsonObj!;
    }
    if (msg is String) {
      try {
        _jsonObj = Map<String, dynamic>.from(jsonDecode(msg));
      } catch (e) {
        _jsonObj = {
          'type': 'WebSocketMessageHandler could not jsonDecode event',
          'data': msg
        };
      }
    } else if (msg is Map<String, dynamic>) {
      _jsonObj = msg;
    } else {
      _jsonObj = {
        'type':
            'WebSocketMessageHandler cant process event non-string and non-map',
        'data': msg
      };
    }
    PrintPens.greenPen(type.toString());
    return _jsonObj!;
  }

  final dynamic _message;

  Map<String, dynamic> get message => processMessage(_message);

  dynamic get type => message['type'];
  dynamic get data => message['data'];

  dynamic model;

  bool looksLikeTransactionJson() {
    if (data is Map<String, dynamic>) {
      try {
        model = TransactionModel.fromJson(data, shouldThrow: false);
        return true;
      } catch (e) {
        return false;
      }
    }
    return false;
  }

  bool looksLikeEntityJson() {
    if (data is Map<String, dynamic>) {
      try {
        model = RetailerModel.fromJson(data, shouldThrow: false);
        return true;
      } on JsonParseException {
      } catch (e) {
        return false;
      }
      try {
        model = CustomerModel.fromJson(data, shouldThrow: false);
        return true;
      } on JsonParseException {
        return false;
      } catch (e) {
        return false;
      }
      // try {
      //   // model = EntityModel.fromJson(data);
      //   return true;
      // } catch (e) {

      // }
    }
    return false;
  }

  TransactionModel? getTransactionModelFromJson() {
    if (model is TransactionModel) {
      return model;
    }
    return null;
  }

  EntityModel? getEntityModelFromJson() {
    if (model is EntityModel) {
      return model;
    }
    return null;
  }
}
