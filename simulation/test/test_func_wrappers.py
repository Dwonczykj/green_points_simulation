import pytest
from func_wrappers import _MAX_RECURSION_FUNC, recursion_detector


@recursion_detector()
def f1(i:int):
    return f1(i+1)


@recursion_detector()
def f2(i:int):
    return f2(i+1) if i < _MAX_RECURSION_FUNC else 0

@recursion_detector()
def f3(i:int):
    return f3(i+1) if i < (_MAX_RECURSION_FUNC + 1) else 0

@recursion_detector(max_recursion_limit=30)
def f4(i:int):
    return f4(i+1) if i < 30 else 0

@recursion_detector(max_recursion_limit=10)
def f5(i:int):
    return f5(i+1) if i < 11 else 0



def test_infinite_recursion_throws():
    with pytest.raises(RuntimeError):
        f1(1)
    pass

def test_doesnt_break_default_recursion_limit():
    f2(1)
    pass

def test_does_break_default_recursion_limit():
    with pytest.raises(RuntimeError):
        f3(1)
        
def test_doesnt_break_custom_recursion_limit():
    f4(1)
    pass

def test_does_break_custom_recursion_limit():
    with pytest.raises(RuntimeError):
        f5(1)

