import 'dart:convert';
import 'dart:html';
import 'dart:math';

import 'package:collection/collection.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';

import '../../utils/number_formatting.dart';
import '../network/service_interface.dart';

class IdentifiableModel extends TSerializable {
  final String id;

  IdentifiableModel({required this.id}) : super();

  factory IdentifiableModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return IdentifiableModel(
        id: TSerializable.getJsonValTypeValue<String>(json, 'id',
            defaultVal: ''));
  }

  @override
  Map<String, dynamic> toJson() => <String, dynamic>{'id': id};
}

class InstitutionModel extends IdentifiableModel {
  final String name;

  InstitutionModel({required this.name, String id = ''}) : super(id: id);

  factory InstitutionModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return InstitutionModel(
        name: TSerializable.getJsonValTypeValue<String>(json, 'name'),
        id: TSerializable.getJsonValTypeValue<String>(json, 'id',
            defaultVal: ''));
  }

  @override
  Map<String, dynamic> toJson() => <String, dynamic>{'name': name, 'id': id};
}

class EntityModel extends InstitutionModel {
  final BankModel bank;
  final BankAccountViewModel balance;
  final CostModel balanceMoney;

  EntityModel(
      {required String name,
      required this.bank,
      String id = '',
      required this.balance,
      required this.balanceMoney})
      : super(name: name, id: id);

  EntityModel.fromSuper(
      InstitutionModel superObj, this.bank, this.balance, this.balanceMoney)
      : super(name: superObj.name, id: superObj.id);

  factory EntityModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return EntityModel.fromSuper(
      InstitutionModel.fromJson(json),
      TSerializable.getJsonValue(json, 'bank', BankModel.fromJson),
      TSerializable.getJsonValue(
          json, 'balance', BankAccountViewModel.fromJson),
      TSerializable.getJsonValue(json, 'balanceMoney', CostModel.fromJson),
    );
  }

  @override
  Map<String, dynamic> toJson() =>
      super.toJson()..addAll(<String, dynamic>{'bank': bank.toJson()});
}

class CustomerModel extends EntityModel {
  final List<ItemModel> basket;
  final List<PurchaseModel> purchaseHistory;

  CustomerModel(
      {required String name,
      required BankModel bank,
      String id = '',
      this.basket = const <ItemModel>[],
      this.purchaseHistory = const <PurchaseModel>[],
      required BankAccountViewModel balance,
      required CostModel balanceMoney})
      : super(
            name: name,
            bank: bank,
            id: id,
            balance: balance,
            balanceMoney: balanceMoney);

  CustomerModel.fromSuper(
      EntityModel superObj, this.basket, this.purchaseHistory)
      : super(
            name: superObj.name,
            bank: superObj.bank,
            id: superObj.id,
            balance: superObj.balance,
            balanceMoney: superObj.balanceMoney);

  factory CustomerModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return CustomerModel.fromSuper(
        EntityModel.fromJson(json),
        TSerializable.getJsonListValue(json, 'basket', ItemModel.fromJson,
            defaultVal: const <ItemModel>[]),
        TSerializable.getJsonListValue(
            json, 'purchaseHistory', PurchaseModel.fromJson,
            defaultVal: const <PurchaseModel>[]));
  }

  @override
  Map<String, dynamic> toJson() => super.toJson()
    ..addAll(<String, dynamic>{
      'basket': basket.map((i) => i.toJson()).toList(),
      'purchaseHistory': purchaseHistory.map((p) => p.toJson()).toList()
    });
}

class RetailerNameModel extends InstitutionModel {
  RetailerNameModel({required String name}) : super(name: name);

  RetailerNameModel.fromSuper(InstitutionModel superObj)
      : super(name: superObj.name, id: superObj.id);

  factory RetailerNameModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return RetailerNameModel.fromSuper(InstitutionModel.fromJson(json));
  }

  @override
  Map<String, dynamic> toJson() => super.toJson()..addAll(<String, dynamic>{});
}

class RetailerStrategy {
  static const double ZERO = 0.0;
  static const double MIN = 0.1;
  static const double COMPETITIVE = 1.0;
  static const double MAX = 10.0;
  static const values = <String, double>{
    'ZERO': ZERO,
    'MIN': MIN,
    'COMPETITIVE': COMPETITIVE,
    'MAX': MAX,
  };
  static String getLabel(double strategy) {
    final matches =
        values.entries.where((element) => element.value == strategy);
    if (matches.isNotEmpty) {
      return matches.first.key;
    } else {
      return 'N/A';
    }
  }
}

class RetailerSustainability {
  static const double LOW = -0.25;
  static const double AVERAGE = 0.0;
  static const double HIGH = 0.25;
  static const values = <String, double>{
    'LOW': LOW,
    'AVERAGE': AVERAGE,
    'HIGH': HIGH,
  };
  static String getLabel(double sustainability) {
    final matches =
        values.entries.where((element) => element.value == sustainability);
    if (matches.isNotEmpty) {
      return matches.first.key;
    } else {
      return 'N/A';
    }
  }
}

class ControlRetailerModel extends RetailerNameModel {
  double strategy;
  double sustainability;

  ControlRetailerModel({
    required String name,
    required this.strategy,
    required this.sustainability,
  }) : super(
          name: name,
        );

  ControlRetailerModel.fromSuper(
      RetailerNameModel superObj, this.strategy, this.sustainability)
      : super(
          name: superObj.name,
        );

  factory ControlRetailerModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return ControlRetailerModel.fromSuper(
      RetailerNameModel.fromJson(json),
      TSerializable.getJsonValTypeValue<double>(json, 'strategy'),
      TSerializable.getJsonValTypeValue<double>(json, 'sustainability'),
    );
  }

  @override
  Map<String, dynamic> toJson() => super.toJson()
    ..addAll(<String, dynamic>{
      'strategy': strategy,
      'sustainability': sustainability,
    });
}

class RetailerModel extends EntityModel {
  List<SaleModel> salesHistory;
  SalesAggregationModel totalSales;
  double strategy;
  double sustainability;

  RetailerModel({
    required String name,
    required BankModel bank,
    String id = '',
    required this.salesHistory,
    required this.totalSales,
    required BankAccountViewModel balance,
    required CostModel balanceMoney,
    required this.strategy,
    required this.sustainability,
  }) : super(
            name: name,
            bank: bank,
            id: id,
            balance: balance,
            balanceMoney: balanceMoney);

  RetailerModel.fromSuper(EntityModel superObj, this.salesHistory,
      this.totalSales, this.strategy, this.sustainability)
      : super(
            name: superObj.name,
            bank: superObj.bank,
            id: superObj.id,
            balance: superObj.balance,
            balanceMoney: superObj.balanceMoney);

  factory RetailerModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return RetailerModel.fromSuper(
      EntityModel.fromJson(json),
      TSerializable.getJsonListValue(json, 'salesHistory', SaleModel.fromJson,
          defaultVal: const <SaleModel>[]),
      TSerializable.getJsonValue(
          json, 'totalSales', SalesAggregationModel.fromJson),
      TSerializable.getJsonValTypeValue<double>(json, 'strategy'),
      TSerializable.getJsonValTypeValue<double>(json, 'sustainability'),
    );
  }

  @override
  Map<String, dynamic> toJson() => super.toJson()
    ..addAll(<String, dynamic>{
      'strategy': strategy,
      'sustainability': sustainability,
      'salesHistory': salesHistory.map((e) => e.toJson()).toList(),
      'totalSales': totalSales.toJson(),
    });

  Color get retailerColor =>
      colorMap[name] ??
      Color.fromRGBO(Random().nextInt(255), Random().nextInt(255),
          Random().nextInt(255), Random().nextInt(100) / 100.0);
}

const colorMap = <String, Color>{
  'ASDA': Color.fromARGB(255, 120, 180, 51),
  'Coop': Color.fromARGB(255, 14, 194, 179),
  'Tescos': Color.fromARGB(255, 35, 47, 117),
  'VW': Color.fromARGB(255, 87, 87, 86),
  'Starbucks': Color.fromARGB(255, 6, 59, 28),
};

class SimulationTokenModel extends IdentifiableModel {
  SimulationTokenModel({
    required String simulationId,
  }) : super(id: simulationId);

  String get simulationId => id;

  SimulationTokenModel.fromSuper(IdentifiableModel superObj)
      : super(id: superObj.id);

  factory SimulationTokenModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return SimulationTokenModel(
        simulationId:
            TSerializable.getJsonValTypeValue<String>(json, 'simulation_id'));
  }

  @override
  Map<String, String> toJson() => <String, String>{
        'simulation_id': simulationId,
      };
}

class BankModelLight extends InstitutionModel {
  BankModelLight({
    required String name,
    String id = '',
  }) : super(name: name, id: id);

  BankModelLight.fromSuper(InstitutionModel superObj)
      : super(name: superObj.name, id: superObj.id);

  factory BankModelLight.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return BankModelLight.fromSuper(InstitutionModel.fromJson(json));
  }

  @override
  Map<String, dynamic> toJson() => super.toJson();
}

class BankModel extends BankModelLight {
  final List<BankAccountModel> accounts;

  BankModel(
      {required String name,
      String id = '',
      this.accounts = const <BankAccountModel>[]})
      : super(name: name, id: id);

  BankModel.fromSuper(InstitutionModel superObj,
      {this.accounts = const <BankAccountModel>[]})
      : super(name: superObj.name, id: superObj.id);

  factory BankModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return BankModel.fromSuper(BankModelLight.fromJson(json),
        accounts: TSerializable.getJsonListValue(
            json, 'accounts', BankAccountModel.fromJson,
            defaultVal: const <BankAccountModel>[]));
  }

  @override
  Map<String, dynamic> toJson() => super.toJson()
    ..addAll(<String, dynamic>{
      'accounts': accounts.map((e) => e.toJson()).toList()
    });
}

class BankAccountNameModel extends IdentifiableModel {
  BankAccountNameModel({required String id, required this.ownerId})
      : super(id: id);

  IdentifiableModel ownerId;

  BankAccountNameModel.fromSuper(IdentifiableModel superObj, this.ownerId)
      : super(id: superObj.id);

  factory BankAccountNameModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return BankAccountNameModel.fromSuper(IdentifiableModel.fromJson(json),
        IdentifiableModel.fromJson(json['owner']));
  }

  @override
  Map<String, dynamic> toJson() => super.toJson()..addAll(<String, dynamic>{});
}

class CryptoWalletModel extends TSerializable {
  final CoinModel ethBalance;
  final double gpBalance;
  final InstitutionModel owner;
  final IdentifiableModel ownerBankAccount;
  final InstitutionModel ownerBank;

  CryptoWalletModel({
    required this.ethBalance,
    required this.gpBalance,
    required this.owner,
    required this.ownerBankAccount,
    required this.ownerBank,
  }) : super();

  factory CryptoWalletModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return CryptoWalletModel(
      ethBalance:
          TSerializable.getJsonValue(json, 'ethBalance', CoinModel.fromJson),
      gpBalance: TSerializable.getJsonValTypeValue<double>(json, 'gpBalance'),
      owner:
          TSerializable.getJsonValue(json, 'owner', InstitutionModel.fromJson),
      ownerBankAccount: TSerializable.getJsonValue(
          json, 'ownerBankAccount', IdentifiableModel.fromJson),
      ownerBank: TSerializable.getJsonValue(
          json, 'ownerBank', InstitutionModel.fromJson),
    );
  }

  @override
  Map<String, dynamic> toJson() => {
        "ethBalance": ethBalance.toJson(),
        "gpBalance": gpBalance,
        "owner": owner.toJson(),
        "ownerBankAccount": ownerBankAccount.toJson(),
        "ownerBank": ownerBank.toJson(),
      };
}

class BankAccountModel extends IdentifiableModel {
  final EntityModel owner;
  final double balance;
  final BankModel bank;
  final String fiatCurrency;
  final CryptoWalletModel? cryptoWallet;

  BankAccountModel(
    String id, {
    required this.owner,
    required this.balance,
    required this.bank,
    required this.fiatCurrency,
    this.cryptoWallet,
  }) : super(id: id);

  factory BankAccountModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return BankAccountModel(
      json['id'],
      owner: TSerializable.getJsonValue(json, 'owner', EntityModel.fromJson),
      balance: TSerializable.getJsonValTypeValue<double>(json, 'balance'),
      bank: TSerializable.getJsonValue(json, 'bank', BankModel.fromJson),
      fiatCurrency:
          TSerializable.getJsonValTypeValue<String>(json, 'fiatCurrency'),
      cryptoWallet: TSerializable.getJsonValue(
          json, 'cryptoWallet', CryptoWalletModel.fromJson),
    );
  }

  @override
  Map<String, dynamic> toJson() => super.toJson()
    ..addAll(<String, dynamic>{
      'owner': owner.toJson(),
      'balance': balance,
      'bank': bank.toJson(),
      'fiatCurrency': fiatCurrency,
      'cryptoWallet': cryptoWallet?.toJson(),
    });
}

class BankAccountModelLight extends IdentifiableModel {
  final InstitutionModel owner;
  final String fiatCurrency;
  final InstitutionModel bank;
  final BankAccountViewModel balance;
  final CryptoWalletModel? cryptoWallet;

  BankAccountModelLight(
    String id, {
    required this.owner,
    required this.balance,
    required this.bank,
    required this.fiatCurrency,
    this.cryptoWallet,
  }) : super(id: id);

  factory BankAccountModelLight.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return BankAccountModelLight(
      json['id'],
      owner:
          TSerializable.getJsonValue(json, 'owner', InstitutionModel.fromJson),
      balance: TSerializable.getJsonValue(
          json, 'balance', BankAccountViewModel.fromJson),
      bank: TSerializable.getJsonValue(json, 'bank', InstitutionModel.fromJson),
      fiatCurrency:
          TSerializable.getJsonValTypeValue<String>(json, 'fiatCurrency'),
      cryptoWallet: TSerializable.getJsonValue(
          json, 'cryptoWallet', CryptoWalletModel.fromJson),
    );
  }

  @override
  Map<String, dynamic> toJson() => super.toJson()
    ..addAll(<String, dynamic>{
      'owner': owner.toJson(),
      'balance': balance.toJson(),
      'bank': bank.toJson(),
      'fiatCurrency': fiatCurrency,
      'cryptoWallet': cryptoWallet?.toJson(),
    });
}

class BankAccountViewModel extends TSerializable {
  final String viewCurrency;
  final String underlyingCurrency;
  final CostModel greenPointsMonetaryValue;
  final double greenPoints;
  final CostModel moneyBalance;
  final CostModel combinedBalance;

  BankAccountViewModel({
    required this.viewCurrency,
    required this.underlyingCurrency,
    required this.greenPointsMonetaryValue,
    required this.greenPoints,
    required this.moneyBalance,
    required this.combinedBalance,
  }) : super();

  factory BankAccountViewModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return BankAccountViewModel(
      viewCurrency:
          TSerializable.getJsonValTypeValue<String>(json, 'viewCurrency'),
      underlyingCurrency:
          TSerializable.getJsonValTypeValue<String>(json, 'underlyingCurrency'),
      greenPointsMonetaryValue: TSerializable.getJsonValue(
          json, 'greenPointsMonetaryValue', CostModel.fromJson),
      greenPoints: TSerializable.getJsonValTypeValue<double>(
          json, 'greenPoints',
          defaultVal: 0.0),
      moneyBalance:
          TSerializable.getJsonValue(json, 'moneyBalance', CostModel.fromJson),
      combinedBalance: TSerializable.getJsonValue(
          json, 'combinedBalance', CostModel.fromJson),
    );
  }

  static BankAccountViewModel dummy() {
    return BankAccountViewModel(
      viewCurrency: 'GBP',
      underlyingCurrency: 'GBP',
      moneyBalance: CostModel(0.0, 'GBP'),
      combinedBalance: CostModel(0.0, 'GBP'),
      greenPoints: 0.0,
      greenPointsMonetaryValue: CostModel(0.0, 'GBP'),
    );
  }

  @override
  Map<String, dynamic> toJson() => {
        "viewCurrency": viewCurrency,
        "underlyingCurrency": underlyingCurrency,
        "greenPointsMonetaryValue": greenPointsMonetaryValue.toJson(),
        "greenPoints": greenPoints,
        "moneyBalance": moneyBalance.toJson(),
        "combinedBalance": combinedBalance.toJson(),
      };
}

class CoinModel extends TSerializable {
  final double amount;

  CoinModel(this.amount) : super();

  factory CoinModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return CoinModel(json['amount']);
  }

  @override
  Map<String, dynamic> toJson() => <String, dynamic>{'amount': amount};

  @override
  String toString() => "$amount";
}

class CoinDetailModel extends CoinModel {
  final double tokenValueInPeggedCurrency;
  final CostModel valueInPeggedCurrency;
  final String peggedCurrency;

  CoinDetailModel({
    required double amount,
    required this.tokenValueInPeggedCurrency,
    required this.valueInPeggedCurrency,
    required this.peggedCurrency,
  }) : super(amount);

  CoinDetailModel.fromSuper(CoinModel superObj, this.tokenValueInPeggedCurrency,
      this.valueInPeggedCurrency, this.peggedCurrency)
      : super(superObj.amount);

  factory CoinDetailModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return CoinDetailModel.fromSuper(
      CoinModel.fromJson(json),
      TSerializable.getJsonValTypeValue<double>(
          json, 'tokenValueInPeggedCurrency'),
      TSerializable.getJsonValue(
          json, 'valueInPeggedCurrency', CostModel.fromJson),
      TSerializable.getJsonValTypeValue<String>(json, 'peggedCurrency'),
    );
  }

  @override
  Map<String, dynamic> toJson() => super.toJson()
    ..addAll(<String, dynamic>{
      'tokenValueInPeggedCurrency': tokenValueInPeggedCurrency,
      'valueInPeggedCurrency': valueInPeggedCurrency.toJson(),
      'peggedCurrency': peggedCurrency,
    });
}

class CostModel extends TSerializable {
  final double amount;
  final String currency;

  CostModel(this.amount, this.currency) : super();

  factory CostModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return CostModel(json['amount'], json['currency']);
  }

  @override
  Map<String, dynamic> toJson() =>
      <String, dynamic>{'amount': amount, 'currency': currency};

  @override
  String toString() {
    try {
      return CurrencyNumberFormat(currency).format(amount);
    } catch (e) {
      return '$currency $amount';
    }
  }
}

class ItemModel extends TSerializable {
  final String id;
  final String name;
  final RetailerNameModel retailer;
  final CostModel cost;
  final double KGCo2;
  final double GP;

  ItemModel(
      {required this.name,
      this.id = '',
      required this.retailer,
      required this.cost,
      required this.KGCo2,
      required this.GP})
      : super();

  factory ItemModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return ItemModel(
        name: TSerializable.getJsonValTypeValue<String>(json, 'name'),
        id: TSerializable.getJsonValTypeValue<String>(json, 'id',
            defaultVal: ''),
        retailer: TSerializable.getJsonValue(
            json, 'retailer', RetailerNameModel.fromJson),
        cost: TSerializable.getJsonValue(json, 'cost', CostModel.fromJson),
        KGCo2: TSerializable.getJsonValTypeValue<double>(json, 'KGCo2'),
        GP: TSerializable.getJsonValTypeValue<double>(json, 'GP'));
  }

  @override
  Map<String, dynamic> toJson() => <String, dynamic>{
        'name': name,
        'id': id,
        'retailer': retailer.toJson(),
        'cost': cost.toJson(),
        'KGCo2': KGCo2,
        'GP': GP
      };
}

class GreenPointsPaymentModel extends TSerializable {
  final CoinDetailModel greenPoints;
  final CoinModel gas;
  final CostModel money;

  GreenPointsPaymentModel({
    required this.greenPoints,
    required this.gas,
    required this.money,
  }) : super();

  factory GreenPointsPaymentModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return GreenPointsPaymentModel(
      greenPoints: TSerializable.getJsonValue(
          json, 'greenPoints', CoinDetailModel.fromJson),
      gas: TSerializable.getJsonValue(json, 'gas', CoinModel.fromJson),
      money: TSerializable.getJsonValue(json, 'money', CostModel.fromJson),
    );
  }

  @override
  Map<String, dynamic> toJson() => <String, dynamic>{
        'greenPoints': greenPoints.toJson(),
        'gas': gas.toJson(),
        'money': money.toJson(),
      };
}

class EtherPaymentModel extends TSerializable {
  final CoinModel ether;
  final CoinModel gas;
  final CostModel money;

  EtherPaymentModel({
    required this.ether,
    required this.gas,
    required this.money,
  }) : super();

  factory EtherPaymentModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return EtherPaymentModel(
      ether: TSerializable.getJsonValue(json, 'ether', CoinModel.fromJson),
      gas: TSerializable.getJsonValue(json, 'gas', CoinModel.fromJson),
      money: TSerializable.getJsonValue(json, 'money', CostModel.fromJson),
    );
  }

  @override
  Map<String, dynamic> toJson() => <String, dynamic>{
        'greenPoints': ether.toJson(),
        'gas': gas.toJson(),
        'money': money.toJson(),
      };
}

class SaleModel extends ItemModel {
  final GreenPointsPaymentModel greenPointsIssuedForItem;

  SaleModel(
      {required String name,
      String id = '',
      required retailer,
      required cost,
      required KGCo2,
      required GP,
      required this.greenPointsIssuedForItem})
      : super(
            name: name,
            id: id,
            retailer: retailer,
            cost: cost,
            KGCo2: KGCo2,
            GP: GP);

  SaleModel.fromSuper(ItemModel superObj, this.greenPointsIssuedForItem)
      : super(
            name: superObj.name,
            id: superObj.id,
            retailer: superObj.retailer,
            cost: superObj.cost,
            KGCo2: superObj.KGCo2,
            GP: superObj.GP);

  factory SaleModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return SaleModel.fromSuper(
        ItemModel.fromJson(json),
        TSerializable.getJsonValue(json, 'greenPointsIssuedForItem',
            GreenPointsPaymentModel.fromJson));
  }

  @override
  Map<String, dynamic> toJson() => super.toJson()
    ..addAll(<String, dynamic>{
      'greenPointsIssuedForItem': greenPointsIssuedForItem.toJson()
    });
}

class PurchaseModel extends ItemModel {
  final CostModel totalGasBoughtWithMoney;
  final CoinModel totalGasUsed;

  PurchaseModel(
      {required String name,
      String id = '',
      required retailer,
      required cost,
      required KGCo2,
      required GP,
      required this.totalGasUsed,
      required this.totalGasBoughtWithMoney})
      : super(
            name: name,
            id: id,
            retailer: retailer,
            cost: cost,
            KGCo2: KGCo2,
            GP: GP);

  PurchaseModel.fromSuper(
      ItemModel superObj, this.totalGasBoughtWithMoney, this.totalGasUsed)
      : super(
            name: superObj.name,
            id: superObj.id,
            retailer: superObj.retailer,
            cost: superObj.cost,
            KGCo2: superObj.KGCo2,
            GP: superObj.GP);

  factory PurchaseModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return PurchaseModel.fromSuper(
        ItemModel.fromJson(json),
        TSerializable.getJsonValue(
            json, 'totalGasBoughtWithMoney', CostModel.fromJson),
        TSerializable.getJsonValue(json, 'totalGasUsed', CoinModel.fromJson));
  }

  @override
  Map<String, dynamic> toJson() => super.toJson()
    ..addAll(<String, dynamic>{
      'totalGasBoughtWithMoney': totalGasBoughtWithMoney.toJson(),
      'totalGasUsed': totalGasUsed.toJson()
    });
}

class SalesAggregationModel extends TSerializable {
  final Map<String, CostModel> totalCostByCcy;
  final Map<String, CostModel> totalMoneySentByCcy;
  final double totalGPIssued;
  final int numItemsIssued;
  final Map<String, int> itemCountMap;

  SalesAggregationModel({
    required this.totalCostByCcy,
    required this.totalMoneySentByCcy,
    required this.totalGPIssued,
    required this.numItemsIssued,
    required this.itemCountMap,
  }) : super();

  factory SalesAggregationModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return SalesAggregationModel(
      totalCostByCcy: TSerializable.getJsonMapValue(
          json, 'totalCostByCcy', CostModel.fromJson,
          defaultVal: <String, CostModel>{}),
      totalMoneySentByCcy: TSerializable.getJsonMapValue(
          json, 'totalMoneySentByCcy', CostModel.fromJson,
          defaultVal: <String, CostModel>{}),
      totalGPIssued:
          TSerializable.getJsonValTypeValue<double>(json, 'totalGPIssued'),
      numItemsIssued: TSerializable.getJsonValTypeValue<int>(
          json, 'numItemsIssued',
          defaultVal: 0),
      itemCountMap: TSerializable.getJsonMapValTypeValue<int>(
          json, 'itemCountMap',
          defaultVal: <String, int>{}),
    );
  }

  @override
  Map<String, dynamic> toJson() => <String, dynamic>{
        'totalCostByCcy':
            totalCostByCcy.map((key, value) => MapEntry(key, value.toJson())),
        'totalMoneySentByCcy': totalMoneySentByCcy
            .map((key, value) => MapEntry(key, value.toJson())),
        'totalGPIssued': totalGPIssued,
        'numItemsIssued': numItemsIssued,
        'itemCountMap': itemCountMap
      };
}

class TransactionModel extends TSerializable {
  final String id;
  final BankAccountModelLight accountFrom;
  final BankAccountModelLight accountTo;
  final CostModel money;
  final EtherPaymentModel ether;
  final GreenPointsPaymentModel greenPoints;

  TransactionModel({
    required this.accountFrom,
    required this.accountTo,
    this.id = '',
    required this.money,
    required this.ether,
    required this.greenPoints,
  }) : super();

  factory TransactionModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return TransactionModel(
      accountFrom: TSerializable.getJsonValue(
          json, 'accountFrom', BankAccountModelLight.fromJson),
      accountTo: TSerializable.getJsonValue(
          json, 'accountTo', BankAccountModelLight.fromJson),
      id: TSerializable.getJsonValTypeValue<String>(json, 'id', defaultVal: ''),
      money: TSerializable.getJsonValue(json, 'money', CostModel.fromJson),
      ether:
          TSerializable.getJsonValue(json, 'ether', EtherPaymentModel.fromJson),
      greenPoints: TSerializable.getJsonValue(
          json, 'greenPoints', GreenPointsPaymentModel.fromJson),
    );
  }

  @override
  Map<String, dynamic> toJson() => <String, dynamic>{
        'accountFrom': accountFrom.toJson(),
        'accountTo': accountTo.toJson(),
        'id': id,
        'money': money.toJson(),
        'ether': ether.toJson(),
        'greenPoints': greenPoints.toJson(),
      };
}

class TransitionJourney {
  TransitionJourney({
    required this.start,
    required this.end,
  });

  Alignment start;
  Alignment end;
}

class AlignedEntity {
  AlignedEntity({
    required this.entity,
    required this.alignment,
  });

  Alignment alignment;
  EntityModel entity;
}

class RunSimulationResponseModel extends TSerializable {
  final int status;
  final String message;
  final String taskId;
  final String simulationId;
  final String simulationType;
  final LoadSimulationDataEnvResult simulationData;

  RunSimulationResponseModel({
    required this.status,
    required this.message,
    required this.taskId,
    required this.simulationId,
    required this.simulationType,
    required this.simulationData,
  }) : super();

  factory RunSimulationResponseModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return RunSimulationResponseModel(
      status: TSerializable.getJsonValTypeValue<int>(
        json,
        'status',
      ),
      message: TSerializable.getJsonValTypeValue<String>(
        json,
        'message',
      ),
      taskId: TSerializable.getJsonValTypeValue<String>(
        json,
        'task_id',
      ),
      simulationId: TSerializable.getJsonValTypeValue<String>(
        json,
        'simulation_id',
      ),
      simulationType: TSerializable.getJsonValTypeValue<String>(
        json,
        'simulation_type',
      ),
      simulationData: TSerializable.getJsonValue(
          json, 'simulation_data', LoadSimulationDataEnvResult.fromJson),
    );
  }

  @override
  Map<String, dynamic> toJson() => <String, dynamic>{
        'status': status,
        'message': message,
        'task_id': taskId,
        'simulation_id': simulationId,
        'simulation_type': simulationType,
        'simulation_data': simulationData.toJson(),
      };
}

class PandasDF {
  PandasDF.fromJson(dynamic data) {
    dynamic dataMap;
    assert(data != null);
    if (data is String) {
      dataMap = jsonDecode(data);
    }
    //TODO: parse the df json
    throw UnimplementedError('Implement PandasDF.fromJson()');
  }
}

class SimulationComparisonHistory extends TSerializable {
  @override
  Map<String, dynamic> toJson() {
    // TODO: implement toJson
    throw UnimplementedError();
  }
}

class AppTransactionsStateModel extends TSerializable {
  final Map<String, List<TransactionModel>> transactionsByEntityId;

  AppTransactionsStateModel({
    required this.transactionsByEntityId,
  }) : super();

  factory AppTransactionsStateModel.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return AppTransactionsStateModel(
      transactionsByEntityId: TSerializable.getJsonMapListValue(
          json, 'transactionsByEntityId', TransactionModel.fromJson,
          defaultVal: <String, List<TransactionModel>>{}),
    );
  }

  @override
  Map<String, dynamic> toJson() => <String, dynamic>{
        'transactionsByEntityId': transactionsByEntityId.map((key, value) =>
            MapEntry(key, value.map((t) => t.toJson()).toList())),
      };
}

class AggregatedRetailers extends TSerializable {
  final BankAccountViewModel balance;
  final CostModel balanceMoney;
  final List<SaleModel> salesHistory;
  final SalesAggregationModel totalSales;

  final List<String> retailerNames;

  String get combinedNames => retailerNames.join(', ');

  AggregatedRetailers(
      {required this.balance,
      required this.balanceMoney,
      required this.salesHistory,
      required this.totalSales,
      this.retailerNames = const <String>['']});

  static AggregatedRetailers zero() => AggregatedRetailers(
      balance: BankAccountViewModel.dummy(),
      balanceMoney: CostModel(0.0, 'GBP'),
      salesHistory: <SaleModel>[],
      totalSales: SalesAggregationModel(
        totalCostByCcy: {},
        totalMoneySentByCcy: {},
        totalGPIssued: 0.0,
        numItemsIssued: 0,
        itemCountMap: {},
      ));

  factory AggregatedRetailers.fromJson(
      Map<String, dynamic> json, List<String> retailerNames) {
    return AggregatedRetailers(
      balance: TSerializable.getJsonValueFromChain(
          json, ['balance'], BankAccountViewModel.fromJson),
      balanceMoney: TSerializable.getJsonValueFromChain(
          json, ['balanceMoney'], CostModel.fromJson),
      salesHistory: TSerializable.getJsonListValueFromChain(
          json, ['salesHistory'], SaleModel.fromJson),
      totalSales: TSerializable.getJsonValueFromChain(
          json, ['totalSales'], SalesAggregationModel.fromJson),
      retailerNames: retailerNames,
    );
  }

  // @override
  Map<String, dynamic> toJson() => <String, dynamic>{
        'balance': balance.toJson(),
        'balanceMoney': balanceMoney.toJson(),
        'salesHistory': salesHistory.map((sh) => sh.toJson()).toList(),
        'totalSales': totalSales.toJson(),
      };
}

class LoadSimulationDataEnvResult extends TSerializable {
  final LoadEntitiesResult entities;
  final GemberAppConfig simulationConfig;

  LoadSimulationDataEnvResult({
    required this.entities,
    required this.simulationConfig,
  }) : super();

  factory LoadSimulationDataEnvResult.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return LoadSimulationDataEnvResult(
      entities: LoadEntitiesResult.fromJson(json),
      simulationConfig: GemberAppConfig.fromJson(json),
    );
  }

  @override
  Map<String, dynamic> toJson() => <String, dynamic>{
        ...entities.toJson(),
        ...simulationConfig.toJson(),
      };
}

class LoadEntitiesResult {
  final List<RetailerModel> retailers;
  final List<CustomerModel> customers;
  final AggregatedRetailers retailersCluster;
  // final int basketFullSize;
  // final int numShopTrips;

  LoadEntitiesResult({
    required this.retailers,
    required this.customers,
    required this.retailersCluster,
    // required this.basketFullSize,
    // required this.numShopTrips,
  });

  factory LoadEntitiesResult.emptyInit() {
    return LoadEntitiesResult(
      customers: <CustomerModel>[],
      retailers: <RetailerModel>[],
      retailersCluster: AggregatedRetailers.zero(),
      // basketFullSize: 1,
      // numShopTrips: 1,
    );
  }

  bool get isEmpty => retailers.isEmpty && customers.isEmpty;

  bool get isNotEmpty => !isEmpty;

  factory LoadEntitiesResult.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    final _ret = TSerializable.getJsonMapValue(
        json, 'retailers', RetailerModel.fromJson);
    return LoadEntitiesResult(
      customers: TSerializable.getJsonMapValue(
              json, 'customers', CustomerModel.fromJson)
          .values
          .toList(),
      retailers: _ret.values.toList(),
      retailersCluster: TSerializable.getJsonValue<AggregatedRetailers>(
          json,
          'retailersCluster',
          (Map<String, dynamic> json, {bool shouldThrow = true}) =>
              AggregatedRetailers.fromJson(json, _ret.keys.toList())),
    );
  }

  @override
  Map<String, dynamic> toJson() => <String, dynamic>{
        'customers': customers.map((ent) => ent.toJson()).toList(),
        'retailers': retailers.map((ent) => ent.toJson()).toList(),
        'retailersCluster': retailersCluster.toJson(),
      };
}

class LoadTransactionsForEntityResult {
  final List<TransactionModel> transactionsFromEntity;
  final List<TransactionModel> transactionsToEntity;

  LoadTransactionsForEntityResult(
      {required this.transactionsFromEntity,
      required this.transactionsToEntity});

  bool get isEmpty =>
      transactionsFromEntity.isEmpty && transactionsToEntity.isEmpty;

  bool get isNotEmpty => !isEmpty;
}

class LoadSalesForItem {
  final List<SaleModel> salesForItem;

  LoadSalesForItem({required this.salesForItem});

  bool get isEmpty => salesForItem.isEmpty;

  bool get isNotEmpty => !isEmpty;
}

class SimulationProgressData {
  SimulationProgressData({required dynamic data})
      : runningSum = TSerializable.getJsonValue(
            data, "running_sum", SimulationProgressDataSeries.fromJson),
        runningAverage = TSerializable.getJsonValue(
            data, "running_average", SimulationProgressDataSeries.fromJson),
        runningVariance = TSerializable.getJsonValue(
            data, "running_variance", SimulationProgressDataSeries.fromJson),
        iterationNumber =
            TSerializable.getJsonValTypeValue<int>(data, "iteration_number"),
        maxNIterations =
            TSerializable.getJsonValTypeValue<int>(data, "maxNIterations"),
        simConfig = GemberAppConfig.fromJson(data);

  final SimulationProgressDataSeries runningSum;
  final SimulationProgressDataSeries runningAverage;
  final SimulationProgressDataSeries runningVariance;
  final int iterationNumber;
  final int maxNIterations;
  final GemberAppConfig simConfig;
}

class SimulationResult extends SimulationProgressDataSeries {
  final String simulationId;
  final double startedAt;

  SimulationResult({
    required salesCount,
    required greenPointsIssued,
    required marketShare,
    required totalSalesRevenue,
    required totalSalesRevenueLessGP,
    required this.simulationId,
    required this.startedAt,
  }) : super(
          salesCount: salesCount,
          greenPointsIssued: greenPointsIssued,
          marketShare: marketShare,
          totalSalesRevenue: totalSalesRevenue,
          totalSalesRevenueLessGP: totalSalesRevenueLessGP,
        );

  SimulationResult.fromSuper(
      SimulationProgressDataSeries superObj, this.simulationId, this.startedAt)
      : super(
          salesCount: superObj.salesCount,
          greenPointsIssued: superObj.greenPointsIssued,
          marketShare: superObj.marketShare,
          totalSalesRevenue: superObj.totalSalesRevenue,
          totalSalesRevenueLessGP: superObj.totalSalesRevenueLessGP,
        );

  factory SimulationResult.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return SimulationResult.fromSuper(
      SimulationProgressDataSeries.fromJson(json),
      TSerializable.getJsonValTypeValue<String>(json, 'simulation_id'),
      TSerializable.getJsonValTypeValue<double>(json, 'started_at'),
    );
  }

  Map<String, dynamic> toJson() => <String, dynamic>{
        ...super.toJson(),
        'simulation_id': simulationId,
        'started_at': startedAt,
      };
}

class SimulationProgressDataSeries extends TSerializable {
  final Map<String, num> salesCount;
  final Map<String, num> greenPointsIssued;
  final Map<String, num> marketShare;
  final Map<String, num> totalSalesRevenue;
  final Map<String, num> totalSalesRevenueLessGP;
  // final Map<String, Map<String,num>> totalSalesRevenueByItem;

  SimulationProgressDataSeries({
    required this.salesCount,
    required this.greenPointsIssued,
    required this.marketShare,
    required this.totalSalesRevenue,
    required this.totalSalesRevenueLessGP,
  }) : super();

  factory SimulationProgressDataSeries.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return SimulationProgressDataSeries(
      salesCount: TSerializable.getJsonMapValTypeValue<num>(
        json,
        'sales_count',
      ),
      greenPointsIssued: TSerializable.getJsonMapValTypeValue<num>(
        json,
        'green_points_issued',
      ),
      marketShare: TSerializable.getJsonMapValTypeValue<num>(
        json,
        'market_share',
      ),
      totalSalesRevenue: TSerializable.getJsonMapValTypeValue<num>(
        json,
        'total_sales_revenue',
      ),
      totalSalesRevenueLessGP: TSerializable.getJsonMapValTypeValue<num>(
        json,
        'total_sales_revenue_less_gp',
      ),
    );
  }

  @override
  Map<String, dynamic> toJson() => <String, dynamic>{
        'sales_count': salesCount,
        'green_points_issued': greenPointsIssued,
        'market_share': marketShare,
        'total_sales_revenue': totalSalesRevenue,
        'total_sales_revenue_less_gp': totalSalesRevenueLessGP,
      };
}

class SimulationScenarioRef {
  String? implementFields;
}

class SingleIterationFinishedRef {
  String? implementFields;
}

class GemberAppConfig extends TSerializable {
  GemberAppConfig({
    required this.BASKET_FULL_SIZE,
    required this.NUM_SHOP_TRIPS_PER_ITERATION,
    required this.NUM_CUSTOMERS,
    this.maxN = 1,
    this.convergenceTH = 0.0,
    this.strategy = 0.0,
    this.sustainabilityBaseline = 0.0,
    this.controlRetailerName,
  }) : super();

  factory GemberAppConfig.fromJson(Map<String, dynamic> json,
      {bool shouldThrow = true}) {
    return GemberAppConfig(
      BASKET_FULL_SIZE: TSerializable.getJsonValTypeValue<int>(
        json,
        'BASKET_FULL_SIZE',
      ),
      NUM_SHOP_TRIPS_PER_ITERATION: TSerializable.getJsonValTypeValue<int>(
        json,
        'NUM_SHOP_TRIPS_PER_ITERATION',
      ),
      NUM_CUSTOMERS: TSerializable.getJsonValTypeValue<int>(
        json,
        'NUM_CUSTOMERS',
      ),
      maxN: TSerializable.getJsonValTypeValue<int>(
        json,
        'maxN',
      ),
      convergenceTH: TSerializable.getJsonValTypeValue<double>(
        json,
        'convergenceTH',
      ),
      strategy: TSerializable.getJsonValTypeValue<double>(
        json,
        'strategy',
      ),
      sustainabilityBaseline: TSerializable.getJsonValTypeValue<double>(
        json,
        'sustainability',
      ),
      controlRetailerName: TSerializable.getJsonValTypeValue<String?>(
        json,
        'controlRetailerName',
      ),
    );
  }

  final int BASKET_FULL_SIZE;
  final int NUM_SHOP_TRIPS_PER_ITERATION;
  final int NUM_CUSTOMERS;
  final int maxN;
  final double convergenceTH;
  final double strategy;
  final double sustainabilityBaseline;
  final String? controlRetailerName;

  @override
  Map<String, dynamic> toJson() => <String, dynamic>{
        'BASKET_FULL_SIZE': BASKET_FULL_SIZE,
        'NUM_SHOP_TRIPS_PER_ITERATION': NUM_SHOP_TRIPS_PER_ITERATION,
        'NUM_CUSTOMERS': NUM_CUSTOMERS,
        'maxN': maxN,
        'convergenceTH': convergenceTH,
        'strategy': strategy,
        'sustainability': sustainabilityBaseline,
        'controlRetailerName': controlRetailerName,
      };

  Map<String, String> toStrJson() => Map<String, String>.fromEntries(
      toJson().entries.map((e) => MapEntry(e.key, e.value.toString())));

  @override
  String toString() {
    return 'N=$maxN;a=$convergenceTH;cust=$controlRetailerName;strat=$strategy;sust=$sustainabilityBaseline;numCust=$NUM_CUSTOMERS;';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;

    return other is GemberAppConfig &&
        other.BASKET_FULL_SIZE == BASKET_FULL_SIZE &&
        other.NUM_SHOP_TRIPS_PER_ITERATION == NUM_SHOP_TRIPS_PER_ITERATION &&
        other.NUM_CUSTOMERS == NUM_CUSTOMERS &&
        other.maxN == maxN &&
        other.convergenceTH == convergenceTH &&
        other.strategy == strategy &&
        other.controlRetailerName == controlRetailerName &&
        other.sustainabilityBaseline == sustainabilityBaseline;
  }

  @override
  int get hashCode {
    return BASKET_FULL_SIZE.hashCode ^
        NUM_SHOP_TRIPS_PER_ITERATION.hashCode ^
        NUM_CUSTOMERS.hashCode ^
        maxN.hashCode ^
        convergenceTH.hashCode ^
        strategy.hashCode ^
        sustainabilityBaseline.hashCode ^
        controlRetailerName.hashCode;
  }
}
