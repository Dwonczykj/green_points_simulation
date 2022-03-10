import logging
from typing import Any, Callable
from colorama import Fore, Style


def logmethodaccess(f:Callable):
    def wrapWithLog(*args,**kwargs):
        logging.debug(Fore.BLUE + Style.DIM + f'{f.__name__} accessed' + Style.RESET_ALL)
        return f(*args,**kwargs)
    return wrapWithLog

class logpropertyaccess(property):
    def __init__(self, fget: Callable[[Any], Any] | None = ..., fset: Callable[[Any, Any], None] | None = ..., fdel: Callable[[Any], None] | None = ..., doc: str | None = ...) -> None:
        super().__init__(fget, fset, fdel, doc)
        logging.debug(Fore.BLUE + Style.DIM +
                      f'{self.__repr__} accessed' + Style.RESET_ALL)
