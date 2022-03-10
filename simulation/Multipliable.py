from __future__ import annotations
from typing import Union

# from typing import TypeVar
from typing_extensions import Self
import abc

# T = TypeVar('T', bound='Multipliable')

Numeric = Union[float,int]

class Multipliable:
    def __init__(self, amount:Numeric) -> None:
        # super().__init__(name='Multipliable',bases=(Multipliable))
        self._amount = amount
    
    @property    
    def amount(self):
        return self._amount
        
    @abc.abstractclassmethod
    def _copyFromMultipliable(self:Self, multi:Multipliable) -> Self:
        raise NotImplementedError()
    
    @abc.abstractclassmethod
    def _assertOtherArgIsOperatable(self:Self, other:(Self|Numeric)):
        if isinstance(other,Numeric) or isinstance(other,int) or isinstance(other,Multipliable):
            return True
        raise TypeError(type(other))
        # assert other.gpType == self.gpType, f'GreenPoints must have same gpTypes for operations: [self={self.gpType.retailer.name}, other={other.gpType.retailer.name}]'
    
    def __add__(self:Self, other:(Self|Numeric)) -> Self:
        if isinstance(other, Multipliable):
            self._assertOtherArgIsOperatable(other)
            return self._copyFromMultipliable(Multipliable(self.amount + other.amount))
            # self._amount = self._amount + other._amount
            # return self
        elif isinstance(other,Numeric):
            return self._copyFromMultipliable(Multipliable(self.amount + other))
            # self._amount = self._amount + other
            # return self
        raise NotImplementedError(f'Args of type {type(other)} cannot be operatored to objects of type {type(self)}')
        
    def __sub__(self:Self, other:(Self|Numeric)) -> Self:
        assert isinstance(self, Multipliable)
        if isinstance(other, Multipliable):
            self._assertOtherArgIsOperatable(other)
            return self._copyFromMultipliable(Multipliable(self._amount - other._amount))
        elif isinstance(other,Numeric):
            return self._copyFromMultipliable(Multipliable(self._amount - other))
        raise NotImplementedError(f'Args of type {type(other)} cannot be operatored to objects of type {type(self)}')
    
    def __mul__(self:Self, other:(Self|Numeric)) -> Self:
        assert isinstance(self, Multipliable)
        if isinstance(other, Multipliable):
            self._assertOtherArgIsOperatable(other)
            return self._copyFromMultipliable(Multipliable(self.amount * other.amount))
        elif isinstance(other,Numeric):
            return self._copyFromMultipliable(Multipliable(self.amount * other))
        raise NotImplementedError(f'Args of type {type(other)} cannot be operatored to objects of type {type(self)}')
        
    def __neg__(self:Self) -> Self:
        return self._copyFromMultipliable(Multipliable(-self.amount))
        
    def __le__(self, other:(Self|Numeric)):
        if isinstance(other,type(self)):
            self._assertOtherArgIsOperatable(other)
            return self.amount <= other.amount
        elif isinstance(other,Numeric):
            return self.amount <= other
        else:
            raise TypeError(other)
    
    def __lt__(self, other:(Self|Numeric)):
        if isinstance(other,type(self)):
            self._assertOtherArgIsOperatable(other)
            return self.amount < other.amount
        elif isinstance(other,Numeric):
            return self.amount < other
        else:
            raise TypeError(other)
        
    def __ge__(self, other:(Self|Numeric)):
        if isinstance(other,type(self)):
            self._assertOtherArgIsOperatable(other)
            return self.amount >= other.amount
        elif isinstance(other,Numeric):
            return self.amount >= other
        else:
            raise TypeError(other)
        
    def __gt__(self, other:(Self|Numeric)):
        if isinstance(other,type(self)):
            self._assertOtherArgIsOperatable(other)
            return self.amount > other.amount
        elif isinstance(other,Numeric):
            return self.amount > other
        else:
            raise TypeError(other)
        
    def __imul__(self, other:(Self|Numeric)):
        return self.__mul__(other)
    
    def __rmul__(self, other:(Self|Numeric)):
        return self.__mul__(other)
    
    def __iadd__(self, other:(Self|Numeric)):
        return self.__add__(other)
    
    def __radd__(self, other:(Self|Numeric)):
        return self.__add__(other)
    
    def __isub__(self, other:(Self|Numeric)):
        return self.__sub__(other)
    
    def __rsub__(self:Self, other:(Self|Numeric)) -> Self:
        assert isinstance(self, Multipliable)
        if isinstance(other, Multipliable):
            return other.__sub__(self)
        elif isinstance(other,int) or isinstance(other,Numeric): 
            return self._copyFromMultipliable(Multipliable(other - self.amount))
        raise NotImplementedError(f'Args of type {type(other)} cannot be operatored to objects of type {type(self)}')
        
    
    def __str__(self):
        return f'{type(self).__name__}_{self.amount}'
    
    def __repr__(self):
        return f'{type(self).__name__}_{self.amount}'
    
class Divideable(Multipliable):
    
    def __init__(self, amount: Numeric) -> None:
        super().__init__(amount)
    
    @abc.abstractclassmethod
    def _copyFromMultipliable(self:Self, multi:Multipliable) -> Self:
        raise NotImplementedError()
    
    def __truediv__(self:Self, other:(Self|Numeric)) -> Self:
        assert isinstance(self, Divideable)
        if isinstance(other, Divideable):
            self._assertOtherArgIsOperatable(other)
            return self._copyFromMultipliable(Multipliable(self.amount / other.amount))
        elif isinstance(other,Numeric):
            return self._copyFromMultipliable(Multipliable(self.amount / other))
        raise NotImplementedError(f'Args of type {type(other)} cannot be operatored to objects of type {type(self)}')
        
    def __itruediv__(self, other:(Self|Numeric)):
        return self.__truediv__(other)
    
    def __rtruediv__(self, other:(Self|Numeric)):
        if isinstance(other,Divideable):
            return other.__truediv__(self)
        elif isinstance(other,int) or isinstance(other,Numeric):
            return self._copyFromMultipliable(Divideable(other / self.amount))
        raise TypeError(type(other))