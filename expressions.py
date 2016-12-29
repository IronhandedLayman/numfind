#!/opt/local/bin/python

import math

class Expression:
    _memorepr = None
    _memohash = None
    def complexity(self):
        return 1

    def value(self):
        return 0.0

    def __lt__(self, other):
        return str(self)<str(other)

    def __eq__(self, other):
        return str(self)==str(other)

    def __hash__(self):
        if self._memohash is None:
            self._memohash = str(self).__hash__()
        return self._memohash

    def __str__(self):
        return "0"

    def __repr__(self):
        if self._memorepr is None:
            self._memorepr = "Expr("+str(self)+")"
        return self._memorepr

class Constant(Expression):
    def __init__(self, name, inner_val):
        self.name = name
        self.inner_val = inner_val
        self._memorepr = name
        self._memostr = name

    def complexity(self):
        return 1

    def value(self):
        return self.inner_val

    def __str__(self):
        return self.name

class Unary(Expression):
    def __init__(self, exprName, innerExpr, complexFunc, exprFunc):
        self.expr_name = exprName
        self.inner_expr = innerExpr
        self.complex_func = complexFunc
        self.expr_func = exprFunc
        self._memovalue = None
        self._memocomp = None
        self._memostr = None

    def complexity(self):
        if self._memocomp is None:
            self._memocomp = self.complex_func(self.inner_expr.complexity())
        return self._memocomp

    def value(self):
        if self._memovalue is None:
            return self.expr_func(self.inner_expr.value())
        return self._memovalue

    def __str__(self):
        if self._memostr is None:
            self._memostr = "{0}({1})".format(self.expr_name, str(self.inner_expr))
        return self._memostr

class Binary(Expression):
    def __init__(self, exprName, innerExprL, innerExprR, complexFunc, exprFunc, infixFlag):
        self.expr_name = exprName
        self.inner_expr_left = innerExprL
        self.inner_expr_right = innerExprR
        self.complex_func = complexFunc
        self.expr_func = exprFunc
        self.infix_flag = infixFlag
        self._memovalue = None
        self._memocomp = None
        self._memostr = None

    def complexity(self):
        if self._memocomp is None:
            self._memocomp = self.complex_func(self.inner_expr_left.complexity(), self.inner_expr_right.complexity())
        return self._memocomp

    def value(self):
        if self._memovalue is None:
            self._memovalue = self.expr_func(self.inner_expr_left.value(),self.inner_expr_right.value())
        return self._memovalue 

    def __str__(self):
        if self._memostr is None:
            if self.infix_flag:
                self._memostr = "({1}){0}({2})".format(self.expr_name, str(self.inner_expr_left), str(self.inner_expr_right))
            else:    
                self._memostr = "{0}({1},{2})".format(self.expr_name, str(self.inner_expr_left), str(self.inner_expr_right))
        return self._memostr

def IntConst(n):
    return Constant(str(n),float(n))

def SqrtExpr(x):
    return Unary("sqrt", x, lambda x:x+1, math.sqrt)

def SinExpr(x):
    return Unary("sin", x, lambda x:x+1, math.sin)

def CosExpr(x):
    return Unary("cos", x, lambda x:x+1, math.cos)

def TanExpr(x):
    return Unary("tan", x, lambda x:x+1, math.tan)

def LogExpr(x):
    return Unary("log", x, lambda x:x+1, math.log)

def AddExpr(x,y):
    return Binary("+", x, y, lambda x,y:(x+y)+2, lambda x,y:x+y, True)

def SubtractExpr(x,y):
    return Binary("-", x, y, lambda x,y:(x+y)+2, lambda x,y:x-y, True)

def MultExpr(x,y):
    return Binary("*", x, y, lambda x,y:(x+y)+2, lambda x,y:x*y, True)

def DivExpr(x,y):
    return Binary("/", x, y, lambda x,y:(x+y)+2, lambda x,y:x/y, True)

def PowExpr(x,y):
    return Binary("^", x, y, lambda x,y:(x+y)+2, lambda x,y:x**y, True)
