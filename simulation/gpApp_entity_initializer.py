from __future__ import annotations
import pandas as pd
# from app_config import AppConfig

from Bank import RetailerStrategyGPMultiplier, Retailer, RetailerSustainabilityIntercept

class SimStamp:
    def __init__(self, id: str, timestamp: float) -> None:
        self.id = id
        self.timestamp = timestamp


class EntityInitialiser:
    
    def __init__(self, df: pd.DataFrame):
        self._df = df

        _retailerNames = [str(r).replace(' Sells', '')
                          for r in df.columns if str(r).endswith('Sells')]

        self._retailers = {r: Retailer(name=r,
                                       strategy=RetailerStrategyGPMultiplier.COMPETITIVE,
                                       sustainability=RetailerSustainabilityIntercept.AVERAGE,
                                       greenPointFiatValue=0.01)
                           for r in _retailerNames}

        # Opt out VW for now
        self._retailers['VW'].strategy = RetailerStrategyGPMultiplier.ZERO

        # Declare Customers
        # self._customers: list[Customer] = [
        #     Customer(f'Customer[{i}]') for i in range(AppConfig.NUM_CUSTOMERS)]

    @property
    def initialDataSet(self):
        return self._df.copy()

    @property
    def retailerNames(self):
        return list(self._retailers.keys())

    @property
    def retailers(self):
        return self._retailers

    # @property
    # def customers(self):
    #     return self._customers
