
from typing_extensions import Self
import uuid

class Identifiable:
    def __init__(self) -> None:
        self.__id = str(uuid.uuid4()) 
        
    @property
    def id(self):
        return self.__id
    
    def toDict(self):
        return {
            "id": self.id
        }
    
    def __eq__(self, __o: object) -> bool:
        return bool(isinstance(__o,Identifiable) and self.id == __o.id)
    
    def _withId(self:Self, id:str, ifTrue:bool):
        assert id is not None and id != ''
        try:
            assert isinstance(uuid.UUID(hex=('{'+ id +'}')), uuid.UUID)
        except:
            return self
        self.__id = id
        return self