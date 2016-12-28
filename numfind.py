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

    def __repr__(self):
        return "Expr({0})".format(self)

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
    return Unary("sqrt", x, lambda x:x+1, math.sqrt)

def SinExpr(x):
    return Unary("sin", x, lambda x:x+1, math.sin)

def CosExpr(x):
    return Unary("cos", x, lambda x:x+1, math.cos)

def TanExpr(x):
    return Unary("tan", x, lambda x:x+1, math.tan)

def LogExpr(x):
    return Unary("log", x, lambda x:x+1, math.log)

class NumFinder:
    def __init__(self):
        self.set_max_complexity(30).set_epsilon(1e-9).reset_constants().reset_unaries()

    def reset_constants(self):
        self.constants = set()
        self.add_constant(Constant("pi",math.pi)).add_constant(Constant("e",math.e))
        for n in range(1,101):
            self.add_constant(IntConst(n))
        return self

    def reset_unaries(self):
        self.unaries = set()
        self.add_unary(SqrtExpr).add_unary(SinExpr).add_unary(CosExpr).add_unary(TanExpr).add_unary(LogExpr)
        return self

    def add_constant(self, expr):
        self.constants.add(expr)
        return self

    def add_unary(self, unary):
        self.unaries.add(unary)
        return self

    def search_heuristic(self, X, Y):
        diff = abs(X-Y.value())
        if diff < self.epsilon:
            return 100/math.sqrt(Y.complexity())
        try:
            return math.log(1/diff)/math.sqrt(Y.complexity())
        except:
            return -100

    def set_max_complexity(self, newcomp):
        self.max_complexity = newcomp
        return self

    def set_epsilon(self, neweps):
        self.epsilon = neweps
        return self

    def find(self, X):
        bfsf = None
        heur = None
        for expr in self.constants:
            constHeur = self.search_heuristic(X, expr)
            if heur is None or heur < constHeur:
                heur=constHeur
                bfsf=expr
            for unry in self.unaries:
                unryExpr = unry(expr)
                unryHeur = self.search_heuristic(X, unryExpr)
                if heur is None or heur < unryHeur:
                    heur=unryHeur
                    bfsf=unryExpr

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
