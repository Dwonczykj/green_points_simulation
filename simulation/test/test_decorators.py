from functools import wraps
from threading import local
from typing import Any, Callable, TypeVar

TARG = TypeVar('TARG')
TKWARG = TypeVar('TKWARG')
TRES = TypeVar('TRES')


def repeat(times: int | Callable[...[Any], TRES] = 5) -> Callable[...[Any], TRES] | Callable[[Callable[...[Any], TRES]], Callable[...[Any], TRES]]:
    ''' call a function a number of times '''
    _times = times if isinstance(times,int) else 5

    def decorate(fn: Callable[...[Any], TRES]) -> Callable[...[Any], TRES]:
        @wraps(fn)
        def wrapper(*args:TARG, **kwargs:TKWARG) -> TRES:
            result:TRES
            for _ in range(_times):
                result = fn(*args, **kwargs)
            else:
                result = fn(*args, **kwargs)
            return result
        return wrapper
    
    return decorate if isinstance(times,int) else decorate(times)
    
T = TypeVar('T')  

@repeat
def say1(message:T) -> T:
    ''' print the message 
    Arguments
        message: the message to show
    '''
    print(message)
    return message

x1 = say1('Hi there')

@repeat(10)
def say(message:T) -> T:
    ''' print the message 
    Arguments
        message: the message to show
    '''
    print(message)
    return message



x = say('Hello')
