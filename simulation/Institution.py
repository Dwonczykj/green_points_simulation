
import abc
from typing import Any
from ISerializable import ISerializable

from Identifiable import Identifiable

class Institution(Identifiable, ISerializable):
    def __init__(self, name:str) -> None:
        super().__init__()
        self._name = name
        
    def toDict(self):
        return {
            **super().toDict(),
            "name": self.name
        }
        
    def toDictLight(self):
        return self.toDict()
    
    def toDictUI(self):
        return self.toDict()
        
    @property    
    def name(self):
        return self._name
    
    @abc.abstractmethod
    def purchaseSucceeded(self, purchaseId:str, transaction:Any):
        pass
    
    