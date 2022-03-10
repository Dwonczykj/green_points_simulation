from __future__ import annotations
from typing import Type

class Singleton:
    '''Singleton: Call getInstance() to get the House'''
    __instance:Singleton = None
    
    
    
    @staticmethod 
    def getInstance(type:Type=None):
        """ Static access method. """
        if type is None:
            type = Singleton
        assert issubclass(type,Singleton), f'{type} must be a subclass of Singleton'
        if Singleton.__instance == None:
            Singleton()
        return Singleton.__instance
    
    def __init__(self):
        """ Virtually private constructor. """
        if Singleton.__instance != None:
            raise Exception(type(self).__name__ + " class is a singleton!")
        else:
            Singleton.__instance = self
            
class DerivedSingleton(Singleton):
    pass


class SingletonFactory:
    def __init__(self) -> None:
        raise NotImplementedError('Cannot instantiate a static class')
    
    def _checkTypeAIsDerivedClassFromTypeB(A:Type,B:Type):
        '''Function to check whether A is a subclass of B, i.e. like definition: 
            class A(B): 
                pass
        '''
        return B.__name__ in (cls.__name__ for  cls in A.__mro__)
    
    def createSingletonFor(type:Type[Singleton]):
        assert SingletonFactory._checkTypeAIsDerivedClassFromTypeB(type, Singleton)
        type.
        

x = SingletonFactory.createSingletonFor(type=DerivedSingleton)

pass