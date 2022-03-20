from __future__ import annotations
from ISerializable import TSERIALIZABLE_ALIAS, TSTRUC_ALIAS, ISerializable
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Bank import Bank

from Multipliable import Divideable, Multipliable


class Money(Divideable, ISerializable):
    def __init__(self, amount:float, currency:str='GBP') -> None:
        super().__init__(amount=amount)
        self._currency = currency
        self._amount = amount
        
    def _copyFromMultipliable(self, multi: Multipliable) -> Money:
        return Money(multi.amount, self.currency)
    
    def copy(self):
        return Money(self.amount, self.currency)
    
    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            "amount": self.amount,
            "currency": self.currency
        }
        
    def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
        return super().toDictLight()
    
    def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
        return super().toDictUI()
    
    def inCcy(self, viewInCurrency:str, throughBank:Bank):
        return throughBank.FXPeek(fxFrom=self, fxToCurrency=viewInCurrency)
    
    
    # def exchange(self, fromAccount:BankAccount, throughBank:Bank, toCurrency:str):
    #     return throughBank.exchange(caller=fromAccount, 
    #                                 money=self, 
    #                                 toCurrency=toCurrency)
    
    def _assertOtherArgIsOperatable(self, other:(Money|float|int)):
        if isinstance(other,Money):
            assert other.currency == self.currency, f'Moneys must have same currencies for operations: [self={self.currency}, other={other.currency}]'
        elif isinstance(other,float) or isinstance(other,int):
            pass
        else:
            raise ValueError('other must be an operable type for Money operations')
                
    
    def _getCurrency(self):
        return self._currency
    
    currency:str = property(_getCurrency) #type: ignore 
    
    def __eq__(self, __o: object) -> bool:
        return bool(isinstance(__o, Money) and self.amount == __o.amount and self.currency == __o.currency)
    
    def __str__(self):
        return str(type(self).__name__) + f'[{self.currency} {self.amount}]'
    
    def __repr__(self):
        return str(type(self).__name__) + f'[{self.currency} {self.amount}]'
    
    
class EtherCoin(Divideable):
    def __init__(self, amount: float) -> None:
        super().__init__(amount)
        
    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            "amount": self.amount
        }
        
    def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
        return self.toDict()
        
    def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
        return self.toDict()
        
    def take(self, amount:float):
        assert amount <= self.amount, 'Cannot take more than the existing amount of EtherCoin'
        return EtherCoin(amount=amount)
        
    def _copyFromMultipliable(self, multi: Multipliable) -> EtherCoin:
        return EtherCoin(amount=multi.amount)
    
    def _assertOtherArgIsOperatable(self, other:(EtherCoin|float|int)):
        if isinstance(other,EtherCoin):
            pass
        elif isinstance(other,float) or isinstance(other,int):
            pass
        else:
            raise ValueError('other must be an operable type for EtherCoin operations')
        
    def __str__(self):
        return str(type(self).__name__) + f'[{self.amount}]'
    
    def __repr__(self):
        return str(type(self).__name__) + f'[{self.amount}]'