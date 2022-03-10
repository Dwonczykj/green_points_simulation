from __future__ import annotations
import abc
from typing import TYPE_CHECKING
from datetime import datetime, timezone

from Coin import EtherCoin, Money
from Identifiable import Identifiable

if TYPE_CHECKING:
    from Bank import Bank, BankAccount, GreenPointTokensView




class Transfer(Identifiable):
    def __init__(self, fromObj:Identifiable, toObj:Identifiable) -> None:
        assert isinstance(fromObj,Identifiable) and isinstance(toObj,Identifiable), TypeError('Transfers must occur between Identifiable objects')
        super().__init__()
        self.fromObj = fromObj
        self.toObj = toObj
        self.__timestamp = datetime.now(tz=timezone.utc).timestamp()
        #TODO LATER: Add probability small that Transfer fails and has to be redone, but to this on the Transaction line not the transfer line
        self.success = True
    
    @property  
    def timestamp(self):
        return self.__timestamp
    
    @property
    def atDatetime(self):
        return datetime.fromtimestamp( self.__timestamp, tz=timezone.utc )
    
    @property
    def atDatetimeStr(self):
        return datetime.strftime(self.atDatetime,'%Y-%m-%d %H:%M:%s')
    
    @abc.abstractmethod
    def __str__(self):
        return f'Transfer ({self.atDatetimeStr}) between {self.fromObj.id} and {self.toObj.id}'

    @abc.abstractmethod
    def __repr__(self):
        pass
    
        
        
class MoneyTransfer(Transfer):
    def __init__(self, fromObj: Identifiable, toObj: Identifiable, amount:Money) -> None:
        super().__init__(fromObj, toObj)
        assert isinstance(amount,Money), TypeError('amount must be Money')
        self.amount = amount
        
    def __str__(self):
        return f'Transfer ({self.atDatetimeStr}) between {self.fromObj.id} and {self.toObj.id} for {self.amount}'

    def __repr__(self):
        return str(type(self)) + f'[{self.amount}]'
    
class EtherTransfer(Transfer):
    def __init__(self, fromObj: Identifiable, toObj: Identifiable, amount:EtherCoin) -> None:
        super().__init__(fromObj, toObj)
        assert isinstance(amount,EtherCoin), TypeError('amount must be EtherCoin')
        self.amount = amount
        # self.gas = gas
        
    def __str__(self):
        return f'Transfer ({self.atDatetimeStr}) between {self.fromObj.id} and {self.toObj.id} for {self.amount}'

    def __repr__(self):
        return str(type(self)) + f'[{self.amount}]'
    
class GreenPointTransfer(Transfer):
    def __init__(self, fromObj: Identifiable, toObj: Identifiable, amount:GreenPointTokensView) -> None:
        super().__init__(fromObj, toObj)
        from Bank import GreenPointTokensView
        assert isinstance(amount,GreenPointTokensView), TypeError('amount must be GreenPointTokensView')
        # assert isinstance(gas,EtherCoin), TypeError('amount must be EtherCoin')
        self.amount = amount
        # self.gas = gas
        
    def __str__(self):
        return f'Transfer ({self.atDatetimeStr}) between {self.fromObj.id} and {self.toObj.id} for {self.amount}'

    def __repr__(self):
        return str(type(self)) + f'[{self.amount}]'
    
class FXTransfer(Transfer):
    def __init__(self, forAccount: BankAccount, usingBank: Bank, amount:Money, bankCharge:Money, toCurrency:str) -> None:
        super().__init__(forAccount, forAccount)
        self.forAccount=forAccount
        self.usingBank=usingBank
        self.amount=amount
        self.bankCharge=bankCharge
        self.fromCurrency=amount.currency
        self.toCurrency=toCurrency
        
    def __str__(self):
        return f'FX Transaction ({self.atDatetimeStr}) for {self.forAccount} using bank {self.usingBank} for {self.amount} to {self.toCurrency} with bank charge: {self.bankCharge}'

    def __repr__(self):
        return str(type(self)) + f'[{self.fromCurrency}{self.toCurrency}]({self.amount})'
    
    def toDict(self):
        return {
            'forAccount': self.forAccount.id,
            'usingBank': self.usingBank.id,
            'AmountMonetary Amount': self.amount.amount,
            'AmountMonetary Currency': self.amount.currency,
            'BankCharge Amount': self.bankCharge.amount,
            'BankCharge Currency': self.bankCharge.currency,
            'ToCurrency': self.toCurrency,
            'Timestamp': self.atDatetimeStr
        }
    

class FailedTransfer(Transfer):
    def __init__(self, accountFrom:Identifiable, accountTo:Identifiable):
        super().__init__(accountFrom, accountTo)
        self.success = False