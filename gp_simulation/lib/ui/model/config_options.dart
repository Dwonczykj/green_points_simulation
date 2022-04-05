// abstract class ConfigOptions {

//   abstract String fullBasketSize;
//   abstract String numTripsToShops;
//   abstract String numCustomers;
//   abstract String maxN;
//   abstract String convergenceTH;
//   abstract String sustainabilityBaseline;
//   abstract String strategy;
// }

abstract class ConfigOptionsDTFs {
  static const String numTripsToShops = 'NUM_SHOP_TRIPS_PER_ITERATION';
  static const String numCustomers = 'NUM_CUSTOMERS';
  static const String maxN = 'maxN';
  static const String convergenceTH = 'convergenceTH';
  static const String sustainabilityBaseline = 'sustainabilityBaseline';
  static const String strategy = 'strategy';
}

abstract class ConfigOptionsLabels {
  static const String fullBasketSize = 'Basket Size';
  static const String numTripsToShops = 'Number Trips';
  static const String numCustomers = 'Number Customers';
  static const String maxN = 'Number Iter';
  static const String convergenceTH = 'Sim. Convg. Crit.';
  static const String sustainabilityBaseline = 'Retailer Sustainability';
  static const String strategy = 'GP Generosity';
}

// abstract class ConfigOptionsDTFs {
//   static const String fullBasketSize = 'BASKET_FULL_SIZE';
//   static const String numTripsToShops = 'NUM_SHOP_TRIPS_PER_ITERATION';
//   static const String numCustomers = 'NUM_CUSTOMERS';
//   static const String maxN = 'maxN';
//   static const String convergenceTH = 'convergenceTH';
//   static const String sustainabilityBaseline = 'sustainabilityBaseline';
//   static const String strategy = 'strategy';
//   // static const String controlRetailerName = 'controlRetailerName';

//   static const labels = <String, String>{
//     ConfigOptions.fullBasketSize: 'full basket size',
//     ConfigOptions.numTripsToShops: '# trips to shops',
//     ConfigOptions.numCustomers: '# customers',
//     ConfigOptions.maxN: 'max # iterations',
//     ConfigOptions.convergenceTH: 'condition for convergence of sim',
//     ConfigOptions.strategy: 'gember points issuing generosity',
//     ConfigOptions.sustainabilityBaseline:
//         'sustainability rating of retailer supply chain',
//     // ConfigOptions.controlRetailerName: 'demonstrative retailer',
//   };

//   static int get count => labels.length;

//   static String getLabel(String option) => labels[option]!;
// }
