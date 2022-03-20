from __future__ import annotations

from collections import defaultdict
from functools import reduce
import uuid
import enum
import abc
from typing import Tuple, Any, Callable, Literal, Iterable, DefaultDict, TypeVar
from typing_extensions import Self
from collections import defaultdict
from enums import *
import numpy as np
import logging

from Coin import Money, EtherCoin
from Identifiable import Identifiable
from ISerializable import TSERIALIZABLE_ALIAS, TSTRUC_ALIAS, ISerializable, ISerializableBasic
from InsufficientCoinError import CheckSameTypeError, GreenPointsLostInDoubleBookingTransactionException, DoubleBookingTransactionMisMatchException, InsufficientEtherError, InsufficientGreenPointsError, InsufficientMoneyError, BankTransactionFailedError, NotAllowedError, PurchaseItemTransactionError
from Institution import Institution
from Multipliable import Numeric
from Observer import Observable, Observer
from Transfer import GreenPointTransfer, MoneyTransfer, Transfer
from ChainLinkDummyDataFeed import ChainLinkDummyDataFeed

        

_RT = TypeVar('_RT')
def tryInline(func:Callable[[],_RT]) -> _RT | None:
    try:
        x = func()
    except:
        x = None
    return x


def isnum(o:Any):
    try:
        x = int(o)
        return True
    except:
        return False


debug = False

class MetaPeggedToken(type):
    __peggedCurrency:Literal['GBP'] = 'GBP'

    @property
    def peggedCurrency(self):
        return self.__peggedCurrency
    
    __tokenValueInPeggedCurrency = 0.01
    
    @property
    def tokenValueInPeggedCurrency(self):
        return GreenPointTokens.__tokenValueInPeggedCurrency
    
    
    
    
class GreenPointTokens(metaclass=MetaPeggedToken):
    '''GreenPoint Tokens are pegged to Fiat Currency: GBP'''
    __metaclass__=MetaPeggedToken
    
    
    def __init__(self, amount:float, callerSecret:str):
        #TODO LATER: Add unit test to confirm that this fails unless the house calls the constructor.
        if amount < 0.0:
            raise ValueError('Cannot have a negative holding of GreenPointTokens')            
        self.__house = GreenPointsHouse.getInstance()
        if amount != 0.0:
            assert self.__house.checkCallFromHouse(callerSecret), 'Only the House can mint GreenPointTokens'
        self.__secret__ = callerSecret
        self.__amount = amount
        
    
    @property
    def amount(self):
        return self.__amount
    
    @property
    def valueInPeggedCurrency(self):
        return Money(amount=self.amount * GreenPointTokens.tokenValueInPeggedCurrency, currency=GreenPointTokens.peggedCurrency)
    
    def toDict(self):
        return {
            "amount": self.amount
        }
    
    def __add__(self, other:(Self|Numeric)):
        assert isinstance(other,type(self))
        return GreenPointTokens(amount=(self.amount + other.amount), callerSecret=self.__secret__)
        
    def __sub__(self, other:(Self|Numeric)):
        assert isinstance(other,type(self))
        return GreenPointTokens(amount=(self.amount - other.amount), callerSecret=self.__secret__)
    
        
    # def __neg__(self):
    #     return GreenPointTokens(amount=(-self.amount), callerSecret=self.__secret__)
    
    # def __mul__(self, other:(Self|Numeric)):
    #     assert isinstance(other,float) and other >= 0.0 and other <= 1.0
    #     if other == 1.0:
    #         return self
    #     else:
    #         return GreenPointTokens(amount=(self.amount * other), callerSecret=self.__secret__)
        
    def split(self, proportions:Iterable[float]):
        if proportions is None or proportions == 1:
            return [self]
        elif isinstance(proportions, float):
            assert proportions >= 0.0 and proportions <= 1, 'proportions must be in range [0,1]'
            return [GreenPointTokens(amount=(self.amount * proportions), callerSecret=self.__secret__), 
                    GreenPointTokens(amount=(self.amount * (1.0 - proportions)), callerSecret=self.__secret__)]
        elif isinstance(proportions,Iterable): 
            assert all((i <= 1.0 and i >= 0.0 for i in proportions)), 'proportions must be in range [0,1]'
            assert sum(proportions) <= 1.0, 'propotions cant sum > 1'
            if sum(proportions) < 1.0:
                return [*[GreenPointTokens(amount=(self.amount * p), callerSecret=self.__secret__) for p in proportions], 
                        GreenPointTokens(amount=(self.amount * (1.0-sum(proportions))), callerSecret=self.__secret__)]
            elif sum(proportions) == 1:
                return [GreenPointTokens(amount=(self.amount * p), callerSecret=self.__secret__) for p in proportions]
            else:
                return []
        else:
            return []
    
    def __radd__(self, other:(Self|Numeric)):
        return other + self
    
    def __rsub__(self, other:(Self|Numeric)):
        assert isinstance(other,type(self))
        return GreenPointTokens(amount=(other.amount - self.amount), callerSecret=self.__secret__)
    
    def __iadd__(self, other:(Self|Numeric)):
        return self + other
    
    def __isub__(self, other:(Self|Numeric)):
        return self - other
    
    def __le__(self, other:(Self|Numeric)):
        if isinstance(other,type(self)):
            return self.amount <= other.amount
        else:
            return self.amount <= other
    
    def __lt__(self, other:(Self|Numeric)):
        if isinstance(other,type(self)):
            return self.amount < other.amount
        else:
            return self.amount < other
        
    def __ge__(self, other:(Self|Numeric)):
        if isinstance(other,type(self)):
            return self.amount >= other.amount
        else:
            return self.amount >= other
        
    def __gt__(self, other:(Self|Numeric)):
        if isinstance(other,type(self)):
            return self.amount > other.amount
        else:
            return self.amount > other
        
    def __str__(self):
        return f'GPTknV_{self.amount}'
    
    def __repr__(self):
        return f'GPTknV_{self.amount}'


class GreenPointTokensView(ISerializable):
    def __init__(self, gp:(GreenPointTokens|Literal[0])) -> None:
        if gp == 0:
            self.__gp = GreenPointsHouse.getInstance().zeroTokenWrapper()
        else:
            assert gp is not None and isinstance(gp,GreenPointTokens)
            self.__gp = gp
    
    @property   
    def peggedCurrency(self) -> Literal['GBP']:
        return GreenPointTokens.peggedCurrency
    
    @property
    def amount(self):
        return self.__gp.amount
    
    @property
    def tokenValueInPeggedCurrency(self):
        return GreenPointTokens.tokenValueInPeggedCurrency
    
    @property
    def valueInPeggedCurrency(self):
        return Money(amount=self.amount * self.tokenValueInPeggedCurrency, currency=self.peggedCurrency)
    
    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            "amount": self.amount,
            "tokenValueInPeggedCurrency": self.tokenValueInPeggedCurrency,
            "valueInPeggedCurrency": self.valueInPeggedCurrency.toDict(),
            "peggedCurrency": self.peggedCurrency
        }
        
    def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            "amount": self.amount
        }
        
    def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            "amount": self.amount
        }
   
    def __add__(self, other:(Self|Numeric)):
        assert isinstance(other,type(self)) or isinstance(other,type(self.__gp))
        if isinstance(other,type(self)):
            return GreenPointTokensView(self.__gp + other.__gp)
        elif isinstance(other,type(self.__gp)):
            return GreenPointTokensView(self.__gp + other)
        else:
            return self
        
    def __sub__(self, other:(Self|Numeric)):
        assert isinstance(other,type(self)) or isinstance(other,type(self.__gp))
        if isinstance(other,type(self)):
            return GreenPointTokensView(self.__gp - other.__gp)
        elif isinstance(other,type(self.__gp)):
            return GreenPointTokensView(self.__gp - other)
        else:
            return self
        
    # def __mul__(self, other:(Self|Numeric)):
    #     assert isinstance(other,float), 'Can only multiply GreenPointTokensView by float'
    #     return GreenPointTokensView(self.__gp)
        
    # def __truediv__(self, other:(Self|Numeric)):
    #     assert isinstance(other,type(self)) or isinstance(other,type(self.__gp))
    #     if isinstance(other,type(self)):
    #         return GreenPointTokensView(self.__gp - other.__gp)
    #     elif isinstance(other,type(self.__gp)):
    #         return GreenPointTokensView(self.__gp - other)
    
    def split(self, proportions:Iterable[float]):
        tokens = self.__gp.split(proportions)
        if tokens is not None:
            return [GreenPointTokensView(gp=t) for t in tokens]
        else:
            return []
        # if proportions is None or proportions == 1:
        #     return [self]
        # elif isinstance(proportions, float):
        #     assert proportions >= 0.0 and proportions < 1, 'proportions must be in range [0,1)'
        #     return [GreenPointTokensView(gp=self.__gp * proportions), GreenPointTokensView(gp=self.__gp * (1.0 - proportions))]
        # elif isinstance(proportions,Iterable): 
        #     assert all((i < 1.0 and i >= 0.0 for i in proportions)), 'proportions must be in range [0,1)'
        #     assert sum(proportions) <= 1.0, 'propotions cant sum > 1'
        #     if sum(proportions) < 1.0:
        #         return [*[GreenPointTokensView(gp=self.__gp * p) for p in proportions], GreenPointTokensView(gp=self.__gp * (1.0-sum(proportions)))]
        #     elif sum(proportions) == 1:
        #         return [GreenPointTokensView(gp=self.__gp * p) for p in proportions]
                
    
    def __radd__(self, other:(Self|Numeric)):
        return self + other
    
    def __rsub__(self, other:(Self|Numeric)):
        assert isinstance(other,type(self)) or isinstance(other,type(self.__gp))
        if isinstance(other,type(self)):
            return GreenPointTokensView(other.__gp - self.__gp)
        elif isinstance(other,type(self.__gp)):
            return GreenPointTokensView(other - self.__gp)
    
    # def __rmul__(self, other:(Self|Numeric)):
    #     return other + self
    
    # def __rtruediv__(self, other:(Self|Numeric)):
    #     return other - self
    
    def __iadd__(self, other:(Self|Numeric)):
        return self + other
    
    def __isub__(self, other:(Self|Numeric)):
        return self - other
    
    
    def __le__(self, other:(Self|Numeric)):
        if isinstance(other,type(self)):
            return self.amount <= other.amount
        else:
            return self.amount <= other
    
    def __lt__(self, other:(Self|Numeric)):
        if isinstance(other,type(self)):
            return self.amount < other.amount
        else:
            return self.amount < other
        
    def __ge__(self, other:(Self|Numeric)):
        if isinstance(other,type(self)):
            return self.amount >= other.amount
        else:
            return self.amount >= other
        
    def __gt__(self, other:(Self|Numeric)):
        if isinstance(other,type(self)):
            return self.amount > other.amount
        else:
            return self.amount > other
    
    def __str__(self):
        return f'GPTknV_{self.amount}'
    
    def __repr__(self):
        return f'GPTknV_{self.amount}'          



class GreenPointsChain:
    '''Singleton: Call getInstance() to get'''
    __instance:GreenPointsChain|None=None
    
    @staticmethod 
    def getInstance(callerSecret:str, gpHouse:GreenPointsHouse):
        """ Static access method. """
        if GreenPointsChain.__instance == None:
            GreenPointsChain(callerSecret,gpHouse)
        assert isinstance(GreenPointsChain.__instance,GreenPointsChain)
        return GreenPointsChain.__instance
    
    def __init__(self, callerSecret:str, gpHouse:GreenPointsHouse):
        """ Virtually private constructor. """
        if GreenPointsChain.__instance != None:
            raise Exception(type(self).__name__ + " class is a singleton!")
        else:
            # gpHouse = GreenPointsHouse.getInstance()
            if gpHouse.checkCallFromHouse(callerSecret=callerSecret):
                GreenPointsChain.__instance = self
                self.__chainsecret__ = str(uuid.uuid4())
                self.__housesecret__ = callerSecret
                self.__house = gpHouse
                self._dataFeed = ChainLinkDummyDataFeed()
                self._walletBalances:dict[str,GreenPointsChain.Balance] = defaultdict(lambda : GreenPointsChain.Balance(self, ether=0.0, gpTokens=0.0))
                self._transactionHistory:list[GreenPointsChain.Transaction] = []
                self._usedGas:EtherCoin = EtherCoin(0)
                self.__holdingContainer = GreenPointsChain.Balance(self, ether=2.0**31, gpTokens=2.0**31)
            
    _GAS_AMOUNT_MINT_MULTI = 0.0001
    _GAS_AMOUNT_TRANSACTION_MULTI = 0.00001
    
    _GAS_AMOUNT_ETH_MINT_MULTI = 0.0001
    _GAS_AMOUNT_ETH_TRANSACTION_MULTI = 0.00001
    
    def checkCallFromChain(self, callerSecret:str):
        return callerSecret == self.__chainsecret__
    
    def assignHouseAccountBalance(self, id:str, callerSecret:str):
        if self.__house.checkCallFromHouse(callerSecret=callerSecret):
            self._walletBalances[id] = self.__holdingContainer
            
    def calculateGasFeesForTransferGP(self, amount:(GreenPointTokensView|GreenPointTokens|float)):
        return self._calculateGasFees(amountGreenTokens=amount, multiplier=GreenPointsChain._GAS_AMOUNT_TRANSACTION_MULTI)
        
    def calculateGasFeesForMintGP(self, amount:(GreenPointTokensView|GreenPointTokens|float)):
        return self._calculateGasFees(amountGreenTokens=amount, multiplier=GreenPointsChain._GAS_AMOUNT_MINT_MULTI)
            
    def _calculateGasFees(self, amountGreenTokens:(GreenPointTokensView|GreenPointTokens|float), multiplier:float):
        amountGPT = amountGreenTokens if isinstance(amountGreenTokens,float) else amountGreenTokens.amount
        if amountGPT <= 0:
            return EtherCoin(0.0)
        fx_ETHCCY = self._dataFeed.getEtherToCurrencyRate(GreenPointTokens.peggedCurrency)
        if not fx_ETHCCY:
            raise NotImplementedError(f'Have not implemented Currency conversion from Ether to {GreenPointTokens.peggedCurrency}')
        gpx_ETHGPT = fx_ETHCCY / GreenPointTokens.tokenValueInPeggedCurrency
        return EtherCoin(multiplier * (amountGPT) / gpx_ETHGPT)
    
    def calculateGasFeesForTransferEther(self, amount:(float)):
        return self._calculateGasFees(amountGreenTokens=amount, multiplier=GreenPointsChain._GAS_AMOUNT_ETH_TRANSACTION_MULTI)
    
    def calculateGasFeesForMintEther(self, amount:(float)):
        return self._calculateGasFees(amountGreenTokens=amount, multiplier=GreenPointsChain._GAS_AMOUNT_ETH_MINT_MULTI)
           
    def transferGP(self, walletFrom:CryptoWallet, walletTo:CryptoWallet, amount:float):
        return self._transferGP(walletFrom=walletFrom, walletTo=walletTo, amount=amount, isMint=False)
    
    def mintGP(self, walletTo:CryptoWallet, amount:float, callerSecret:str):
        walletFrom = self.__house.cryptoWallet
        if not self.__house.checkCallFromHouse(callerSecret=callerSecret):
            return
        return self._transferGP(walletFrom=walletFrom, walletTo=walletTo, amount=amount, isMint=True)
    
    def requiredTopupForTransfer(self, wallet:CryptoWallet, amount:float):
        return self._requiredTopup(wallet=wallet, amount=amount, isMint=False)
        
    def requiredTopupForMint(self, wallet:CryptoWallet, amount:float):
        return self._requiredTopup(wallet=wallet, amount=amount, isMint=True)
    
    def requiredTopupForTransferEther(self, wallet:CryptoWallet, amount:float):
        return self._requiredTopupForEther(wallet=wallet, amount=amount, isMint=False)
        
    def requiredTopupForMintEther(self, wallet:CryptoWallet, amount:float):
        return self._requiredTopupForEther(wallet=wallet, amount=amount, isMint=True)
        
    def _requiredTopup(self, wallet:CryptoWallet, amount:float, isMint:bool):
        gas = self.calculateGasFeesForMintGP(amount=amount)
        if gas > wallet.ethBalance:
            return gas - wallet.ethBalance
        else:
            return EtherCoin(0.0)
        
    def _requiredTopupForEther(self, wallet:CryptoWallet, amount:float, isMint:bool):
        gas = self.calculateGasFeesForMintEther(amount=amount) if isMint else self.calculateGasFeesForTransferEther(amount=amount)
        if gas > wallet.ethBalance:
            return gas - wallet.ethBalance
        else:
            return EtherCoin(0.0)
        
    def _transferGP(self, walletFrom:CryptoWallet, walletTo:CryptoWallet, amount:float, isMint:bool):
        if self._walletBalances[walletFrom.id].gpTokensView.amount < amount and not isinstance(walletFrom.owner,GreenPointsHouse):
            raise InsufficientGreenPointsError(f'{walletFrom}')
        
        if amount > 0:
            gas = self.calculateGasFeesForMintGP(amount=amount) if isMint else self.calculateGasFeesForTransferGP(amount=amount)
            self._walletBalances[walletFrom.id]._ether -= gas.amount
            self._usedGas += gas
            self._walletBalances[walletFrom.id]._gpTokens -= amount
            self._walletBalances[walletTo.id]._gpTokens += amount
            _tokens = GreenPointTokens(amount=amount, callerSecret=self.__housesecret__)
            self._transactionHistory.append(GreenPointsChain.Transaction(walletFrom=walletFrom, walletTo=walletTo, amount=_tokens))
            return _tokens
        
    def transferEther(self, walletFrom:CryptoWallet, walletTo:CryptoWallet, amount:float):
        return self._transferEther(walletFrom=walletFrom, walletTo=walletTo, amount=amount, isMint=False)
    
    def mintEther(self, walletTo:CryptoWallet, amount:float, callerSecret:str):
        walletFrom = self.__house.cryptoWallet
        if not self.__house.checkCallFromHouse(callerSecret):
            return
        return self._transferEther(walletFrom=walletFrom, walletTo=walletTo, amount=amount, isMint=False)
    
    def _transferEther(self, walletFrom:CryptoWallet, walletTo:CryptoWallet, amount:float, isMint:bool):
        if self._walletBalances[walletFrom.id].ether < amount and not isinstance(walletFrom.owner,GreenPointsHouse):
            raise InsufficientGreenPointsError(f'{walletFrom}')
        
        if amount > 0:
            gas = self.calculateGasFeesForMintEther(amount=amount) if isMint else self.calculateGasFeesForTransferEther(amount=amount)
            self._walletBalances[walletFrom.id]._ether -= gas.amount
            self._usedGas += gas
            self._walletBalances[walletFrom.id]._ether -= amount
            self._walletBalances[walletTo.id]._ether += amount
            _etherMint = EtherCoin(amount)
            self._transactionHistory.append(GreenPointsChain.Transaction(walletFrom=walletFrom, walletTo=walletTo, amount=_etherMint))
            return _etherMint
        
    def balance(self, wallet:CryptoWallet):
        return self._walletBalances[wallet.id]
            
    class Transaction:
        def __init__(self, walletFrom:CryptoWallet, walletTo:CryptoWallet, amount:(EtherCoin|GreenPointTokens)) -> None:
            self.walletFrom=walletFrom
            self.walletTo=walletTo
            self.amount=amount
            
        def toDict(self) -> dict[str,TSTRUC_ALIAS]:
            return {
                'walletFrom': self.walletFrom.toDict(),
                'walletTo': self.walletTo.toDict(),
                'amount': self.amount.toDict(),
            }
            
    class Balance:
        def __init__(self, outer:GreenPointsChain, ether:float=0.0, gpTokens:float=0.0) -> None:
            self._ether = ether
            self._gpTokens = gpTokens
            self.__outer = outer
            
        def __repr__(self):
            return f'{super().__repr__()} [{EtherCoin(self._ether)} ; {self.gpTokensView}]'
            
        @property
        def ether(self):
            return self._ether
        
        @property
        def gpTokensAmount(self):
            return self._gpTokens
        
        @property
        def gpTokensView(self):
            return GreenPointTokensView(gp=GreenPointTokens(amount=self._gpTokens, callerSecret=self.__outer.__housesecret__))
            

class SingletonMeta(type):
    __instance:SingletonMeta|None = None

    @property
    def instance(self:Self) -> Self:
        assert self.__instance is not None
        return self.__instance
    

class GreenPointsHouse(Institution):
    '''Singleton: Call getInstance() to get the House'''
    __instance:GreenPointsHouse|None = None
    
    @staticmethod 
    def getInstance():
        """ Static access method. """
        if GreenPointsHouse.__instance == None:
            GreenPointsHouse()
        assert isinstance(GreenPointsHouse.__instance,GreenPointsHouse)
        return GreenPointsHouse.__instance
    
    def __init__(self):
        """ Virtually private constructor. """
        if GreenPointsHouse.__instance != None:
            raise Exception("GreenPointsHouse class is a singleton!")
        else:
            GreenPointsHouse.__instance = self
            super().__init__(GreenPointsHouse.__name__)
            self.__secret__ = str(uuid.uuid4())
            self.__houseAccount = None
            self.cashAccountBalance:Money = Money(0.0, GreenPointsHouse.__houseCurrency)
            self._dataFeed = ChainLinkDummyDataFeed()
            self._gpChain = GreenPointsChain.getInstance(callerSecret=self.__secret__, gpHouse=self)
            
            # self.ethWallet = EtherWallet(balance=EtherCoin(0.0))
            # self._transactionHistory:list[GreenPointsTransaction] = []
    
    @property     
    def _bank(self):
        return AMEX_BANK
    
    @property
    def _houseAccount(self):
        if self.__houseAccount is None:
            self.__houseAccount = BankAccount(accountHolder=self, 
                                              bank=self._bank, 
                                              startingBalance=self.cashAccountBalance)
            self._gpChain.assignHouseAccountBalance(id=self.__houseAccount.cryptoWallet.id, callerSecret=self.__secret__)
        return self.__houseAccount
    
    def purchaseSucceeded(self, purchaseId: str, transaction: Any):
        # 'GreenPointHouse cannot make purchases'
        return
            
    def checkCallFromHouse(self, callerSecret:str):
        return bool(self.__secret__ == callerSecret)
    
    def checkInitialised(self, callerSecret:str):
        if self._gpChain.checkCallFromChain(callerSecret=callerSecret):
            return isinstance(self._houseAccount,BankAccount)
    
    def zeroTokenWrapperView(self):
        return GreenPointTokensView(gp=GreenPointTokens(amount=0.0, callerSecret=self.__secret__))
    
    def zeroTokenWrapper(self):
        return GreenPointTokens(amount=0.0, callerSecret=self.__secret__)
    
    # def combineTokenAmounts(self, a:GreenPointTokens, b:GreenPointTokens):
    #     return a + b
    
    __houseCurrency:Literal['GBP'] = 'GBP'
    
    def _getHouseCurrency(self):
        return GreenPointsHouse.__houseCurrency
    
    # def _getEthWallet(self):
    #     return self._houseAccount.cryptoWallet.ethBalance
    
    # ethWallet:EtherWallet = property(_getEthWallet) #type: ignore 
    
    def _getCryptoWallet(self):
        return self._houseAccount.cryptoWallet
    
    cryptoWallet:CryptoWallet = property(_getCryptoWallet) #type: ignore
    
    houseCurrency:Literal['GBP'] = property(_getHouseCurrency) #type: ignore 
    
    def balance(self, wallet:CryptoWallet):
        return self._gpChain.balance(wallet=wallet)

    def requireTopUpToTransferEther(self, wallet:CryptoWallet, amount:float):
        numEther = EtherCoin(0.0)
        if amount > 0:
            gas = self._gpChain.calculateGasFeesForTransferEther(amount=amount)
            if wallet.ethBalance < (amount + gas):
                numEther = ((amount + gas) - wallet.ethBalance)
        return numEther
    
    def costToMintEther(self, wallet:CryptoWallet, amount:float):
        if amount > 0:
            fx_ETHCcy = self._dataFeed.getEtherToCurrencyRate(toCurrency=GreenPointTokens.peggedCurrency)
            assert fx_ETHCcy is not None
            gasMoney = Money(self._gpChain.calculateGasFeesForMintEther(amount=amount).amount * fx_ETHCcy, currency=GreenPointTokens.peggedCurrency)
            
            return gasMoney
        return Money(0.0, GreenPointTokens.peggedCurrency)
        
    def requireTopUpToTransferGreenPoints(self, wallet:CryptoWallet, amount:float):
        topupEth = EtherCoin(0)
        topupGP = 0.0
        if amount > 0:
            gas = self._gpChain.calculateGasFeesForTransferGP(amount=amount)
            if gas > wallet.ethBalance:
                topupEth:EtherCoin = gas - wallet.ethBalance
            
            
            CheckSameTypeError.check(topupGP, wallet.gpBalanceAmount)
            if wallet.gpBalanceAmount < amount:
                topupGP = amount - wallet.gpBalanceAmount
            
        return (topupEth, topupGP)
        
    def buyEther(self, wallet:CryptoWallet, amount:float, usingPaymentCallBack:Callable[[Money,BankAccount],None], caller:Bank):
        if amount > 0 and wallet.ownerBankAccount.bank == caller:
            fx_ETHCcy = self._dataFeed.getEtherToCurrencyRate(toCurrency=GreenPointTokens.peggedCurrency)
            assert fx_ETHCcy is not None
            gasMoney = Money(self._gpChain.calculateGasFeesForMintEther(amount=amount).amount / fx_ETHCcy, currency=GreenPointTokens.peggedCurrency)
            costMoney = Money(amount / fx_ETHCcy, currency=GreenPointTokens.peggedCurrency)
            usingPaymentCallBack(gasMoney+costMoney, self._houseAccount)
            mintEther = self._gpChain.mintEther(walletTo=wallet, amount=amount, callerSecret=self.__secret__)
            return (gasMoney+costMoney), mintEther, self._houseAccount
        return (Money(0.0,currency=GreenPointTokens.peggedCurrency), EtherCoin(0.0), None)
                
    
    def transferEther(self, walletFrom:CryptoWallet, walletTo:CryptoWallet, amount:EtherCoin, caller:Bank):
        if amount > 0 and walletFrom.ownerBankAccount.bank == caller:
            gas = self._gpChain.calculateGasFeesForTransferEther(amount=amount.amount)
            assert walletFrom.ethBalance >= (amount + gas)
            self._gpChain.transferEther(walletFrom=walletFrom, walletTo=walletTo, amount=amount.amount)
    
    
    def buyGreenPoints(self, wallet:CryptoWallet, amount:float, usingPaymentCallBack:Callable[[Money,BankAccount],None], caller:Bank):
        if amount > 0 and wallet.ownerBankAccount.bank == caller:
            fx_ETHCcy = self._dataFeed.getEtherToCurrencyRate(toCurrency=GreenPointTokens.peggedCurrency)
            assert fx_ETHCcy is not None
            gasMoney = Money(self._gpChain.calculateGasFeesForMintGP(amount=amount).amount / fx_ETHCcy, currency=GreenPointTokens.peggedCurrency)
            gpx_GPTCcy = GreenPointTokens.tokenValueInPeggedCurrency
            costMoney = Money(amount * gpx_GPTCcy, currency=GreenPointTokens.peggedCurrency)
            usingPaymentCallBack(gasMoney+costMoney, self._houseAccount)
            return ((gasMoney+costMoney), self._gpChain.mintGP(walletTo=wallet, amount=amount, callerSecret=self.__secret__), self._houseAccount)
        return (Money(0.0,currency=GreenPointTokens.peggedCurrency), self.zeroTokenWrapper(), None)
    
    def transferGreenPoints(self, walletFrom:CryptoWallet, walletTo:CryptoWallet, amountGP:float, caller:Bank):
        if amountGP > 0 and walletFrom.ownerBankAccount.bank == caller:
            gas = self._gpChain.calculateGasFeesForTransferGP(amount=amountGP)
            assert walletFrom.ethBalance.amount >= gas
            assert walletFrom.gpBalanceAmount >= amountGP
            gpt = self._gpChain.transferGP(walletFrom=walletFrom, walletTo=walletTo, amount=amountGP)
            return (gas, gpt)
        return (EtherCoin(0), self.zeroTokenWrapper())
    
    def calculateGasFeesForTransfer(self, amount:(GreenPointTokensView|GreenPointTokens|float)):
        return self._gpChain.calculateGasFeesForTransferGP(amount=amount)
        
    def calculateGasFeesForMint(self, amount:(GreenPointTokensView|GreenPointTokens|float)):
        return self._gpChain.calculateGasFeesForMintGP(amount=amount)
 
 
class Entity(Identifiable,ISerializable,metaclass=abc.ABCMeta):
    def __init__(self, name:str, account:BankAccount, bank:Bank) -> None:
        if bank is None:
            bank = AMEX_BANK
        assert account is not None
        super().__init__()
        self._name = str(name)
        self._bank = bank
        self._accounts:list[BankAccount] = [account]
        self._permittedTransfers:dict[str,Tuple[float,TransferType]] = {}
    
    @property
    def bank(self):
        return self._bank
    
    @property
    def name(self):
        return self._name
    
    @property
    def allTransactionsIn(self):
        return [tran for account in self._accounts for tran in self._bank.fetchAllTransactionsToAccount(account.id)]
    
    @property
    def allTransactionsOut(self):
        return [tran for account in self._accounts for tran in self._bank.fetchAllTransactionsFromAccount(account.id)]
    
    @property
    def balance(self):
        return sum([a.balance.view() for a in self._accounts], start=BankAccountView.zero())
    
    @abc.abstractmethod
    def copyInstance(self:Self, copyId:bool=False) -> Self:
        raise NotImplementedError('Entity.fromEntity is abstract')

    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            **self.toDictUI(),
            "accounts": [a.toDictFromCaller(caller=self) for a in self._accounts]
        }
        
    def toDictUI(self) -> dict[str, TSTRUC_ALIAS]:
        return {
            **self.toDictLight(),
            "bank": self.bank.toDictLight(),
            "balance": self.balance.toDictUI(),
            "balanceMoney": self.balance.combinedBalance.toDict()
        }
        
    def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            "id": self.id,
            "name": self.name
        }
    
    def _getAccountForCurrencyTransfer(self, currency:str, amount:float=0.0):
        x = next((a for a in self._accounts if a.fiatCurrency == currency and a.balance.view().moneyBalance >= amount),
                    next((a for a in self._accounts if a.balance.view(inCurrency=currency).moneyBalance >= amount),
                         None
                         )
                    )
        if x is None:
            raise InsufficientMoneyError('Insufficient money on account for currency transfer')
        return x
        
    def _getAccountForPayment(self, currency:str, amount:float=0.0):
        x = next((a for a in self._accounts if a.fiatCurrency == currency and a.balance.view().combinedBalance >= amount),
                    next((a for a in self._accounts if a.balance.view(inCurrency=currency).combinedBalance >= amount),
                         None
                         )
                    )
        
        if x is None:
            raise InsufficientMoneyError('Insufficient money & points on account for payment')
        return x
    
    def intersectingCurrencies(self:Self,other:Self):
        return list(set((acc.fiatCurrency for acc in self._accounts)).intersection(set((acc.fiatCurrency for acc in other._accounts))))
        
    def accountForPayment(self, payment:Money):
        return self._getAccountForPayment(currency=payment.currency, amount=payment.amount)
    
    def addBankAccount(self, bankAccount:BankAccount):
        if bankAccount.fiatCurrency not in [a.fiatCurrency for a in self._accounts] or bankAccount not in self._accounts:
            self._accounts.append(bankAccount)

    def isPermittedTransfer(self, toBankAccountId:str, amountPermitted:float, transferType:TransferType):
        if toBankAccountId in self._permittedTransfers and amountPermitted is not None \
            and self._permittedTransfers[toBankAccountId] is not None and self._permittedTransfers[toBankAccountId][0] is not None \
                and self._permittedTransfers[toBankAccountId][1] == transferType:
            return True
        else:
            return False
        
    def _permitTransfer(self, toBankAccountId:str, amountPermitted:float, transferType:TransferType):
        self._permittedTransfers[toBankAccountId] = (amountPermitted,transferType)
        
    @abc.abstractclassmethod
    def purchaseSucceeded(self, purchaseId:str, transaction:Bank.Transaction):
        pass
    
    def __repr__(self):
        return f'{type(self)} {self.name}'
    
    def __str__(self):
        return f'{type(self).name} {self.name}'
    
    def __eq__(self:Self,o:Any):
        assert isinstance(o, Entity)
        return self.id == o.id
      
class Customer(Entity):
    def __init__(self, name:str, bank:Bank|None=None) -> None:
        if bank is None:
            bank = AMEX_BANK
        self._name = name
        self._bank = bank
        super().__init__(name, CustomerAccount(accountHolder=self, bank=bank), bank)
        self._basket:list[PurchaseDTO] = []
        self._purchaseHistory:list[Purchase] = []
        
    # def withStartingMoney(name:str,money:Money,bank:Bank=AMEX_BANK):
    #     customer = Customer(name,bank,accountCurrency=money.currency)
    #     account = customer._getAccountForCurrencyTransfer(currency=money.currency, amount=0.0)
    #     .addMoney(money)
    #     return customer
    
    def _withAccounts(self:Self, oldSelf:Self) -> Self:
        for account in self._accounts:
            account.close()
        
        self._accounts = oldSelf._accounts
        for account in self._accounts:
            account.resetBalance()
        
        return self
    
    def copyInstance(self:Self, copyId:bool=False) -> Self:
        return Customer(name=self.name, bank=self.bank)._withId(self.id, ifTrue=copyId)#._withAccounts(self)
        # return type(self).fromEntity(entity=type(self)(name=self.name, account=self._accounts[0], bank=self.bank))
    
    @property
    def basket(self):
        return self._basket
    
    @property
    def purchaseHistory(self):
        return self._purchaseHistory
    
    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            **super().toDict(),
            "bank": self.bank.toDictLight(),
            "basket": [p.toDict() for p in self.basket],
            "purchaseHistory": [p.toDict() for p in self.purchaseHistory]
        }
        
    def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            **super().toDictUI(),
            "bank": self.bank.toDictLight(),
            "basket": [p.toDictUI() for p in self.basket],
            "purchaseHistory": [p.toDictUI() for p in self.purchaseHistory]
        }
    
    def addToBasket(self, purchase:PurchaseDTO):
        assert purchase is not None
        if purchase is not None:
            self._basket.append(purchase)
        
    def buy(self, itemName:str):
        return CustomerChosenItem(self, itemName)
    
    @staticmethod
    def choosesItem(itemProb:float):
        assert isinstance(itemProb, float) or isinstance(itemProb, int)
        assert itemProb <= 1.0 and itemProb >= 0.0
        return bool(itemProb > np.random.uniform(low=0.0, high=1.0))
    
    def checkout(self):
        while self._basket:
            item = self._basket.pop(0)
            self._purchaseItem(item)
        
        
    def _purchaseItem(self, purchase:PurchaseDTO):
        assert purchase.price == purchase.item.cost
        account = self._getAccountForPayment(currency=purchase.price.currency,amount=purchase.price.amount)
        if account is not None:
            
            accountBalance = account.balance.view()
            if accountBalance.combinedBalance >= purchase.price.amount:
                costHandler = CostHandler(initialCost=purchase.item.cost, startingBalance=accountBalance)
                costHandler.reduceBy(
                    account.releaseGP(greenPointsAmount=accountBalance
                                      .changeCurrency(toCurrency=purchase.item.cost.currency)
                                      .viewGreenPoints,
                                      toAccount=purchase.item.retailer.accountForPayment(payment=purchase.item.cost)))
                if costHandler.costRemaining > 0:
                    costHandler.reduceBy(
                        account.releaseMoney(funds=accountBalance
                                             .changeCurrency(toCurrency=purchase.item.cost.currency)
                                             .moneyBalance,
                                             toAccount=purchase.item.retailer.accountForPayment(payment=purchase.item.cost)))
                assert costHandler.costRemaining.amount == 0
                
                transaction = purchase.item.retailer.buyFrom(customer=self, customerAccount=account, purchase=purchase, costHandler=costHandler)
                if transaction.success:
                    accountBalanceRefreshed = account.balance.view()
                    # BUG: The Retailer's BankAccount doesnt add itself as an observer to observe the bank transaction doesnt and tehn doesnt send out the GP Rewards to the customer.
                    #  Q1: Where does the bank account sign up for updates?
                    if accountBalanceRefreshed.gpAmount != (
                        costHandler.startingBalance.gpAmount
                        - transaction.greenpoints.greenPoints.amount
                        + purchase.gpReward
                        ):
                        debugObject = {
                            'accountBalanceRefreshed.gpAmount': accountBalanceRefreshed.gpAmount,
                            'transactionMoves': {
                                'total': (
                                          costHandler.startingBalance.gpAmount
                                          - transaction.greenpoints.greenPoints.amount
                                          + purchase.gpReward
                                          ),
                                'costHandler.startingBalance.gpAmount': costHandler.startingBalance.gpAmount,
                                'transaction.greenpoints.greenPoints.amount': -transaction.greenpoints.greenPoints.amount,
                                'purchase.gpReward': purchase.gpReward,
                            },
                            'transaction': transaction.toDict()
                        }
                        raise GreenPointsLostInDoubleBookingTransactionException(
                            debugObject,
                            'CATASTROPHE: Green points on the two sides of double booking of transaction don\'t offset one another.'
                        )
                    #BUG: Money will be spent on purchasing ether by the customer account in order to 
                    #   TRANSFER gp to the Retailer for the purchase. 
                    #   This comes off the money account balance but is not factored into the below assertion.
                    
                    if accountBalanceRefreshed.moneyBalance != \
                        (costHandler.startingBalance.moneyBalance -
                         transaction.money +
                         transaction.totalMoneyCostInclTopUps
                         ):
                        debugObject = {
                            'accountBalanceRefreshed.moneyBalance': accountBalanceRefreshed.moneyBalance,
                            'transactionMoves': {
                                "total": (costHandler.startingBalance.moneyBalance -
                                          transaction.money +
                                          transaction.totalMoneyCostInclTopUps
                                          ),
                                'costHandler.startingBalance.moneyBalance': costHandler.startingBalance.moneyBalance,
                                'transaction.money': -transaction.money,
                                'transaction.totalMoneyCostInclTopUps': transaction.totalMoneyCostInclTopUps,
                            },
                            'transaction': transaction.toDict()
                        }
                        raise DoubleBookingTransactionMisMatchException(debugObject,
                            'CATASTROPHE: Money lost in system. \nTransaction is inconsistent with account balance remaining Money')
                    self.purchaseHistory.append(Purchase(
                        transaction=transaction, 
                        retailer=purchase.retailer, 
                        item=purchase.item
                    ))
                else:
                    raise PurchaseItemTransactionError()
            else:
                raise InsufficientMoneyError('Insufficient Funds to purchase Item')
            
    def purchaseSucceeded(self, purchaseId:str, transaction:Bank.Transaction):
        basketItem = next((p for p in self._basket if p.id == purchaseId), None)
        if basketItem is not None:
            self._basket.remove(basketItem)
  
class Retailer(Entity):
    def __init__(self, name:str, strategy:RetailerStrategyGPMultiplier, sustainability: RetailerSustainabilityIntercept, greenPointFiatValue:float=0.01, bank:Bank|None=None) -> None:
        if bank is None:
            bank = AMEX_BANK
        self._name = name
        self._bank = bank
        defaultAccount = RetailerAccount(self, bank)
        super().__init__(name, defaultAccount, bank)
        self._gpIssueingAccount = \
            GreenPointIssueingAccount(self, 
                                      supportingBankAccount=defaultAccount, 
                                      bank=self._bank)
        self._strategy = strategy
        self._sustainability = sustainability
        self.greenPointFiatValue = greenPointFiatValue
        self.salesCount = 0
        self._salesHistory:list[Sale] = []
        self._waitingPurchasesToSettle:list[PurchaseDTO] = []
        
    def _withAccounts(self:Self, oldSelf:Self) -> Self:
        for account in self._accounts:
            account.close()
        self._gpIssueingAccount.close()
        self._accounts = oldSelf._accounts
        for account in self._accounts:
            account.resetBalance()
        self._gpIssueingAccount = oldSelf._gpIssueingAccount
        self._gpIssueingAccount.resetBalance()
        return self
        
    def copyInstance(self:Self, deepCopy:bool=False) -> Self:
        return Retailer(name=self.name, 
                        strategy=self._strategy, 
                        sustainability=self._sustainability, 
                        greenPointFiatValue=self.greenPointFiatValue, 
                        bank=self.bank)._withId(self.id, ifTrue=deepCopy)#._withAccounts(self)
    
    def toDict(self) -> dict:
        return {
            **super().toDict(),
            **self.toDictUI(),
            'salesHistory': [s.toDict() for s in self._salesHistory],
            'totalSales': self.totalSales.toDict()
        }

    def toDictUI(self) -> dict:
        return {
            **super().toDictUI(),
            **self.toDictLight(),
            'salesHistory': [s.toDictUI() for s in self._salesHistory],
            'totalSales': self.totalSales.toDictUI()
        }
        
    def toDictLight(self) -> dict:
        return {
            **super().toDictLight(),
            'name': self.name,
            'strategy': self.strategy,
            'sustainability': self.sustainability
        }
        
    
        
    def buyFrom(self, customer:Customer, customerAccount:BankAccount, purchase:PurchaseDTO, costHandler:CostHandler):
        self._waitingPurchasesToSettle.append(purchase)
        transaction = customerAccount\
            .transact(costHandler=costHandler, 
                      toAccount=purchase.item.retailer.accountForPayment(payment=purchase.item.cost), 
                      purchaseId=purchase.id)
        return transaction
    
    @property
    def strategy(self):
        return self._strategy
    
    @strategy.setter
    def strategy(self, value:RetailerStrategyGPMultiplier):
        self._strategy = value
    
    @property
    def sustainability(self):
        return self._sustainability
    
    @sustainability.setter
    def sustainability(self, value:RetailerSustainabilityIntercept):
        self._sustainability = value
        
    @property
    def salesHistory(self):
        return [s for s in self._salesHistory]
    
    @property
    def totalSales(self:Self):
        def reductionFn(start:SalesAggregation, sale:Sale) -> SalesAggregation:
            greenPointsIssuedForItem = sale.greenPointsIssuedForItem
            transaction:Bank.Transaction = sale.transaction
            retailer:Retailer = sale.retailer
            item:Item = sale.item
            
            if transaction.money.currency not in start.totalMoneySentByCcy:
                start.totalMoneySentByCcy[transaction.money.currency] = Money(0.0, transaction.money.currency)
            start.totalMoneySentByCcy[transaction.money.currency] += transaction.money
            if item.cost.currency not in start.totalCostByCcy:
                start.totalCostByCcy[item.cost.currency] = Money(0.0, item.cost.currency)
            start.totalCostByCcy[item.cost.currency] += item.cost
            start.totalGPIssued += greenPointsIssuedForItem.greenPoints.amount
            start.numItemsIssued += 1
            start.itemCountMap[item.name] += 1
            # return SalesAggregation(totalCostByCcy=totalCostByCcy,
            #                         totalMoneySentByCcy=totalMoneySentByCcy,
            #                         totalGPIssued=totalGPIssued,
            #                         numItemsIssued=numItemsIssued,
            #                         itemCountMap=itemCountMap
            #                         )
            return start
             
        return reduce(reductionFn, self.salesHistory, SalesAggregation.zero())
    
    @property
    def bank(self):
        return self._bank
    
    @property
    def allTransactionsIn(self):
        return super().allTransactionsIn + \
            [tran for tran in self._bank.fetchAllTransactionsToAccount(
                self._gpIssueingAccount.id)]
    
    @property
    def allTransactionsOut(self):
        return super().allTransactionsOut + \
            [tran for tran in self._bank.fetchAllTransactionsFromAccount(
                self._gpIssueingAccount.id)]
    
    def removeFromInventory(self, item:Item, transaction:Bank.Transaction, gp:Bank.Transaction.GreenPoints):
        assert item.retailer == self, f'Item belongs to a different retailer: {item.retailer.name}. This retailer is {self.name}.'
        self.salesCount += 1
        self._salesHistory.append(Sale(transaction=transaction, retailer=self, item=item, greenPointsIssuedForItem=gp))
        return self
    
    def purchaseSucceeded(self, purchaseId:str, transaction:Bank.Transaction):
        basketItem = next((p for p in self._waitingPurchasesToSettle if p.id == purchaseId), None)
        if basketItem is not None:
            if basketItem.gpReward == 0:
                return
            id = str(uuid.uuid4())
            (ethGas,gpt,moneySpent) = self._gpIssueingAccount.issueGreenPointsToCustomer(customerAccount=basketItem.customerAccount, 
                                                                               amount=basketItem.gpReward, 
                                                                               originatorTransactionId=id)
            # BUG: No green points are currently issued to customers in the sales record? 
            #   Get the transaction from the issueGreenPointsToCustomer so that we can get the number of gp actually issued?
            if gpt is not None:
                self.removeFromInventory(item=basketItem.item, 
                                         transaction=transaction,
                                         gp=Bank.Transaction.GreenPoints(
                                             gas=ethGas, 
                                             greenPoints=GreenPointTokensView(gp=gpt), 
                                             money=moneySpent))\
                        ._waitingPurchasesToSettle.remove(basketItem)
                
            else:
                raise BankTransactionFailedError('Bank failed to issue GP for Retailer')
            

class SalesAggregation(ISerializableBasic):
    
    def __init__(self, totalCostByCcy:dict[str,Money] = {}, totalMoneySentByCcy:dict[str,Money] = {}, totalGPIssued:float = 0.0, numItemsIssued:int = 0, itemCountMap:DefaultDict[str,int] = defaultdict(int)):
        super().__init__()
        self.totalCostByCcy = totalCostByCcy
        self.totalMoneySentByCcy = totalMoneySentByCcy
        self.totalGPIssued = totalGPIssued
        self.numItemsIssued = numItemsIssued
        self.itemCountMap = itemCountMap
    
    @staticmethod   
    def zero():
        return SalesAggregation()
        
    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            'totalCostByCcy': {k:v.toDict() for k,v in self.totalCostByCcy.items()},
            'totalMoneySentByCcy': {k:v.toDict() for k,v in self.totalMoneySentByCcy.items()},
            'totalGPIssued': self.totalGPIssued,
            'numItemsIssued': self.numItemsIssued,
            'itemCountMap': self.itemCountMap,
        }
        
    def __add__(self:Self, o):
        assert isinstance(o, type(self))
        return SalesAggregation(
            totalCostByCcy={
                **self.totalCostByCcy,
                **o.totalCostByCcy,
                **{k:(v + o.totalCostByCcy[k]) for k,v in self.totalCostByCcy.items() if k in o.totalCostByCcy.keys()}
            },
            totalMoneySentByCcy={
                **self.totalMoneySentByCcy,
                **o.totalMoneySentByCcy,
                **{k: (v + o.totalMoneySentByCcy[k]) for k, v in self.totalMoneySentByCcy.items() if k in o.totalMoneySentByCcy.keys()}
            },
            totalGPIssued=self.totalGPIssued + o.totalGPIssued,
            numItemsIssued=self.numItemsIssued + o.numItemsIssued,
            itemCountMap=defaultdict(int,{
                **self.itemCountMap,
                **o.itemCountMap,
                **{k: (v + o.itemCountMap[k]) for k, v in self.itemCountMap.items() if k in o.itemCountMap.keys()}
            })
        )
        
        
    

class CryptoWallet(Identifiable):
    
    def __init__(self, owner:BankAccount) -> None:
        super().__init__()
        # self._gp = gp
        # self._eth = eth
        self._ownerBankAccount=owner
        self._gpHouse = GreenPointsHouse.getInstance()
    
    @property
    def ethBalance(self):
        return EtherCoin(self._gpHouse.balance(self).ether)
    
    @property
    def gpBalanceAmount(self):
        return self._gpHouse.balance(self).gpTokensView.amount
    
    @property
    def chainBalance(self):
        return self._gpHouse.balance(self)
    
    @property
    def owner(self):
        return self._ownerBankAccount.owner
       
    @property
    def ownerBankAccount(self):
        return self._ownerBankAccount
    
    @property
    def ownerBank(self):
        return self._ownerBankAccount.bank
    
    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            "ethBalance": self.ethBalance.toDict(),
            "gpBalance": self.gpBalanceAmount,
            "owner": self.owner.toDictLight(),
            "ownerBankAccount": self.ownerBankAccount.toDictLight(),
            "ownerBank": self.ownerBank.toDictLight()
        }
    
    def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            "ethBalance": self.ethBalance.toDict(),
            "gpBalance": self.gpBalanceAmount,
            "owner": self.owner.toDictLight(),
            "ownerBankAccount": self.ownerBankAccount.toDictLight(),
            "ownerBank": self.ownerBank.toDictLight()
        }
    
    def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            "ethBalance": self.ethBalance.toDict(),
            "gpBalance": self.gpBalanceAmount,
            "owner": self.owner.toDictLight(),
            "ownerBankAccount": self.ownerBankAccount.toDictLight(),
            "ownerBank": self.ownerBank.toDictLight()
        }
    
    def __repr__(self):
        return f'{super().__repr__()} [{self.chainBalance}]'

    
       
class BankAccount(Identifiable, ISerializable):
    def __init__(self, accountHolder: (Customer|Retailer|Institution), bank:Bank, startingBalance:Money) -> None:
        assert accountHolder is not None, 'accountHolder must exist'
        assert (isinstance(accountHolder,Customer) or isinstance(accountHolder,Retailer) or isinstance(accountHolder,Institution)), 'accountHolder must be Customer or Retailer'
        assert bank is not None and isinstance(bank,Bank), 'BankAccount requires a bank'
        super().__init__()
        self._owner:(Customer|Retailer|Institution) = accountHolder
        self._bank = bank
        self._cryptoWallet = CryptoWallet(owner=self)
        self._bank.addAccount(self)
        self._startingBalanceWhenCreated = startingBalance
        self._bank.setMoneyAccountBalance(self.id, startingBalance)
        self.__house = GreenPointsHouse.getInstance()
        # self._greenPointsManager = GreenPointsWallet(self)
        # self._ethWallet = EtherWallet(EtherCoin(0.0))
        self._permissionedTransfers:list[Transfer] = []
        self._waitingTransactionsSettle:list[str] = []
        self._mapTransactionToPurchase:dict[str,str] = {}
        self.bankSendsMoneyObserver = BankAccount.BankSendsMoneyObserver(self)
        self._bank.sendMoneyNotifier.addObserver(self.bankSendsMoneyObserver)
        self._minEthBalance = EtherCoin(0.000)
        self._minEthTopUp = EtherCoin(0.0001)
        
    def __eq__(self, __o: object) -> bool:
        return bool(isinstance(__o,BankAccount) and self.id == __o.id)
    
    def __repr__(self):
        return f'{type(self).__name__}: for {self.owner.name}'
    
    def close(self):
        assert self._waitingTransactionsSettle == [
        ], 'Account can not be closed whilst waiting for _waitingTransactionsSettle'
        self._bank.sendMoneyNotifier.deleteObserver(self.bankSendsMoneyObserver)
        self._bank.removeAccount(self)
        
    def resetBalance(self):
        raise NotAllowedError('Do not manufacturer money, rather create new owners with new bank accounts...')
        # self._bank.setMoneyAccountBalance(self.id, self._startingBalanceWhenCreated)
    
    @property
    def owner(self):
        return self._owner
    
    @property
    def fiatCurrency(self):
        return self._moneyBalance.currency
    
    @property
    def _moneyBalance(self):
        return self._bank.accountBalances[self.id]
    
    @property
    def bank(self):
        return self._bank
    
    @property
    def cryptoWallet(self):
        return self._cryptoWallet
     
    @property
    def balance(self):
        return BankAccountBalanceInCurrency(moneyBalance=self._moneyBalance, 
                                            greenPointsBalance=self.cryptoWallet.chainBalance.gpTokensView, 
                                            accountBank=self._bank)
        
    def toDictFromCaller(self, caller:Any=None) -> dict[str,TSTRUC_ALIAS]:
        if isinstance(caller,Entity) and caller == self.owner:
            return {
                **super().toDict(),
                "fiatCurrency": self.fiatCurrency,
                "owner": self.owner.toDictLight(),
                "bank": self.bank.toDictLight(),
                "balance": self.balance.toDict(),
                "cryptoWallet": self.cryptoWallet.toDict()
            }
        elif isinstance(caller,Bank) and caller == self.bank:
            return {
                **super().toDict(),
                "owner": self.owner.toDict(),
                "fiatCurrency": self.fiatCurrency,
                "bank": self.bank.toDictLight(),
                "balance": self.balance.toDict(),
                "cryptoWallet": self.cryptoWallet.toDict()
            }
        else:
            return self.toDict()
            
        
    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            **super().toDict(),
            "owner": self.owner.toDict(),
            "fiatCurrency": self.fiatCurrency,
            "bank": self.bank.toDictLight(),
            "balance": self.balance.toDict(),
            "cryptoWallet": self.cryptoWallet.toDict()
        }
        
    def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            **super().toDict()
        }
    
    def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            **super().toDict(),
            "owner": self.owner.toDictLight(),
            "fiatCurrency": self.fiatCurrency,
            "bank": self.bank.toDictLight(),
            "balance": self.balance.toDict(),
            "cryptoWallet": self.cryptoWallet.toDictUI()
        }
    
    def _replenishLowEthBalances(self):
        (moneySpent, ethBought, topupTransaction) = (Money(0.0), None, None)
        if self._minEthBalance.amount != 0 and self._cryptoWallet.ethBalance < self._minEthBalance:
            (moneySpent, ethBought, topupTransaction) = self._bank.buyEther(wallet=self._cryptoWallet,
                                amount=self._minEthTopUp.amount,
                                caller=self)
        assert self._cryptoWallet.ethBalance >= self._minEthBalance
        return topupTransaction
    
    def releaseMoney(self, funds:Money, toAccount:BankAccount):
        '''Assigns the requested Money as available for release to the specified account if there is sufficient balance and the toAccount then proceeds to action the request'''
        assert toAccount is not None and isinstance(toAccount, BankAccount)
        assert funds is not None and isinstance(funds, Money) and funds.amount > 0 and self.balance.view().moneyBalance >= funds
        transfer = MoneyTransfer(fromObj=self, toObj=toAccount, amount=funds)
        self._permissionedTransfers.append(transfer)
        return funds
    
    def releaseGP(self, greenPointsAmount:GreenPointTokensView, toAccount:BankAccount):
        '''Assigns the requested GP as available for release to the specified account if there is sufficient balance and the toAccount then proceeds to action the request'''
        assert toAccount is not None and isinstance(toAccount, BankAccount)
        assert greenPointsAmount.amount >= 0 and isinstance(greenPointsAmount,GreenPointTokensView)
        if greenPointsAmount.amount > 0:
            transfer = GreenPointTransfer(fromObj=self, toObj=toAccount, amount=greenPointsAmount)
            self._permissionedTransfers.append(transfer)
        return greenPointsAmount
    
    @staticmethod
    def copy(account:BankAccount):
        return BankAccount(accountHolder=account.owner, bank=account._bank, startingBalance=account.balance.view().moneyBalance)
    
    def _willReceiveTransaction(self, originatorTransactionId:str):
        self._waitingTransactionsSettle.append(originatorTransactionId)
        return originatorTransactionId
    
    def transact(self,costHandler:CostHandler,toAccount:BankAccount, purchaseId:str):
        assert isinstance(costHandler,CostHandler), 'BankAccount Transactions must use a CostHandler'
        assert isinstance(toAccount,BankAccount), 'BankAccount Transactions must be directed towards another BankAccount'
        lowValTopUpTran = self._replenishLowEthBalances()
        id = str(uuid.uuid4())
        self._mapTransactionToPurchase[id] = purchaseId
        toAccount._mapTransactionToPurchase[id] = purchaseId
        self._willReceiveTransaction(originatorTransactionId=id)
        toAccount._willReceiveTransaction(originatorTransactionId=id)
        
        transaction = self._bank\
            .createTransaction(accountFrom=self, accountTo=toAccount, originatingTransactionId=id)\
                .withMoneyTransfer(amount=costHandler.moneyToSend)\
                    .withGreenPointTransfer(amount=costHandler.greenPointsToSend)\
                        .finalise().transact()
        if lowValTopUpTran is not None:
            transaction.topUpEtherTransaction = lowValTopUpTran
        return transaction
        
        
        
    class BankSendsMoneyObserver(Observer):
        def __init__(self,outer:BankAccount) -> None:
            super().__init__()
            self.outer = outer
            
        def __repr__(self):
            return f'{type(self).__name__}: for {self.outer.owner.name}'
        
        def update(self, observable:Observable, **kwargs:Any):
            '''self._bank notified us that it has sent money, check if we are in the arg and then do something if we are?'''
            fromBankAccount:BankAccount = kwargs['fromBankAccount']
            toBankAccount:BankAccount = kwargs['toBankAccount']
            fromGPAccount:BankAccount = kwargs['fromGPAccount']
            originatorTransactionId:str = kwargs['originatorTransactionId']
            if originatorTransactionId in self.outer._waitingTransactionsSettle:
                fromBankAccount._waitingTransactionsSettle.remove(originatorTransactionId)
                toBankAccount._waitingTransactionsSettle.remove(originatorTransactionId)
                transaction = self.outer._bank.requestTransferDetails(self.outer.id, originatorTransactionId)
                if not transaction:
                    return
                if transaction.accountFrom.id == self.outer.id:
                    # Event this BankAccount sent money success
                    if self.outer.bank.debug:
                        logging.debug(f'{self.outer._owner.name} has sent {transaction.money} to {toBankAccount._owner.name}')
                    self.outer._owner.purchaseSucceeded(purchaseId=self.outer._mapTransactionToPurchase[originatorTransactionId], transaction=transaction)
                elif transaction.accountTo.id == self.outer.id:
                    # Event this BankAccount has received Money Success
                    if self.outer.bank.debug:
                        logging.debug(f'{self.outer._owner.name} has received {transaction.money} from {fromBankAccount._owner.name}')
                    self.outer._owner.purchaseSucceeded(purchaseId=self.outer._mapTransactionToPurchase[originatorTransactionId], transaction=transaction)


class CustomerAccount(BankAccount):
    def __init__(self, accountHolder: Customer, bank: Bank) -> None:
        super().__init__(accountHolder, bank, startingBalance=Money(100.0, 'GBP'))
        self._minEthBalance = EtherCoin(0.0001)
        self._minEthTopUp = EtherCoin(0.001)
        self._accountHolder = accountHolder
        

    
         
class RetailerAccount(BankAccount):
    def __init__(self, accountHolder: Retailer, bank: Bank) -> None:
        super().__init__(accountHolder, bank, startingBalance=Money(10000.0, 'GBP'))
        self._minEthBalance = EtherCoin(0.001)
        self._minEthTopUp = EtherCoin(1)
        self._accountHolder = accountHolder
        
    
    
        

    
class GreenPointIssueingAccount(BankAccount):
    def __init__(self, accountHolder: Retailer, supportingBankAccount:RetailerAccount, bank: Bank) -> None:
        self._supportingBankAccount = supportingBankAccount
        self._fiatCurrency = self._supportingBankAccount.fiatCurrency
        self._owner = accountHolder
        self._accountHolder = accountHolder
        self._bank = bank
        self.__house = GreenPointsHouse.getInstance()
        super().__init__(accountHolder=accountHolder, bank=bank, startingBalance=Money(0.0,'GBP'))
        # if not issubclass(type(self),BankAccount):
        #     self._bank.addAccount(account=self)
            # self._ethWallet = EtherWallet(EtherCoin(0.0))
        # self._balance:GreenPointTokens = self.__house.zeroTokenWrapper()
        self._minEthBalance = EtherCoin(0.001)
        self._minEthTopUp = EtherCoin(1.0)
        
    
    @property
    def owner(self):
        return self._accountHolder
    
    @property
    def supportingBankAccount(self):
        return self._supportingBankAccount
    
    @property
    def fiatCurrency(self):
        return self._fiatCurrency
    
    @property
    def _balance(self):
        return self.balance
        
    def purchaseGreenPointsFromHouse(self, amount:float):
        amountToMint = (amount - self.cryptoWallet.gpBalanceAmount)
        moneySpent, newMint = self._bank.buyGreenPoints(wallet=self.cryptoWallet, amount=amountToMint, caller=self)
        return moneySpent, newMint
    
    def issueGreenPointsToCustomer(self, customerAccount:BankAccount, amount:float, originatorTransactionId:str):
        assert isinstance(customerAccount,BankAccount)
        moneySpent = Money(0)
        if self.cryptoWallet.gpBalanceAmount < amount:
            moneySpent, newMint = self.purchaseGreenPointsFromHouse(amount=(amount - self.cryptoWallet.gpBalanceAmount))
        
        assert amount >= 0, 'Retailer can only Issue a Positive number of points.'
        
        if amount > 0 and amount >= self.cryptoWallet.gpBalanceAmount:
            (ethGas, gptTransfered) = self._bank.transferGreenPoints(walletFrom=self.cryptoWallet, walletTo=customerAccount.cryptoWallet, amount=amount, caller=self)
            return (ethGas, gptTransfered, moneySpent)
        return (EtherCoin(0), self.__house.zeroTokenWrapper(), moneySpent)
       


class BankAccountBalanceInCurrency(ISerializableBasic):
    
    def __init__(self, moneyBalance:Money, greenPointsBalance:GreenPointTokensView, accountBank:Bank) -> None:
        super().__init__()
        self._moneyBalance = moneyBalance
        self._greenPointsBalance = greenPointsBalance
        self._bank = accountBank
        
    @property
    def greenPointsBalance(self):
        return self._greenPointsBalance
    
    def view(self, inCurrency:str|None=None):
        bav = BankAccountView(viewCurrency=self._moneyBalance.currency, underlyingMoney=self._moneyBalance, greenPointsBalance=self.greenPointsBalance, bank=self._bank)
        if inCurrency and inCurrency != self._moneyBalance.currency:
            bav = bav.changeCurrency(toCurrency=inCurrency)
        return bav
    
    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return self.view().toDict()
        
        
class BankAccountView(ISerializableBasic):
    def __init__(self, viewCurrency:str, underlyingMoney:Money, greenPointsBalance:GreenPointTokensView,  bank:Bank) -> None:
        assert isinstance(underlyingMoney, Money)
        assert isinstance(greenPointsBalance, GreenPointTokensView)
        assert isinstance(bank, Bank)
        super().__init__()
        self.viewCurrency = viewCurrency
        self._moneyCurrency = underlyingMoney.currency
        self.__underlyingMoney = underlyingMoney
        self._viewMoney = self.__underlyingMoney.copy()
        self._greenPointsBalance = greenPointsBalance
        self._viewGreenPointsBalance = self._greenPointsBalance.valueInPeggedCurrency
        self._viewGreenPointsAmount = self._greenPointsBalance.amount
        self._bank=bank
        
    @staticmethod
    def zero():
        return BankAccountView(viewCurrency='GBP',
                               underlyingMoney=Money(0.0),
                               greenPointsBalance=GreenPointsHouse.getInstance().zeroTokenWrapperView(),
                               bank=AMEX_BANK)
    
    def changeCurrency(self, toCurrency:str):
        assert isinstance(self.__underlyingMoney, Money)
        if self.viewCurrency == toCurrency:
            return self
        self.viewCurrency = toCurrency
        self._viewMoney = self._bank.FXPeek(fxFrom=self.__underlyingMoney.copy(), fxToCurrency=toCurrency)
        assert isinstance(self._viewMoney, Money)
        self._viewGreenPointsBalance = self._bank.FXPeek(fxFrom=self._viewGreenPointsBalance.copy(), fxToCurrency=toCurrency)
        return self
    
    @property
    def gpBalance(self):
        return self._viewGreenPointsBalance
    
    @property
    def viewGreenPoints(self):
        return self._greenPointsBalance
    
    @property
    def gpAmount(self):
        return self._viewGreenPointsAmount
    
    @property
    def moneyBalance(self):
        return self._viewMoney
    
    @property
    def combinedBalance(self):
        return self.moneyBalance + self.gpBalance
    
    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            "viewCurrency": self.viewCurrency,
            "underlyingCurrency": self._moneyCurrency,
            "greenPointsMonetaryValue": self.gpBalance.toDict(),
            "greenPoints": self.gpAmount,
            "moneyBalance": self.moneyBalance.toDict(),
            "combinedBalance": self.combinedBalance.toDict()
        }
        
    # def _isOperable(self, o:Any):
    #     if isinstance(o,type(self)):
    #         return all([bool(o.moneyBalance.currency == self.moneyBalance.currency)])
    #     else:
    #         return False
        
    def __add__(self:Self, o:Any):
        if isinstance(o, type(self)):
            if o.moneyBalance.currency == self.moneyBalance.currency:
                return BankAccountView(viewCurrency=self.moneyBalance.currency, 
                                       underlyingMoney=self.moneyBalance + o.moneyBalance, 
                                       greenPointsBalance=self.viewGreenPoints + o.viewGreenPoints, 
                                       bank=self._bank)
            else:
                bavCcy = o.changeCurrency(toCurrency=self.moneyBalance.currency)
                return self.__add__(bavCcy)
            
    
              
class CostHandler():
    
    def __init__(self, initialCost:Money, startingBalance:BankAccountView) -> None:
        self._initialCost = initialCost
        self._startingBalance = startingBalance
        self._moneyToSend = Money(0.0, initialCost.currency)
        self._greenPointsToSend = GreenPointsHouse.getInstance().zeroTokenWrapperView()
        self._costRemaining = initialCost.copy()
        
    def _getCostRemaining(self):
        return self._costRemaining
    
    costRemaining:Money = property(_getCostRemaining) #type: ignore 
    
    def _getMoneyToSend(self):
        assert self._costRemaining.amount == 0.0
        return self._moneyToSend
    
    moneyToSend:Money = property(_getMoneyToSend) #type: ignore 
    
    def _getGPToSend(self):
        assert self._costRemaining.amount == 0.0
        return self._greenPointsToSend
    
    greenPointsToSend:GreenPointTokensView = property(_getGPToSend) #type: ignore 
    
    def _getStartingBalance(self):
        return self._startingBalance
    
    startingBalance:BankAccountView = property(_getStartingBalance) #type: ignore 
    
    def reduceBy(self, funds:(Money|GreenPointTokensView)):
        if isinstance(funds,Money):
            assert funds >= 0.0
            assignment = min(funds, self._costRemaining)
            self._moneyToSend += assignment
            self._costRemaining -= assignment
        elif isinstance(funds,GreenPointTokensView):
            assert funds.amount >= 0
            assignment = min(funds.valueInPeggedCurrency, self._costRemaining)
            if assignment.amount == 0:
                funds_slice = GreenPointTokensView(0)
            else:
                funds_slice = funds.split(proportions=[(assignment.amount / funds.valueInPeggedCurrency.amount)])[0]
            self._greenPointsToSend += funds_slice
            self._costRemaining -= assignment
        return self


class Bank(Institution):
    def __init__(self, name:str) -> None:
        super().__init__(name=name)
        # BUG: Multiple banks do not have access to eachothers bank account lists at the moment to carry out changes in balance between accounts with differing banks.
        self.debug = debug
        self._name = name
        self.__house:GreenPointsHouse|None = None
        self._accounts:dict[str,BankAccount] = {}
        self._transactionHistory:list[Bank.Transaction] = []
        self._originatorTransactionIdMap:dict[str,str] = {}
        self._treasury:Money = Money(0.0, currency='GBP')
        self._sendMoneyNotifier = Bank.SendMoneyNotifier(self)
        self._bankEventNotifier = Bank.BankEventNotifier(self)
        self._accountBalances:defaultdict[str,Money] = defaultdict(lambda : Money(0.0))
        self._fxAccount:BankAccount = BankAccount(accountHolder=self,bank=self,startingBalance=self._treasury)
        self._oldAccounts:list[BankAccount] = []
        
        
    _FX_CHARGE = 0.0001
    
    def removeAccount(self, account:BankAccount):
        assert account is not None, 'cannot remove a none account'
        if account.id in self._accounts:
            oldAccount = self._accounts.pop(account.id)
            self._accountBalances.pop(account.id)
            self._oldAccounts.append(oldAccount)
        
    
    @property
    def _house(self):
        if self.__house is None:
            self.__house = GreenPointsHouse.getInstance()
        return self.__house
    
    @property    
    def name(self):
        return self._name
    
    @property
    def transactionHistory(self):
        return self._transactionHistory    
    
    @property
    def accountBalances(self):
        return self._accountBalances
    
    @property  
    def sendMoneyNotifier(self):
        return self._sendMoneyNotifier
    
    @property  
    def bankEventNotifier(self):
        return self._bankEventNotifier
    
    def fetchAllTransactionsFromAccount(self, accountId: str):
        return [t for t in self._transactionHistory if t.accountFrom.id == accountId]
    
    def fetchAllTransactionsToAccount(self, accountId: str):
        return [t for t in self._transactionHistory if t.accountTo.id == accountId]
    
    def _getAccountsForOwnerDebug(self, owner:Entity):
        return [a for a in self._accounts.values() if a.owner == owner]
    
    def purchaseSucceeded(self, purchaseId: str, transaction: Any):
        # 'Banks can not make purchases'
        return
    
    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            **super().toDict(),
            "accounts": {a:self._accounts[a].toDict() for a in self._accounts},
            "transactionHistory": [t.toDict() for t in self.transactionHistory],
            "treasury": self._treasury.toDict()
        }
        
    def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            "id": self.id,
            "name":self.name
        }
        
    def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            "id": self.id,
            "name":self.name,
            "accounts": {a:self._accounts[a].toDictUI() for a in self._accounts},
            "transactionHistory": [t.toDictUI() for t in self.transactionHistory],
            "treasury": self._treasury.toDictUI()
        }
    
    def addAccount(self, account: BankAccount, ownerName: str|None=None):
        if ownerName is None:
            ownerName = account._owner.name
        #TODO LATER: Assert that the account is a BankAccount
        self._accounts[account.id] = account
        if account.id not in self._accountBalances:
            self._accountBalances[account.id] = Money(0.0, account.fiatCurrency)
        self._bankEventNotifier.notifyListeners(Bank.Event.account_added, account.id)
        
    def setMoneyAccountBalance(self, bankAccountId:str, startingBalance:Money):
        self._accountBalances[bankAccountId] = startingBalance
        
    def exchange(self, caller:BankAccount, money:Money, toCurrency:str):
        chargeInFromCcy:Money = Bank._FX_CHARGE * money
        chargeInBankCcy = self.FXPeek(chargeInFromCcy, self._treasury.currency) - chargeInFromCcy
        self._treasury += chargeInBankCcy
        amountOut = self.FXPeek(fxFrom=money-chargeInFromCcy, fxToCurrency=toCurrency)
        self._transactionHistory.append(Bank.FXTransaction(
            forAccount=caller, 
            usingBank=self, 
            amount=money,
            bankCharge=chargeInFromCcy,
            amountOut=amountOut))
        return amountOut
        
    def FXPeek(self, fxFrom:Money, fxToCurrency:str):
        if fxFrom.currency == fxToCurrency:
            return Money(fxFrom.amount, fxToCurrency)
        elif fxFrom.amount == 0:
            return Money(0.0, fxToCurrency)
        else:
            raise NotImplementedError(f'Bank.FXFiat between currencies [{fxFrom.currency} -> {fxToCurrency}] not implemented.')
    
    def buyEther(self, wallet:CryptoWallet, amount:float, caller:BankAccount):
        def usingPaymentCallBack(cost:Money, houseAccount:BankAccount):
            if cost.currency == self._accountBalances[caller.id].currency:
                self._accountBalances[caller.id] -= cost
            else:
                self._accountBalances[caller.id] -= self.FXPeek(fxFrom=cost,fxToCurrency=self._accountBalances[caller.id].currency)
            if cost.currency == self._accountBalances[houseAccount.id].currency:
                self._accountBalances[houseAccount.id] += cost
            else:
                self._accountBalances[houseAccount.id] += self.FXPeek(fxFrom=cost,fxToCurrency=self._accountBalances[houseAccount.id].currency)
        gasSpent = EtherCoin(0.0)
        moneySpent=Money(0.0,GreenPointTokens.peggedCurrency) 
        (newMoneySpentGas, ethBought, houseAccount) = self._house.buyEther(wallet=wallet, amount=amount, usingPaymentCallBack=usingPaymentCallBack, caller=self)
        moneySpent += newMoneySpentGas
        _tran = Bank.Transaction(
            wallet.ownerBankAccount, 
            wallet.ownerBankAccount,
            ether=Bank.Transaction.Ether()    
        )
        if ethBought is not None and houseAccount is not None:
            _tran = Bank.Transaction(
                houseAccount, 
                wallet.ownerBankAccount,
                ether=Bank.Transaction.Ether(gas=-gasSpent, ether=ethBought, money=-moneySpent)    
            )
            self._transactionHistory.append(_tran)
        return moneySpent, ethBought, _tran
    
    def buyGreenPoints(self, wallet:CryptoWallet, amount:float, caller:BankAccount):
        def usingPaymentCallBack(cost:Money, houseAccount:BankAccount):
            if cost.currency == self._accountBalances[caller.id].currency:
                self._accountBalances[caller.id] -= cost
            else:
                self._accountBalances[caller.id] -= self.FXPeek(fxFrom=cost,fxToCurrency=self._accountBalances[caller.id].currency)
            if cost.currency == self._accountBalances[houseAccount.id].currency:
                self._accountBalances[houseAccount.id] += cost
            else:
                self._accountBalances[houseAccount.id] += self.FXPeek(fxFrom=cost,fxToCurrency=self._accountBalances[houseAccount.id].currency)
                
        moneySpent=Money(0.0,GreenPointTokens.peggedCurrency) 
        (newMoneySpentGas, gpBought, houseAccount) = self._house.buyGreenPoints(wallet=wallet, amount=amount, usingPaymentCallBack=usingPaymentCallBack, caller=self)
        moneySpent += newMoneySpentGas
        if gpBought is not None and houseAccount is not None:
            self._transactionHistory.append(Bank.Transaction(
                    houseAccount, 
                    wallet.ownerBankAccount,
                    greenpoints=Bank.Transaction.GreenPoints(money=-moneySpent, greenPoints=GreenPointTokensView(gpBought))
            ))
        return moneySpent, gpBought
    
    def transferGreenPoints(self, walletFrom:CryptoWallet, walletTo:CryptoWallet, amount:float, caller:BankAccount):
        def usingPaymentCallBack(cost:Money, houseAccount:BankAccount):
            if cost.currency == self._accountBalances[caller.id].currency:
                self._accountBalances[caller.id] -= cost
            else:
                self._accountBalances[caller.id] -= self.FXPeek(fxFrom=cost,fxToCurrency=self._accountBalances[caller.id].currency)
            if cost.currency == self._accountBalances[houseAccount.id].currency:
                self._accountBalances[houseAccount.id] += cost
            else:
                self._accountBalances[houseAccount.id] += self.FXPeek(fxFrom=cost,fxToCurrency=self._accountBalances[houseAccount.id].currency)
        
        gasSpent = EtherCoin(0.0)
        moneySpent=Money(0.0,GreenPointTokens.peggedCurrency)      
        
        if amount > 0:
            (_topUpEthForGas, _topUpGPForTransfer) = self._house.requireTopUpToTransferGreenPoints(wallet=walletFrom, amount=amount)
            
            if _topUpEthForGas.amount > 0:
                (addMoneySpent, newEther, houseAccount) = self._house.buyEther(wallet=walletFrom, 
                                                                    amount=_topUpEthForGas.amount,
                                                                    usingPaymentCallBack=usingPaymentCallBack,
                                                                    caller=self)
                if newEther is not None:
                    gasSpent -= newEther
                moneySpent += addMoneySpent
                
            if _topUpGPForTransfer > 0:
                (addMoneySpent, newGreenPoints, houseAccount) = self._house.buyGreenPoints(wallet=walletFrom, 
                                                                        amount=_topUpGPForTransfer,
                                                                        usingPaymentCallBack=usingPaymentCallBack,
                                                                        caller=self)
                moneySpent += addMoneySpent
        
        (ethGas, gpt) = self._house.transferGreenPoints(walletFrom=walletFrom, walletTo=walletTo, amountGP=amount, caller=self)
        if gpt is not None:
            self._transactionHistory.append(Bank.Transaction(
                walletFrom.ownerBankAccount, 
                walletTo.ownerBankAccount,
                greenpoints=Bank.Transaction.GreenPoints(gas=gasSpent,
                                                        greenPoints=GreenPointTokensView(gpt),
                                                        money=moneySpent
                                                        )))
            
        return (ethGas, gpt)
    
    def createTransaction(self, accountFrom:BankAccount, accountTo:BankAccount, originatingTransactionId:str):
        return Bank.CreateBankTransaction(bank=self, accountFrom=accountFrom, accountTo=accountTo, originatorTransactionId=originatingTransactionId)
        
    def requestTransferDetails(self, fromBankAccountId:str, originatorTransactionId:str):
        if originatorTransactionId in self._originatorTransactionIdMap.keys():
            transactionId = self._originatorTransactionIdMap[originatorTransactionId]
            return next((t for t in self._transactionHistory if t.id == transactionId and (t.accountFrom.id == fromBankAccountId or t.accountTo.id == fromBankAccountId)))
    
    
        
    class SendMoneyNotifier(Observable):
        def __init__(self, outer:Bank):
            super().__init__()
            self.outer:Bank = outer
            
        def notifyListeners(self, fromBankAccount:BankAccount, toBankAccount:BankAccount, fromGPAccount:BankAccount, originatorTransactionId:str):
            self.setChanged()
            super().notifyObservers(fromBankAccount=fromBankAccount, toBankAccount=toBankAccount, fromGPAccount=fromGPAccount, originatorTransactionId=originatorTransactionId)
    
    
    class Event(enum.Enum):
        transaction_created = 'transaction_created'
        transaction_completed = 'transaction_completed'
        transaction_failed = 'transaction_failed'
        account_added = 'account_added'
    
    class BankEventNotifier(Observable):
        def __init__(self, outer:Bank):
            super().__init__()
            self.outer:Bank = outer
            
        def notifyListeners(self, event_name:Bank.Event, data:Any):
            self.setChanged()
            super().notifyObservers(event_name=event_name, data=data)
    
    
    class CreateBankTransaction(ISerializableBasic):
        def __init__(self, bank:Bank, accountFrom:BankAccount, accountTo:BankAccount, originatorTransactionId:str) -> None:
            self.__house = GreenPointsHouse.getInstance()
            self._bank = bank
            self._accountFrom = accountFrom
            self._accountTo = accountTo
            self._transId = originatorTransactionId
            self._sendFiatAmount = Money(0.0)
            self._sendEtherAmount = EtherCoin(0.0)
            self._sendGreenPointsAmount = GreenPointTransfer(fromObj=self._accountFrom,
                                                             toObj=self._accountTo,
                                                             amount=self.__house.zeroTokenWrapperView())
            
        def toDict(self) -> dict[str, TSTRUC_ALIAS]:
            return {
                'bank': self._bank.toDictLight(),
                'accountFrom': self._accountFrom.toDictLight(),
                'accountTo': self._accountTo.toDictLight(),
                'money': self._sendFiatAmount.toDict(),
                'ether': self._sendEtherAmount.toDict(),
                'greenpoints': self._sendGreenPointsAmount.toDict(),
            }

        
        def withMoneyTransfer(self, amount:Money):
            if not isinstance(amount,Money):
                raise TypeError(f'amount must be {Money.__name__} not a {type(amount).__name__}')
            _sendFiatAmount = Money(0.0)
            accountMoneyFrom = self._accountFrom
            if isinstance(self._accountFrom,GreenPointIssueingAccount):
                accountMoneyFrom = self._accountFrom.supportingBankAccount
                
            if amount is not None and amount.amount > 0:
                if accountMoneyFrom.balance.view().moneyBalance >= amount:
                    _sendFiatAmount = amount
                else:
                    raise InsufficientMoneyError()
                assert isinstance(_sendFiatAmount,Money) and _sendFiatAmount.amount >= 0
            self._sendFiatAmount = _sendFiatAmount
            return self
        
        def withEtherTransfer(self, amount:EtherCoin):
            if not isinstance(amount,EtherCoin):
                raise TypeError(f'amount must be {EtherCoin.__name__} not a {type(amount).__name__}')
            _sendEtherAmount = EtherCoin(0.0)
            if amount is not None and amount.amount > 0:
                if self._accountFrom.cryptoWallet.ethBalance >= amount:
                    _sendEtherAmount = amount
                else:
                    raise InsufficientEtherError(f'{self._accountFrom.owner.name} EthWallet does not contain enough ether to pay ether of transfer')
                assert isinstance(_sendEtherAmount,EtherCoin) and _sendEtherAmount.amount >= 0
            self._sendEtherAmount = _sendEtherAmount
            return self
        
        def withGreenPointTransfer(self, amount: GreenPointTokensView, fromDifferentAccount: BankAccount | None = None):
            if fromDifferentAccount is None:
                fromDifferentAccount = self._accountFrom
            self._accountGPFrom = fromDifferentAccount
            if not isinstance(amount,GreenPointTokensView):
                raise TypeError(f'amount must be {GreenPointTokensView.__name__} not a {type(amount).__name__}')
            _sendGreenPointsAmount:GreenPointTokensView
            if amount is not None and amount.amount > 0:
                if self._accountFrom.cryptoWallet.gpBalanceAmount >= amount.amount:
                    _sendGreenPointsAmount = amount
                else:
                    raise InsufficientGreenPointsError(f'{self._accountFrom.owner.name} does not contain enough GreenPoints to transfer')
                assert isinstance(_sendGreenPointsAmount,GreenPointTokensView) and _sendGreenPointsAmount.amount >= 0
                
                # gasForTransfer = self.__house.calculateGasFeesForTransfer(amount=_sendGreenPointsAmount)    
                self._sendGreenPointsAmount = GreenPointTransfer(fromObj=self._accountFrom,
                                                                  toObj=self._accountTo,
                                                                  amount=_sendGreenPointsAmount)
            return self
        
        def finalise(self):
                # if self._sendGreenPointsAmount.gas.amount != 0:
                #     if (self._accountFrom.cryptoWallet.ethBalance - self._sendEtherAmount) < self._sendGreenPointsAmount.gas.amount:
                #         self._accountFrom.cryptoWallet.buyEther(amount=(self._accountFrom.cryptoWallet.ethBalance - self._sendEtherAmount), fromAccount=self._accountFrom)
                #         if (self._accountFrom.cryptoWallet.ethBalance - self._sendEtherAmount) < self._sendGreenPointsAmount.gas.amount:
                #             raise InsufficientEtherError(f'{self._accountFrom.owner.name} EthWallet does not contain enough ether to pay ether of transfer and the gas fee for the Green Point Transfer')
                    
                return Bank.CreateBankTransaction.FinaliseBankTransaction(createBankTran=self)
                    
            
            
        class FinaliseBankTransaction:
            def __init__(self, createBankTran:Bank.CreateBankTransaction) -> None:
                self._p = createBankTran
                self._gpHouse = GreenPointsHouse.getInstance()
                
            def _emit_event(self, event_name:Bank.Event, data:TSTRUC_ALIAS):
                '''emits an event from the hosting bank which is listened to by the GreenpointsApp'''
                self._p._bank._bankEventNotifier.notifyListeners(event_name, data)
            
            def transact(self):
                # emit transaction creation event
                self._emit_event(Bank.Event.transaction_created, {"transaction": self._p.toDict()})
                
                # Transfer Money
                if self._p._sendFiatAmount.amount != 0:
                    self._p._bank._accountBalances[self._p._accountFrom.id] -= self._p._sendFiatAmount
                    self._p._bank._accountBalances[self._p._accountTo.id] += self._p._sendFiatAmount
                
                #Transfer EtherCoin
                def _transferEther(ether:EtherCoin, toWallet:CryptoWallet):
                    gasSpent = EtherCoin(0)
                    moneySpent = Money(0, currency=GreenPointTokens.peggedCurrency)
                    if ether > 0:
                        _topUp = self._gpHouse.requireTopUpToTransferEther(wallet=self._p._accountFrom.cryptoWallet, amount=ether.amount)
                        if _topUp.amount > 0:
                            def usingPaymentCallBack(cost:Money, houseAccount:BankAccount):
                                if cost.currency == self._p._bank._accountBalances[self._p._accountFrom.id].currency:
                                    self._p._bank._accountBalances[self._p._accountFrom.id] -= cost
                                else:
                                    self._p._bank._accountBalances[self._p._accountFrom.id] -= self._p._bank.FXPeek(fxFrom=cost, 
                                                                                                                    fxToCurrency=self._p._bank._accountBalances[self._p._accountFrom.id].currency)
                                if cost.currency == self._p._bank._accountBalances[houseAccount.id].currency:
                                    self._p._bank._accountBalances[houseAccount.id] += cost
                                else:
                                    self._p._bank._accountBalances[houseAccount.id] += self._p._bank.FXPeek(fxFrom=cost, 
                                                                                                            fxToCurrency=self._p._bank._accountBalances[houseAccount.id].currency)
                                
                                
                            (addMoneySpent, newEther, houseAccount) = self._gpHouse.buyEther(wallet=self._p._accountFrom.cryptoWallet, 
                                                                                amount=_topUp.amount,
                                                                                usingPaymentCallBack=usingPaymentCallBack,
                                                                                caller=self._p._bank
                                                                                )
                            moneySpent += addMoneySpent
                            if newEther is not None:
                                gasSpent -= newEther
                        
                        (etherUsed) = self._gpHouse.transferEther(walletFrom=self._p._accountFrom.cryptoWallet, 
                                                    walletTo=toWallet,amount=ether,
                                                    caller=self._p._bank)
                        if etherUsed is not None:
                            gasSpent += etherUsed
                    return gasSpent, moneySpent
                
                gasSpentOnEthTransfer, moneySpentOnEthTransfer = _transferEther(self._p._sendEtherAmount, self._p._accountTo.cryptoWallet)
                
                # Transfer GP
                def _transferGP(gpAmount:float, toWallet:CryptoWallet):
                    gasSpent = EtherCoin(0)
                    moneySpent = Money(0, currency=GreenPointTokens.peggedCurrency)
                    if gpAmount > 0:
                        def usingPaymentCallBack(cost:Money, houseAccount:BankAccount):
                            if cost.currency == self._p._bank._accountBalances[self._p._accountFrom.id].currency:
                                self._p._bank._accountBalances[self._p._accountFrom.id] -= cost
                            else:
                                self._p._bank._accountBalances[self._p._accountFrom.id] -= self._p._bank.FXPeek(fxFrom=cost, 
                                                                                                                fxToCurrency=self._p._bank._accountBalances[self._p._accountFrom.id].currency)
                            if cost.currency == self._p._bank._accountBalances[houseAccount.id].currency:
                                self._p._bank._accountBalances[houseAccount.id] += cost
                            else:
                                self._p._bank._accountBalances[houseAccount.id] += self._p._bank.FXPeek(fxFrom=cost, 
                                                                                                        fxToCurrency=self._p._bank._accountBalances[houseAccount.id].currency)
                        
                        (_topUpEthForGas, _topUpGPForTransfer) = self._gpHouse.requireTopUpToTransferGreenPoints(wallet=self._p._accountFrom.cryptoWallet, amount=gpAmount)
                        
                        if _topUpEthForGas.amount > 0:
                            (addMoneySpent, newEther, houseAccount) = self._gpHouse.buyEther(wallet=self._p._accountFrom.cryptoWallet, 
                                                                                amount=_topUpEthForGas.amount,
                                                                                usingPaymentCallBack=usingPaymentCallBack,
                                                                                caller=self._p._bank)
                            if newEther is not None:
                                gasSpent -= newEther
                            moneySpent += addMoneySpent
                            
                        if _topUpGPForTransfer > 0:
                            (addMoneySpent, newGreenPoints, houseAccount) = self._gpHouse.buyGreenPoints(wallet=self._p._accountFrom.cryptoWallet, 
                                                                                    amount=_topUpGPForTransfer,
                                                                                    usingPaymentCallBack=usingPaymentCallBack,
                                                                                    caller=self._p._bank)
                            moneySpent += addMoneySpent
                        
                        (etherUsed, gpt) = self._gpHouse.transferGreenPoints(walletFrom=self._p._accountFrom.cryptoWallet, 
                                                            walletTo=toWallet, 
                                                            amountGP=gpAmount,
                                                            caller=self._p._bank)
                        if etherUsed is not None:
                            gasSpent += etherUsed
                    return gasSpent, moneySpent
                
                gasSpentOnGPTransfer, moneySpentOnGPTransfer = _transferGP(self._p._sendGreenPointsAmount.amount.amount, self._p._accountTo.cryptoWallet)
                
                
                # Add To Bank Records
                transaction = Bank.Transaction(
                    accountFrom=self._p._accountFrom,
                    accountTo=self._p._accountTo,
                    money=self._p._sendFiatAmount,
                    ether=Bank.Transaction.Ether(gas=gasSpentOnEthTransfer,
                                                 ether=self._p._sendEtherAmount,
                                                 money=moneySpentOnEthTransfer
                                                 ),
                    greenpoints=Bank.Transaction.GreenPoints(gas=gasSpentOnGPTransfer,
                                                             greenPoints=self._p._sendGreenPointsAmount.amount,
                                                             money=moneySpentOnGPTransfer
                                                             )
                )
                self._p._bank._transactionHistory.append(transaction)
                self._p._bank._originatorTransactionIdMap[self._p._transId] = transaction.id
                
                # Notify Observers of the Bank Transfer
                self._p._bank._sendMoneyNotifier.notifyListeners(fromBankAccount=self._p._accountFrom, 
                                                                toBankAccount=self._p._accountTo,
                                                                fromGPAccount=self._p._accountGPFrom, 
                                                                originatorTransactionId=self._p._transId)
                
                 # emit transaction completion event
                self._emit_event(Bank.Event.transaction_completed, transaction.toDictUI())
                return transaction
                
                
    class Transaction(Identifiable):
        def __init__(self, 
                     accountFrom:BankAccount, 
                     accountTo:BankAccount, 
                     money:Money=Money(0),
                     ether:Bank.Transaction.Ether|None=None,
                     greenpoints: Bank.Transaction.GreenPoints | None = None
                     ) -> None:
            super().__init__()
            self._accountFrom=accountFrom
            self._accountTo=accountTo
            self._money=money
            self._ether=ether if ether is not None else Bank.Transaction.Ether()
            self._greenpoints=greenpoints if greenpoints is not None else Bank.Transaction.GreenPoints()
            self._topUpEtherTransaction:Bank.Transaction|None = None
            #TODO LATER: Implement logic as opposed to being constant
            self.success = True
            
        @property
        def accountFrom(self):
            return self._accountFrom
        
        @property
        def accountTo(self):
            return self._accountTo
        
        @property
        def money(self):
            return self._money
        
        @property
        def ether(self):
            return self._ether
        
        @property
        def greenpoints(self):
            return self._greenpoints
        
        @property
        def topUpEtherTransaction(self):
            return self._topUpEtherTransaction
        
        @topUpEtherTransaction.setter
        def topUpEtherTransaction(self, value:Bank.Transaction):
            self._topUpEtherTransaction = value
            
        @property
        def totalMoneyCost(self):
            return self.ether.money + self.greenpoints.money
        
        @property
        def totalMoneyCostInclTopUps(self):
            return self.ether.money + self.greenpoints.money + (self._topUpEtherTransaction.ether.money if self._topUpEtherTransaction is not None else Money(0.0))
        
        def toDict(self) -> dict[str,TSTRUC_ALIAS]:
            return {
                "id": self.id,
                "accountFrom": self.accountFrom.toDict(),
                "accountTo": self.accountTo.toDict(),
                "money": self.money.toDict(),
                "ether": self.ether.toDict(),
                "greenPoints": self.greenpoints.toDict(),
                "totalMoneyCost": self.totalMoneyCost.toDict(),
                "totalMoneyCostInclTopUps": self.totalMoneyCostInclTopUps.toDict(),
                "topUpEtherTransaction": self.topUpEtherTransaction.toDictLight() if self.topUpEtherTransaction is not None else {}
            }
        
        def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
            return {
                "id": self.id,
                "accountFrom": self.accountFrom.toDictUI(),
                "accountTo": self.accountTo.toDictUI(),
                "money": self.money.toDictUI(),
                "ether": self.ether.toDictUI(),
                "greenPoints": self.greenpoints.toDictUI(),
                "totalMoneyCost": self.totalMoneyCost.toDictUI(),
                "totalMoneyCostInclTopUps": self.totalMoneyCostInclTopUps.toDictUI()
            }
        
        def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
            return {
                "id": self.id
            }
            
        def __str__(self) -> str:
            eth = ''
            gp = ''
            money = ''
            if self._ether.ether.amount != 0:
                eth = f'{self._ether.ether}'
            if self._greenpoints.greenPoints.amount != 0:
                gp = f'{self._greenpoints.greenPoints}'
            if self._money.amount != 0:
                money = f'{self._money}'
            tStr = ' ; '.join((x for x in (money, eth, gp) if x != ''))
            return f'[{tStr}] : ({self._accountFrom.owner.name} -> {self._accountTo.owner.name})'
        
        def __repr__(self) -> str:
            return f'{super().__repr__()} {self.__str__()}'
        
        class Ether(ISerializable):
            def __init__(self, gas:EtherCoin=EtherCoin(0), ether:EtherCoin=EtherCoin(0), money:Money=Money(0)) -> None:
                super().__init__()
                self._gas = gas
                self._ether = ether
                self._money = money
                
            @property
            def ether(self):
                return self._ether
            
            @property
            def gas(self):
                return self._gas
            
            @property
            def money(self):
                return self._money
            
            def toDict(self) -> dict[str,TSTRUC_ALIAS]:
                return {
                    "ether": self.ether.toDict(),
                    "gas": self.gas.toDict(),
                    "money": self.money.toDict()
                }
                
            def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
                return self.toDict()
            
            def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
                return self.toDict()
            
            
        class GreenPoints(ISerializable):
            def __init__(self, gas: EtherCoin = EtherCoin(0), greenPoints: GreenPointTokensView | None = None, money: Money = Money(0)) -> None:
                super().__init__()
                self._gas = gas
                self._greenPoints = greenPoints if greenPoints is not None else GreenPointsHouse.getInstance().zeroTokenWrapperView()
                self._money = money
                
            @property
            def greenPoints(self):
                return self._greenPoints
            
            @property
            def gas(self):
                return self._gas
            
            @property
            def money(self):
                return self._money
            
            def toDict(self) -> dict[str,TSTRUC_ALIAS]:
                return {
                    "greenPoints": self.greenPoints.toDict(),
                    "gas": self.gas.toDict(),
                    "money": self.money.toDict()
                }
                
            def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
                return self.toDict()
            
            def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
                return self.toDict()
            
            
    class FXTransaction(Transaction):
        def __init__(self, forAccount: BankAccount, usingBank: Bank, amount:Money, bankCharge:Money, amountOut:Money) -> None:
            super().__init__(accountFrom=usingBank._fxAccount, accountTo=forAccount, money=amount)
            self.bankCharge = bankCharge
            self.amountFXdLessCharge = amountOut
 
AMEX_BANK = Bank('AMEX')           
            

   


        


 



class Item(Identifiable, ISerializable):
    def __init__(self, name:str, retailer:Retailer, cost:Money, greenPointRewards:float, KGCo2:float, **kwargs:dict) -> None:
        super().__init__()
        self._name = name
        self._retailer = retailer
        self.cost = cost
        # self.costToFirmBaseAccount = self.retailer.bank.FXPeek(fxFrom=cost,
        #                                                        fxToCurrency=self._retailer.accountForPayment(cost).fiatCurrency)
        self.GP:float = greenPointRewards
        self.KGCo2:float = KGCo2
        for (key,val) in kwargs.items(): 
            setattr(self, key, val)
        self.attsKeys = list(kwargs.keys())
    
    @property      
    def name(self):
        return self._name
    
    @property
    def retailer(self):
        return self._retailer
    
    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            **super().toDict(),
            **{
                'name': self.name,
                'retailer': self.retailer.toDictLight(),
                'cost': self.cost.toDict(),
                'KGCo2': self.KGCo2,
                'GP': self.GP
            },
            **{k:getattr(self, k) for k in self.attsKeys}
        }
        
    def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            **super().toDict(),
            'name': self.name,
            'retailer': self.retailer.toDictLight(),
            'cost': self.cost.toDict(),
            'KGCo2': self.KGCo2,
            'GP': self.GP
        }
    
    def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            **super().toDict(),
            'name': self.name
        }
        
    class Transaction(ISerializable, metaclass=abc.ABCMeta):
        def __init__(self, transaction:Bank.Transaction, retailer:Retailer, item:Item) -> None:
            self.transaction = transaction
            self.retailer = retailer
            self.item = item
            
        @property
        def totalGasBoughtWithMoney(self):
            return self.transaction.ether.money + self.transaction.greenpoints.money
            
        @property
        def totalGasUsed(self):
            return self.transaction.ether.gas + self.transaction.greenpoints.gas
        
        def __str__(self):
            return f'{self.retailer.name} sold {self.item.name}'
        
        def toDict(self) -> dict[str,TSTRUC_ALIAS]:
            return {
                "totalGasBoughtWithMoney": self.totalGasBoughtWithMoney.toDict(),
                "totalGasUsed": self.totalGasUsed.toDict(),
                **self.item.toDict()
            }
            
        def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
            return super().toDictUI()
        
        def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
            return super().toDictLight()
        
            
            
class PurchaseDTO(Identifiable, ISerializable):
    def __init__(self, item:Item, customer:Customer, retailer:Retailer, price:Money, gpReward:float, atts:dict, customerAccount:BankAccount):
        super().__init__()
        self.item = item
        self.customer = customer
        self.retailer = retailer
        self.customerAccount = customerAccount
        self.price = price
        self.gpReward = gpReward
        self.atts = atts
    
    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            "customer": self.customer.toDict(),
            "retailer": self.retailer.toDict(),
            "customerAccount": self.customerAccount.toDict(),
            "price": self.price.toDict(),
            "gpReward": self.gpReward,
            **self.atts
        }
        
    def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            "customer": self.customer.toDictLight(),
            "retailer": self.retailer.toDictLight(),
            "customerAccount": self.customerAccount.toDictLight(),
            "price": self.price.toDictLight(),
            "gpReward": self.gpReward
        }
    
    def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            "customer": self.customer.toDictUI(),
            "retailer": self.retailer.toDictUI(),
            "customerAccount": self.customerAccount.toDictUI(),
            "price": self.price.toDictUI(),
            "gpReward": self.gpReward
        }


class TransferType(enum.Enum):
    GreenPointToken=0
    Money=1





class Purchase(Item.Transaction):
    def __init__(self, transaction: Bank.Transaction, retailer: Retailer, item: Item) -> None:
        super().__init__(transaction, retailer, item)
      


class CustomerChosenItem():
    def __init__(self, customer:Customer, itemName:str) -> None:
        self.itemName = itemName
        self._customer = customer
        self._itemBaseSustainabilityRating = 0.0
        
    def withCurrency(self,currency:str):
        self._payWithCurrency = currency
        return self
    
    def forPrice(self,price:float):
        self._payFiatAmount = price
        return self
    
    def withBaselineSustainabiltyRatingForItem(self, baselineSustainabiltyRating:float):
        assert baselineSustainabiltyRating is not None and isinstance(baselineSustainabiltyRating, float)
        self._itemBaseSustainabilityRating = baselineSustainabiltyRating
        return self
        
    def fromRetailer(self, retailer:Retailer):
        self.itemRetailer = retailer
        return CustomerChosenItemWithAttributes(customer=self._customer, 
                                                retailer=self.itemRetailer,
                                                itemName=self.itemName, 
                                                itemCost=Money(amount=self._payFiatAmount,
                                                               currency=self._payWithCurrency),
                                                itemBaseSustainabilityRating=self._itemBaseSustainabilityRating)
                                  
        
class CustomerChosenItemWithAttributes():
    def __init__(self, customer:Customer, retailer:Retailer, itemName:str, itemCost:Money, itemBaseSustainabilityRating:float):
        self._customer = customer
        self._retailer = retailer
        self._itemName = itemName
        self._itemCost = itemCost
        self._itemBaseSustainabilityRating = itemBaseSustainabilityRating
        self._baseline_gpRewardsForItem = 0.0
        self._gpRewardsForItem = 0.0
        self._KGCo2:float = 0.0
        self.atts = {}
        
        
    def withAtt(self, attName:str, attValue:Any):
        self.atts[attName] = attValue
        return self
    
    
    def withGreenPointRewards(self, amountGP:float, retailer:str=''):
        '''Add GP Reward to item in basket after updating the item for the retailer's green points strategy'''
        if not isnum(amountGP):
            print(amountGP)
            print(retailer)
        assert isnum(amountGP)
        self._baseline_gpRewardsForItem = amountGP
        self._gpRewardsForItem:float = np.round(self._baseline_gpRewardsForItem * self._retailer.strategy * 10)
        self._gpRewardsForItem: float = np.round(min(max(
            (self._itemBaseSustainabilityRating + self._retailer.sustainability), -1), 1) * self._gpRewardsForItem, decimals=0)
        return self
        
    def withKGCo2(self, KGCo2:float):
        '''Add KGCo2 cost to item in basket by also the Sustainability Factor (Intercept) of the retailer.'''
        assert KGCo2 is not None and isinstance(KGCo2,float)
        self._KGCo2:float = KGCo2
        return self
        
    def usingAccount(self, bankAccount:BankAccount):
        return CustomerBuyingItem(customer=self._customer,
                                  retailer=self._retailer,
                                  item=Item(name=self._itemName,
                                            retailer=self._retailer,
                                            cost=self._itemCost,
                                            greenPointRewards=self._gpRewardsForItem,
                                            KGCo2=self._KGCo2),
                                  customerAccount=bankAccount)
    
    
class CustomerBuyingItem():
    def __init__(self, customer:Customer, retailer:Retailer, item:Item, customerAccount:BankAccount) -> None:
        self._customer = customer
        self.item = item
        self.itemRetailer = retailer
        self.customerAccount = customerAccount
        
        
    def _getCustomer(self):
        return self._customer
    
    customer:Customer = property(_getCustomer) #type: ignore 
        
        
    def addToBasket(self):
        self.customer.addToBasket(PurchaseDTO(item=self.item, 
                                              customer=self.customer, 
                                              retailer=self.itemRetailer, 
                                              price=self.item.cost, 
                                              gpReward=self.item.GP, 
                                              atts={k:getattr(self.item, k) for k in self.item.attsKeys},
                                              customerAccount=self.customerAccount))
        return self.customer




# Add custom alpha multipliers to reflect setting Green Point Strategy

    
class ControlRetailer:
    def __init__(self, name: str, strategy: RetailerStrategyGPMultiplier, sustainability: RetailerSustainabilityIntercept):
        self.name=name
        self.strategy=strategy
        self.sustainability = sustainability
    
    
    
class Sale(Item.Transaction):
    def __init__(self, transaction: Bank.Transaction, retailer: Retailer, item: Item, greenPointsIssuedForItem: Bank.Transaction.GreenPoints) -> None:
        super().__init__(transaction, retailer, item)
        self.greenPointsIssuedForItem = greenPointsIssuedForItem
        
    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            **super().toDict(),
            "greenPointsIssuedForItem": self.greenPointsIssuedForItem.toDict()
        }
        
    def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            **super().toDictUI(),
            "greenPointsIssuedForItem": self.greenPointsIssuedForItem.toDictUI()
        }
    
    def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            **super().toDictLight(),
            "greenPointsIssuedForItem": self.greenPointsIssuedForItem.toDictLight()
        }




    
    


