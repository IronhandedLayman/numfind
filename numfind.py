#!/opt/local/bin/python

import argparse
import math

class Expression:
    def complexity(self):
        return 1

    def value(self):
        return 0.0

    def __str__(self):
        return "0"

class Constant(Expression):
    def __init__(self, name, inner_val):
        self.name = name
        self.inner_val = inner_val

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

    def complexity(self):
        return self.complex_func(self.inner_expr.complexity())

    def value(self):
        return self.expr_func(self.inner_expr.value())

    def __str__(self):
        return "{0}({1})".format(self.expr_name, str(self.inner_expr))

def IntConst(n):
    return Constant(str(n),n)

def SqrtExpr(x):
    return Unary("sqrt", x, lambda x:x+1, lambda x:math.sqrt(x))

class NumFinder:
    def __init__(self):
        self.constants = set()
        self.max_complexity = 30
        self.reset_constants()

    def reset_constants(self):
        self.constants = set()
        self.add_constant(Constant("pi",math.pi))
        self.add_constant(Constant("e",math.e))
        for n in range(1,101):
            self.add_constant(IntConst(n))

    def add_constant(self, expr):
        self.constants.add(expr)

    def search_heuristic(self, X, Y):
        try:
            return math.log(1/abs(X-Y))
        except:
            return -999 #TODO: does this constant even make sense?

    def find(self, X):
        bfsf = None
        heur = None
        for expr in self.constants:
            constHeur = self.search_heuristic(expr.value(),X)
            if heur is None or heur < constHeur:
                heur=constHeur
                bfsf=expr
            sqrtExpr = SqrtExpr(expr)
            sqrtHeur = self.search_heuristic(sqrtExpr.value(),X)
            if heur is None or heur < sqrtHeur:
                heur=sqrtHeur
                bfsf=sqrtExpr

        return (bfsf, heur)

def main():
    parser = argparse.ArgumentParser(description='Find numbers close to a given constant or expression')
    parser.add_argument('inval', metavar='X', type=float, nargs=1, help='the number to approximate with a constant')
    pargs = parser.parse_args()
    X = pargs.inval[0]
    print("You're looking for: {0}".format(X))
    numfind = NumFinder()
    expr, cert = numfind.find(X)
    print("It looks like: {0} with a certainty of: {1}".format(expr,cert))
    
if __name__ == "__main__":
    main()
