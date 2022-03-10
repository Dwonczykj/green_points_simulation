from __future__ import annotations

import abc
from typing import Any, Callable, Iterable, Sequence, Union
from typing import TypeGuard, TypeVar, Type, Set
# from typeguard import check_argument_types, check_return_type, typechecked # https://typeguard.readthedocs.io/en/latest/userguide.html    
from typing_extensions import Self
import json

TVALUE = Union[str, bytes, int, float, bool]
TSTRUC = Union[str, bytes, int, float, bool, Iterable[Union[str, bytes, int, float, bool]], dict[(str|int|float),Union[str, bytes, int, float, bool]]]
TSTRUC_ALIAS = (TSTRUC|list[TSTRUC]|dict[str,TSTRUC])

_T = TypeVar("_T")
_TKEY = TypeVar("_TKEY",str,float,bool)
def is_set_of(val: Set[Any], type: Type[_T]) -> TypeGuard[Set[_T]]:
    return all(isinstance(x, type) for x in val)

def is_iterable_of(val: Iterable[Any], type: Type[_T]) -> TypeGuard[Iterable[_T]]:
    return all(isinstance(x, type) for x in val)

def is_dict_of(val: dict[Any,Any], typeKey: Type[_TKEY], typeVal: Type[_T]) -> TypeGuard[dict[_TKEY,_T]]:
    return all(isinstance(x, typeKey) for x in val.keys()) and all(isinstance(x, typeVal) for x in val.values())

def _is_set_of_example():
    x = {1,4,5,2}
    if is_set_of(x, int):
        y = [i for i in x] # type checking exists here for compiler annotations.
        assert isinstance(y[0], int)
    y2:dict = {'hello':3}
    if is_iterable_of(y2, Any):
        x2 = y2
        

   
class ISerializable(metaclass=abc.ABCMeta):
    
    # Mixins do not have constructors specified
    # def __init__(self) -> None:
    #     pass
    
    @staticmethod
    def _toSer(x:Any):
        if isinstance(x, TVALUE):
            return x
        elif isinstance(x, dict):
            return {k:ISerializable._toSer(x[k]) for k in x.keys() if ISerializable._canSer(x[k])}
        elif isinstance(x, Iterable):
            if is_iterable_of(x, TVALUE):
                return x
            elif all((isinstance(i, Iterable) for i in x)):
                return [ISerializable._toSer(i) for i in x]
        elif isinstance(x, ISerializable):
            return ISerializable._toSer(x)
        else:
            pass
    
    @staticmethod    
    def _canSer(x:Any):
        if isinstance(x,Callable):
            return False
        elif isinstance(x, TVALUE):
            return True
        elif isinstance(x, dict):
            return True
        elif isinstance(x, Iterable):
            if all((isinstance(i, TVALUE) for i in x)):
                return True
            elif all((isinstance(i, Iterable) for i in x)):
                return True
        elif isinstance(x, ISerializable):
            return True
        
        return False
    
    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return {
            m : getattr(self, m) 
            for m in dir(self) 
            if (not m.startswith('_')) and ISerializable._canSer(getattr(self, m))
        }
        # d = {}
        # for m in dir(self):
        #     if m.startswith('_'):
        #         continue
        #     x = getattr(self, m)
        #     if ISerializable._canSer(x):
        #         d[m] = x
            
        # return d
        
    @abc.abstractmethod
    def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
        '''returns viewable information on an object that would not necessarily be sufficient to create a copy of the object'''
        return self.toDict()
    
    @abc.abstractmethod
    def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
        '''returns light information for object identification at runtime'''
        return self.toDict()
    
    def toJson(self:Self):
        '''Method to make any class that inherits ISerializable json encodable'''
        # return json.dumps(self, default=lambda o: o.__dict__)
        return json.dumps(self.toDict())
    
TSERIALIZABLE_ALIAS = (TSTRUC_ALIAS|
                       ISerializable|
                       Iterable[TSTRUC_ALIAS|ISerializable]|
                       dict[str,(TSTRUC_ALIAS|ISerializable)])


class ISerializableBasic(ISerializable):
    
    def toDict(self) -> dict[str,TSTRUC_ALIAS]:
        return super().toDict()
    
    
    def toDictLight(self) -> dict[str,TSTRUC_ALIAS]:
        '''returns light information for object identification at runtime'''
        return self.toDict()
    
    def toDictUI(self) -> dict[str,TSTRUC_ALIAS]:
        '''returns viewable information on an object that would not necessarily be sufficient to create a copy of the object'''
        return self.toDict()
    

class SerializableList(list[(TSTRUC_ALIAS|ISerializable)], ISerializable):
    # @typechecked
    @staticmethod
    def _dictToDict(d:dict[str,(ISerializable|TSTRUC_ALIAS)]):
        if is_dict_of(d, str, TSTRUC_ALIAS):
            return d
        elif is_dict_of(d, str, ISerializable):
            return {
                k:v.toDict()
                for k,v in d.items()
            }
        else:
            return {
                k:(v.toDict() if isinstance(v,ISerializable) else v)
                for k,v in d.items()
            }
            
    # @typechecked
    @staticmethod
    def _iterableToDict(l:Iterable[(ISerializable|TSTRUC_ALIAS)]):
        if is_iterable_of(l, str):
            if isinstance(l,dict):
                nd:dict[str,(ISerializable|TSTRUC_ALIAS)] = {k:v for k,v in l.items()}
                return SerializableList._dictToDict(nd)
            else:
                return l
        elif is_iterable_of(l, TSTRUC_ALIAS):
            return l
        elif is_iterable_of(l, ISerializable):
            return [v.toDict() for v in l]
        else:
            return [(v.toDict() if isinstance(v,ISerializable) else v) for v in l]
    
    # @typechecked
    @staticmethod
    def _toSerialized(a:(TSTRUC_ALIAS|ISerializable)):
        if isinstance(a, TVALUE):
            return a
        elif isinstance(a, dict):
            if is_dict_of(a, str, (ISerializable|TSTRUC_ALIAS)):
                return SerializableList._dictToDict(a)
        elif isinstance(a, Iterable):
            return SerializableList._iterableToDict(a)
        else:
            raise TypeError(f'Arg of type {type(a)} cannot be used in {Iterable[TSTRUC_ALIAS]}')
        
    # @typechecked
    def __init__(self, l:Iterable[(TSTRUC_ALIAS|ISerializable)]):
        super().__init__(l)
    
    def toSerialized(self):
        return [SerializableList._toSerialized(a) for a in self]
        
    def toJson(self):
        return [(a.toDict() if isinstance(a,ISerializable) else a) for a in self]

    def toJsonLight(self):
        '''returns light information for object identification at runtime'''
        return [(a.toDictLight() if isinstance(a,ISerializable) else a) for a in self]
    
    def toJsonUI(self):
        '''returns viewable information on an object that would not necessarily be sufficient to create a copy of the object'''
        return [(a.toDictUI() if isinstance(a,ISerializable) else a) for a in self]
    
    def toDict(self):
        return self.toJson()
    
    def toDictUI(self):
        return self.toJsonUI()
    
    def toDictLight(self):
        return self.toJsonLight()
    