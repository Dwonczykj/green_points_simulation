from __future__ import annotations


    
class ChainLinkDummyDataFeed:
    def __init__(self) -> None:
        self._permittedCurrencies = [
            'GBP',
            'USD'
        ]
        
    def getEtherToCurrencyRate(self, toCurrency:str):
        '''Get value of 1 Ether in Unit of Currency: i.e. ETHUSD ~= USD 2430.13, if USDGBP = 0.738 -> ETHGBP ~= 1793.44'''
        if toCurrency not in self._permittedCurrencies:
            raise ValueError('toCurrency must be in ChainLink DataFeed permitted Currencies.')
        if toCurrency == 'GBP':
            return 1793.44
        elif toCurrency == 'USD':
            return 2430.13
    
    def canGetEtherToCurrencyRate(self, toCurrency:str):
        return bool(toCurrency in self._permittedCurrencies)