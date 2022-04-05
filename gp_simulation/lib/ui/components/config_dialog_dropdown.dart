import 'package:flutter/material.dart';

import '../model/models.dart';

class ConfigDialogDrowdown<TVal> extends StatelessWidget {
  ConfigDialogDrowdown({
    Key? key,
    required this.appStateMgr,
    required this.label,
    required this.value,
    required this.onChanged,
    required this.labelsToValuesMap,
    this.hint,
    this.labelValueLayout,
    this.disabledHint,
  }) : super(key: key);

  final AppStateManager appStateMgr;
  final String label;
  final TVal value;
  final void Function(TVal? value) onChanged;
  final Map<String, TVal> labelsToValuesMap;
  final Widget? hint;
  final Widget? disabledHint;
  final Axis? labelValueLayout;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      //https://stackoverflow.com/a/56767046/7439791
      width: 300,
      child: Flex(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        direction: labelValueLayout ?? Axis.vertical,
        children: <Widget>[
          Text(
            label,
            style: Theme.of(context).textTheme.labelSmall,
          ),
          SizedBox(
            width: 300,
            child: ButtonTheme(
              alignedDropdown: true,
              child: DropdownButton(
                value: value,
                hint: hint,
                disabledHint: disabledHint,
                icon: const Icon(Icons.arrow_downward),
                elevation: 16,
                style: TextStyle(
                    color: Theme.of(context).buttonTheme.colorScheme?.primary ??
                        Colors.limeAccent[100]),
                underline: Container(
                  height: 2,
                  color: Theme.of(context).buttonTheme.colorScheme?.secondary ??
                      Colors.deepPurpleAccent,
                ),
                // selectedItemBuilder: ,
                items: labelsToValuesMap.entries
                    .map((entry) => DropdownMenuItem(
                          child: Text(
                            entry.key,
                          ),
                          value: entry.value,
                        ))
                    .toList(),
                // onChanged: (ViewMeasureType? value) {
                //   appStateMgr
                //       .updateMeasureType(value ?? ViewMeasureType.salesCount);
                onChanged: onChanged,
              ),
            ),
          )
        ],
      ),
    );
  }
}
