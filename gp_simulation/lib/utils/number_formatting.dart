import 'package:intl/intl.dart';
import 'package:webtemplate/ui/model/models.dart';

final oCcy = NumberFormat("#,##0.00", "en_US");

class CurrencyNumberFormat {
  CurrencyNumberFormat(String this.currencyCode,
      [String? this.pattern, String? this.locale]) {
    numberFormat = NumberFormat(pattern, locale);
  }

  CurrencyNumberFormat.fromCostModel(CostModel cost)
      : currencyCode = cost.currency,
        pattern = "#,##0.00",
        locale = "en_US";

  final String currencyCode;
  final String? pattern;
  final String? locale;

  String get currencySymbol {
    if (currencyCode.toLowerCase() == 'gbp') {
      return '£';
    } else if (currencyCode.toLowerCase() == 'usd') {
      return '\$';
    } else if (currencyCode.toLowerCase() == 'eur') {
      return '€';
    } else {
      return currencyCode.toUpperCase();
    }
  }

  NumberFormat numberFormat = NumberFormat("#,##0.00", "en_US");

  String format(dynamic number) {
    return currencyCode + ' ' + numberFormat.format(number).toString();
  }
}
