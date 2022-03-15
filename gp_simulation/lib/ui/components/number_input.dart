import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:webtemplate/utils/pipe.dart';

class NumberInput extends StatelessWidget {
  NumberInput({
    Key? key,
    required this.label,
    this.controller,
    this.value,
    this.onChanged,
    this.error,
    this.icon,
    this.allowDecimal = false,
    this.disabled = false,
  }) : super(key: key) {
    if (controller == null && allowDecimal) {
      controller = _getCommaStyledController();
    }
  }

  late final TextEditingController? controller;

  final String? value;
  final String label;
  bool disabled;
  final void Function(num val)? onChanged;
  final String? error;
  final Widget? icon;
  final bool allowDecimal;

  StyleableTextFieldController _getCommaStyledController() {
    return StyleableTextFieldController(
      styles: TextPartStyleDefinitions(
        definitionList: <TextPartStyleDefinition>[
          // Gray out the part immediately after the comma using regex: r',(\d+)$'
          TextPartStyleDefinition(
            style: const TextStyle(
              color: Colors.black38,
            ),
            pattern: r',(\d+)$',
          )
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      initialValue: value,
      onChanged: (String val) => pipe_if_func_exists(
          allowDecimal
              ? double.tryParse(val) ?? 0.0
              : double.tryParse(val)?.round() ?? 0,
          onChanged),
      readOnly: disabled,
      keyboardType: TextInputType.numberWithOptions(decimal: allowDecimal),
      inputFormatters: <TextInputFormatter>[
        FilteringTextInputFormatter.allow(RegExp(_getRegexString())),
        TextInputFormatter.withFunction(
          (oldValue, newValue) => newValue.copyWith(
            text: newValue.text.replaceAll('.', ','),
          ),
        ),
      ],
      decoration: InputDecoration(
        label: Text(label),
        errorText: error,
        icon: icon,
        floatingLabelAlignment: FloatingLabelAlignment.start,
        labelStyle: Theme.of(context).textTheme.labelMedium,

      ),

    );
  }

  String _getRegexString() =>
      allowDecimal ? r'[0-9]+[,.]{0,1}[0-9]*' : r'[0-9]';
}

class TextPartStyleDefinition {
  TextPartStyleDefinition({
    required this.pattern,
    required this.style,
  });
  final String pattern;
  final TextStyle style;
}

class TextPartStyleDefinitions {
  TextPartStyleDefinitions({required this.definitionList});

  final List<TextPartStyleDefinition> definitionList;

  RegExp createCombinedPatternBasedOnStyleMap() {
    final String combinedPatternString = definitionList
        .map<String>(
          (TextPartStyleDefinition textPartStyleDefinition) =>
              textPartStyleDefinition.pattern,
        )
        .join('|');
    return RegExp(
      combinedPatternString,
      multiLine: true,
      caseSensitive: false,
    );
  }

  TextPartStyleDefinition? getStyleOfTextPart(
    String textPart,
    String text,
  ) {
    return List<TextPartStyleDefinition?>.from(definitionList).firstWhere(
      (TextPartStyleDefinition? styleDefinition) {
        if (styleDefinition == null) return false;
        bool hasMatch = false;
        RegExp(styleDefinition.pattern, caseSensitive: false)
            .allMatches(text)
            .forEach(
          (RegExpMatch currentMatch) {
            if (hasMatch) return;
            if (currentMatch.group(0) == textPart) {
              hasMatch = true;
            }
          },
        );
        return hasMatch;
      },
      orElse: () => null,
    );
  }
}

class StyleableTextFieldController extends TextEditingController {
  StyleableTextFieldController({
    required this.styles,
  }) : combinedPattern = styles.createCombinedPatternBasedOnStyleMap();

  final TextPartStyleDefinitions styles;
  final Pattern combinedPattern;

  @override
  TextSpan buildTextSpan({
    required BuildContext context,
    TextStyle? style,
    required bool withComposing,
  }) {
    final List<InlineSpan> textSpanChildren = <InlineSpan>[];
    text.splitMapJoin(
      combinedPattern,
      onMatch: (Match match) {
        final String? textPart = match.group(0);
        if (textPart == null) return '';
        final TextPartStyleDefinition? styleDefinition =
            styles.getStyleOfTextPart(
          textPart,
          text,
        );
        if (styleDefinition == null) return '';
        _addTextSpan(
          textSpanChildren,
          textPart,
          style?.merge(styleDefinition.style),
        );
        return '';
      },
      onNonMatch: (String text) {
        _addTextSpan(textSpanChildren, text, style);
        return '';
      },
    );
    return TextSpan(style: style, children: textSpanChildren);
  }

  void _addTextSpan(
    List<InlineSpan> textSpanChildren,
    String? textToBeStyled,
    TextStyle? style,
  ) {
    textSpanChildren.add(
      TextSpan(
        text: textToBeStyled,
        style: style,
      ),
    );
  }
}
