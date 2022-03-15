// import 'package:chopper/chopper.dart'; // flutter pub run build_runner build --delete-conflicting-outputs

import 'package:logging/logging.dart';

abstract class TSerializable {
  TSerializable();

  TSerializable.fromJson(Map<String, dynamic> json);

  static final log = Logger('TSerializable');

  Map<String, dynamic> toJson();

  // static T deepCopy<T extends TSerializable>(T tSerializableInst) =>
  //     T.fromJson(toJson());

  static Map<String, T> getJsonMapValue<T extends TSerializable>(
      Map<String, dynamic> json,
      String fieldName,
      T Function(Map<String, dynamic> a) fromJsonFactory,
      {Map<String, T>? defaultVal}) {
    try {
      json = _defaultJson(json, fieldName, defaultVal: defaultVal);
      return json[fieldName] == null ||
              (json[fieldName] as Map<String, dynamic>).isEmpty
          ? defaultVal!
          : (json[fieldName] as Map<String, dynamic>)
              .map((key, value) => MapEntry(key, fromJsonFactory(value)));
    } on JsonParseException catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: '${err.fieldName}.$fieldName');
    } catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: fieldName);
    }
  }

  static List<T> getJsonListValue<T extends TSerializable>(
      Map<String, dynamic> json,
      String fieldName,
      T Function(Map<String, dynamic> a) fromJsonFactory,
      {List<T>? defaultVal}) {
    try {
      json = _defaultJson(json, fieldName, defaultVal: defaultVal ?? <T>[]);
      assert(json[fieldName] is List);
      return json[fieldName] == null || (json[fieldName] as List).isEmpty
          ? defaultVal!
          : (json[fieldName] as List).map((j) => fromJsonFactory(j)).toList();
      // return (json.containsKey(fieldName) &&
      //             ((json[fieldName] ?? []) as List).isNotEmpty
      //         ? (json[fieldName] as List)
      //             .map((j) => modelType.fromJson(j))
      //             .toList()
      //         : const <ItemModel>[])
    } on JsonParseException catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: '${err.fieldName}.$fieldName');
    } catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: fieldName);
    }
  }

  static Map<String, List<T>> getJsonMapListValue<T extends TSerializable>(
      Map<String, dynamic> json,
      String fieldName,
      T Function(Map<String, dynamic> a) fromJsonFactory,
      {Map<String, List<T>>? defaultVal}) {
    try {
      json = _defaultJson(json, fieldName,
          defaultVal: defaultVal ?? <String, List<T>>{});
      return json[fieldName] == null ||
              (json[fieldName] as Map<String, dynamic>).isEmpty ||
              (json[fieldName] is! Map<String, List>)
          ? defaultVal!
          : (json[fieldName] as Map<String, List>).map((key, value) => MapEntry(
              key,
              value
                  .map((v) => fromJsonFactory(v as Map<String, dynamic>))
                  .toList()));
    } on JsonParseException catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: '${err.fieldName}.$fieldName');
    } catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: fieldName);
    }
  }

  static T getJsonValue<T extends TSerializable>(Map<String, dynamic> json,
      String fieldName, T Function(Map<String, dynamic> a) fromJsonFactory,
      {T? defaultVal}) {
    try {
      json = _defaultJson(json, fieldName, defaultVal: defaultVal);
      // assert(json[fieldName] is! List);
      return json[fieldName] == null
          ? defaultVal!
          : fromJsonFactory(json[fieldName]);
    } on JsonParseException catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: '${err.fieldName}.$fieldName');
    } catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: fieldName);
    }
  }

  static T getJsonValTypeValue<T>(Map<String, dynamic> json, String fieldName,
      {T? defaultVal}) {
    try {
      json = _defaultJson(json, fieldName, defaultVal: defaultVal);
      assert(json.containsKey(fieldName));
      json[fieldName] ??= defaultVal;
      // assert(json[fieldName] is T); // BUG: Dont check type as type is _JsonMap
      if (json[fieldName] != null && json[fieldName] is! T) {
        json[fieldName] = Map<String, dynamic>.from(json[fieldName]);
      }
      return (json[fieldName] ?? defaultVal);
    } on JsonParseException catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: '${err.fieldName}.$fieldName');
    } catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: fieldName);
    }
  }

  static Map<String, TVal> getJsonMapValTypeValue<TVal>(
      Map<String, dynamic> json, String fieldName,
      {Map<String, TVal>? defaultVal}) {
    try {
      json = _defaultJson(json, fieldName, defaultVal: defaultVal);
      assert(json.containsKey(fieldName));
      json[fieldName] ??= defaultVal;
      // assert(json[fieldName] is T); // BUG: Dont check type as type is _JsonMap
      if (json[fieldName] != null && json[fieldName] is! Map<String, TVal>) {
        json[fieldName] = Map<String, TVal>.from(json[fieldName]);
      }
      return (json[fieldName] ?? defaultVal);
    } on JsonParseException catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: '${err.fieldName}.$fieldName');
    } catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: fieldName);
    }
  }

  static T getJsonValTypeTryParseValue<T>(
      Map<String, dynamic> json, String fieldName,
      {required T? Function(String jsonVal) parser, T? defaultVal}) {
    try {
      json = _defaultJson(json, fieldName, defaultVal: defaultVal);
      assert(json.containsKey(fieldName));
      json[fieldName] ??= defaultVal;
      // assert(json[fieldName] is T); // BUG: Dont check type as type is _JsonMap
      if (json[fieldName] != null && json[fieldName] is! String) {
        json[fieldName] = Map<String, dynamic>.from(json[fieldName]);
      } else {
        json[fieldName] = parser(json[fieldName]) ?? defaultVal;
      }
      return (json[fieldName] ?? defaultVal);
    } on JsonParseException catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: '${err.fieldName}.$fieldName');
    } catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: fieldName);
    }
  }

  static T getJsonValueFromChain<T extends TSerializable>(
      Map<String, dynamic> json,
      List<String> fieldNames,
      T Function(Map<String, dynamic> a) fromJsonFactory,
      {T? defaultVal}) {
    dynamic out = json;
    try {
      assert(fieldNames.isNotEmpty);

      for (String fieldName in fieldNames) {
        out ??= <String, dynamic>{fieldName: null};
        out = out[fieldName];
      }
      assert(out != null || defaultVal != null);
      return out == null ? defaultVal! : fromJsonFactory(out);
    } on JsonParseException catch (err) {
      var fieldNameJ = fieldNames.join('.');
      throw JsonParseException('Unable to pass json of fieldName: $fieldNameJ',
          fieldName: '${err.fieldName}.$fieldNameJ');
    } catch (err) {
      var fieldNameJ = fieldNames.join('.');
      throw JsonParseException(
          'Unable to pass json of fieldName: $fieldNameJ with value: $out',
          fieldName: fieldNameJ);
    }
  }

  static List<T> getJsonListValueFromChain<T extends TSerializable>(
      Map<String, dynamic> json,
      List<String> fieldNames,
      T Function(Map<String, dynamic> a) fromJsonFactory,
      {List<T>? defaultVal}) {
    try {
      assert(fieldNames.isNotEmpty);
      dynamic out = json;
      for (String fieldName in fieldNames) {
        out ??= <String, dynamic>{fieldName: null};
        out = out[fieldName];
      }
      assert(out != null || defaultVal != null);
      if (out != null) {
        assert(out is List);
      }
      return out == null
          ? defaultVal!
          : (out as List).map((j) => fromJsonFactory(j)).toList();
    } on JsonParseException catch (err) {
      var fieldNameJ = fieldNames.join('.');
      throw JsonParseException('Unable to pass json of fieldName: $fieldNameJ',
          fieldName: '${err.fieldName}.$fieldNameJ');
    } catch (err) {
      var fieldNameJ = fieldNames.join('.');
      throw JsonParseException('Unable to pass json of fieldName: $fieldNameJ',
          fieldName: fieldNameJ);
    }
  }

  static T getJsonValTypeValueFromChain<T>(
      Map<String, dynamic> json, List<String> fieldNames,
      {T? defaultVal}) {
    try {
      assert(fieldNames.isNotEmpty);
      dynamic out = json;
      for (String fieldName in fieldNames) {
        out ??= <String, dynamic>{fieldName: null};
        out = out[fieldName];
      }
      out ??= defaultVal;
      return out;
    } on JsonParseException catch (err) {
      var fieldNameJ = fieldNames.join('.');
      throw JsonParseException('Unable to pass json of fieldName: $fieldNameJ',
          fieldName: '${err.fieldName}.$fieldNameJ');
    } catch (err) {
      var fieldNameJ = fieldNames.join('.');
      throw JsonParseException('Unable to pass json of fieldName: $fieldNameJ',
          fieldName: fieldNameJ);
    }
  }

  static Map<String, dynamic> _defaultJson(
      Map<String, dynamic> json, String fieldName,
      {dynamic defaultVal}) {
    try {
      if (defaultVal == null) {
        assert(json.containsKey(fieldName));
      } else {
        if (!json.containsKey(fieldName)) {
          json[fieldName] = defaultVal;
        }
      }
      return json;
    } on JsonParseException catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: '${err.fieldName}.$fieldName');
    } catch (err) {
      throw JsonParseException('Unable to pass json of fieldName: $fieldName',
          fieldName: fieldName);
    }
  }
}

abstract class ServiceInterface<T extends TSerializable> {
  Future<Iterable<T>> loadService();
}

class JsonParseException implements Exception {
  JsonParseException(this.message, {required this.fieldName}) : super() {
    log.fine(errMsg);
  }

  static final log = Logger('JsonParseException');

  final String fieldName;
  final String message;

  String get errMsg => 'JsonParseException: $message';
}
