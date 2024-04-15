from typing import Callable
import carrotlib as cl
import raylib as rl

def window_size():
    return (rl.GetScreenWidth(), rl.GetScreenHeight())

# 电脑调试用该常量设置design_size的大小
WINDOW_SIZE_ON_WIN32_INIT = (int(2560/2), int(1600*0.8))

# 移动端调试用该常量设置design_size的大小
VIEWPORT_WIDTH_INIT = 1000

    
class _VWVH():
    '''
    视口的宽高只允许右乘, 其他所有与基本类型的运算都是不允许的
    '''

    def __init__(self):
        self.getter = None
    
    def raise_exception(self, experssion_name, other):
        raise TypeError(f"Operation not allowed:  '{self.__class__.__name__.lower()}.{experssion_name}({other})'")
    def __mul__(self, other):
        self.raise_exception('__mul__', other)
    
    def __rmul__(self, other):
        return int(self.getter() * other)
    
    def __add__(self, other):
        if not isinstance(other, _VWVH):
            self.raise_exception('__add__', other)
        
        return int(self.getter() + other.getter())
    
    def __radd__(self, other):
        if not isinstance(other, _VWVH):
            self.raise_exception('__radd__', other)
        
        return int(self.getter() + other.getter())
    
    def __sub__(self, other):
        if not isinstance(other, _VWVH):
            self.raise_exception('__sub__', other)
        
        return int(self.getter() - other.getter())
    
    def __rsub__(self, other):
        if not isinstance(other, _VWVH):
            self.raise_exception('__rsub__', other)
        
        return int(self.getter() - other.getter())
    
    def __truediv__(self, other):
        self.raise_exception('__truediv__', other)
    
    def __rtruediv__(self, other):
        self.raise_exception('__rtruediv__', other)
    
    def __floordiv__(self, other):
        self.raise_exception('__floordiv__', other)
    
    def __rfloordiv__(self, other):
        self.raise_exception('__rfloordiv__', other)
    
    def __mod__(self, other):
        self.raise_exception('__mod__', other)
    
    def __rmod__(self, other):
        self.raise_exception('__rmod__', other)
    
    def __int__(self):
        return int(self.getter())
    
    @property
    def int(self):
        return self.__int__()


class VW(_VWVH):
    def __init__(self):
        super().__init__()
        self.getter = rl.GetScreenWidth

class VH(_VWVH):
    def __init__(self):
        super().__init__()
        self.getter = rl.GetScreenHeight

# 支持运算的屏幕宽高
vw = VW()
vh = VH()
