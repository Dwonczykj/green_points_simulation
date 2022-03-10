from __future__ import annotations
import pandas as pd

from Bank import Customer, GPStrategyMultiplier, Retailer, RetailerSustainabilityIntercept

class SimStamp:
    def __init__(self, id: str, timestamp: float) -> None:
        self.id = id
        self.timestamp = timestamp


class EntityInitialiser:
    # Declare Simulation Constants
    BASKET_FULL_SIZE = 1
    NUM_SHOP_TRIPS_PER_ITERATION = 1
    NUM_CUSTOMERS = 4

    def __init__(self, df: pd.DataFrame):
        self._df = df

        _retailerNames = [str(r).replace(' Sells', '')
                          for r in df.columns if str(r).endswith('Sells')]

        self._retailers = {r: Retailer(name=r,
                                       strategy=GPStrategyMultiplier.COMPETITIVE,
                                       sustainability=RetailerSustainabilityIntercept.AVERAGE,
                                       greenPointFiatValue=0.01)
                           for r in _retailerNames}

        # Opt out VW for now
        self._retailers['VW'].strategy = GPStrategyMultiplier.ZERO

        # Declare Customers
        self._customers: list[Customer] = [
            Customer(f'Customer[{i}]') for i in range(EntityInitialiser.NUM_CUSTOMERS)]

    @property
    def initialDataSet(self):
        return self._df.copy()

    @property
    def retailerNames(self):
        return list(self._retailers.keys())

    @property
    def retailers(self):
        return self._retailers

    @property
    def customers(self):
        return self._customers


# Declare Simulation Constants
BASKET_IS_FULL_SIZE = EntityInitialiser.BASKET_FULL_SIZE
NUM_SHOP_TRIPS_PER_ITERATION = EntityInitialiser.NUM_SHOP_TRIPS_PER_ITERATION
NUM_CUSTOMERS = EntityInitialiser.NUM_CUSTOMERS


class TweakRetailerStrategy:
    def __init__(self, retailerName: str, strategy: GPStrategyMultiplier, sustainability: RetailerSustainabilityIntercept) -> None:
        self.retailerName = retailerName
        self.strategy = strategy
        self.sustainability = sustainability

    def validate(self, validRetailers: dict[str, Retailer]):
        return bool(self.retailerName in validRetailers.keys())
