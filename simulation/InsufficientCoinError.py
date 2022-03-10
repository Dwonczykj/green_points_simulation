from pprint import PrettyPrinter
from typing import Any
from colorama import Style
import numpy as np

class InsufficientMoneyError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    
    def __str__(self):
        if self.args and isinstance(self.args[0],str):
            return self.args[0]
        else:
            return 'Insufficient Money on account to perform transaction.'

    def __repr__(self):
        return str(type(self))

class InsufficientEtherError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    
    def __str__(self):
        if self.args and isinstance(self.args[0],str):
            return self.args[0]
        else:
            return 'Insufficient Ether to perform transaction.'

    def __repr__(self):
        return str(type(self))
    
class InsufficientGasFeeError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    
    def __str__(self):
        if self.args and isinstance(self.args[0],str):
            return self.args[0]
        else:
            return 'Insufficient GasFees passed to Green Point Transfer to perform transaction.'

    def __repr__(self):
        return str(type(self))
    
class InsufficientGreenPointsError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    
    def __str__(self):
        if self.args and isinstance(self.args[0],str):
            return self.args[0]
        else:
            return 'Insufficient Green Points on account to perform transaction'

    def __repr__(self):
        return str(type(self))

    
class PurchaseItemTransactionError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    
    def __str__(self):
        if self.args and isinstance(self.args[0],str):
            return self.args[0]
        else:
            return 'Purchase Transaction failed'

    def __repr__(self):
        return str(type(self))
    
class BankTransactionFailedError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    
    def __str__(self):
        if self.args and isinstance(self.args[0],str):
            return self.args[0]
        else:
            return 'Bank Transaction failed'

    def __repr__(self):
        return str(type(self))
      

class TodoImplementError(NotImplementedError):
    pass

class DoubleBookingTransactionMisMatchException(Exception):
    def __init__(self, transactionMovesDebug:dict={}, *args: object) -> None:
        super().__init__(*args)
        self.transactionMovesDebug = transactionMovesDebug

    def __str__(self):
        if self.args and isinstance(self.args[0], str):
            return self.args[0] + '\n\twith debug information:\n' + Style.DIM + PrettyPrinter(indent=2, sort_dicts=False).pformat(self.transactionMovesDebug) + Style.NORMAL
        else:
            return 'Two sides of double booking of transaction don\'t offset one another.'

    def __repr__(self):
        return str(type(self).__name__) + self.__str__()

class GreenPointsLostInDoubleBookingTransactionException(Exception):
    def __init__(self, transactionMovesDebug:dict={}, *args: object) -> None:
        super().__init__(*args)
        self.transactionMovesDebug = transactionMovesDebug

    def __str__(self):
        if self.args and isinstance(self.args[0], str):
            return self.args[0] + '\n\twith debug information:\n' + Style.DIM + PrettyPrinter(indent=2,sort_dicts=False).pformat(self.transactionMovesDebug) + Style.NORMAL
        else:
            return 'Green points on the two sides of double booking of transaction don\'t offset one another.'

    def __repr__(self):
        return str(type(self).__name__) + self.__str__()
    
class NotAllowedError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __str__(self):
        if self.args and isinstance(self.args[0], str):
            return self.args[0]
        else:
            return 'Not allowed!'

    def __repr__(self):
        return str(type(self).__name__) + self.__str__()
    

class CheckSameTypeError(TypeError):
    def __init__(self, objA:Any, objB:Any, *args: object) -> None:
        super().__init__(*args)
        self.objA=objA
        self.objB=objB

    def __str__(self):
        if self.args and isinstance(self.args[0], str):
            return f'Type:{type(self.objA).__name__} != Type:{type(self.objA).__name__}; ' + self.args[0]
        else:
            return f'Type:{type(self.objA).__name__} != Type:{type(self.objA).__name__}'

    def __repr__(self):
        return str(type(self).__name__) + self.__str__()
    
    @staticmethod
    def check(objA:Any,objB:Any,raiseErr:bool=True):
        if type(objA) == type(objB):
            return True
        elif np.issubclass_(np.float_, type(objA)) and np.issubclass_(np.float_, type(objB)):
            return True
        elif raiseErr:
            raise CheckSameTypeError(objA=objA,objB=objB)
        else:
            return False
