from __future__ import annotations
from typing_extensions import Self

# class classproperty(property):
#     def __get__(self, cls, owner):
#         return classmethod(self.fget).__get__(None, owner)()
    
# from typing import Generic, Type, TypeVar

# TSGL = TypeVar('TSGL', bound='Singleton')

# class Singleton():
#     '''Singleton: Call getInstance() to get the House'''
#     __instance
    
#     @classmethod 
#     def getInstance(cls: Type[TSGL]):
#         """ Static access method. """
#         if cls.__instance == None:
#             cls()
#         return cls.__instance
    
#     def __init__(self:TSGL):
#         """ Virtually private constructor. """
#         if type(self).__instance != None:
#             raise Exception(f"{type(self)} class is a singleton!")
#         else:
#             type(self).__instance = self
            
            
# class Test(Singleton):
    
#     def dosomething(self):
#         pass
    
# x = Test.getInstance()

class SingletonFactory:
    
    @staticmethod
    def create():
        pass

class SingletonMeta(type):
    __instance:SingletonMeta|None=None

    @property
    def instance(self:Self):
        assert self.__instance is not None
        return self.__instance
    
    def create(cls):
        return SingletonMeta.__instance
    
    
    
class SingletonNot(metaclass=SingletonMeta):
    '''Not a singleton, just being used to work it out'''
    __metaclass__=SingletonMeta
    
    @property
    def test(self):
        return SingletonNot.__instance == SingletonNot.instance