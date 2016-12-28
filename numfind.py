#!/opt/local/bin/python

import argparse
import math
import heapq

class Expression:
    def complexity(self):
        return 1

    def value(self):
        return 0.0

    def __lt__(self, other):
        return str(self)<str(other)

    def __eq__(self, other):
        return str(self)==str(other)

    def __hash__(self):
        return str(self).__hash__()

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
    return Unary("sqrt", x, lambda x:2*x+1, math.sqrt)

def SinExpr(x):
    return Unary("sin", x, lambda x:2*x+1, math.sin)

def CosExpr(x):
    return Unary("cos", x, lambda x:2*x+1, math.cos)

def TanExpr(x):
    return Unary("tan", x, lambda x:2*x+1, math.tan)

def LogExpr(x):
    return Unary("log", x, lambda x:2*x+1, math.log)

class NumFinder:
    def __init__(self):
        self.set_max_complexity(30).set_epsilon(1e-9).reset_constants().reset_unaries()
        self.set_search_depth(100000)
        self.set_confirm_found(10)

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
        diff = None
        try:
            diff = abs(X-Y.value())
        except ValueError:
            return 100.0
        if diff < self.epsilon:
            return -100.0
        try:
            return -math.log(abs(X)/diff)
        except:
            return 100.0

    def set_max_complexity(self, newcomp):
        self.max_complexity = newcomp
        return self

    def set_search_depth(self, newsd):
        self.search_depth = newsd
        return self
    
    def set_confirm_found(self, newcf):
        self.confirm_found = newcf
        return self

    def set_epsilon(self, neweps):
        self.epsilon = neweps
        return self

    def find(self, X):
        bfsf = None
        heur = None
        allExpr = set()
        exprPQ = []

        for expr in self.constants:
            allExpr.add(expr)
            heur, comp = self.search_heuristic(X, expr), expr.complexity()
            exprPQ.append((heur,comp-heur,expr))
        heapq.heapify(exprPQ)

        tryThisMany = 0
        while len(exprPQ) > 0 and tryThisMany < self.search_depth:
            tryThisMany += 1
            if tryThisMany % 10000 == 0:
                print("Tried so far: {0}".format(tryThisMany))
            newHeur, newComplexity, nextExpr = heapq.heappop(exprPQ)
            if heur is None or heur > newHeur:
                heur,bfsf=newHeur,nextExpr
                print("best found so far: {0} (confidence: {1})".format(bfsf, -heur))
            if -heur > self.confirm_found:
                break
            for unry in self.unaries:
                unryExpr = unry(nextExpr)
                if unryExpr in allExpr or unryExpr.complexity() >= self.max_complexity:
                    continue
                unryHeur, unryComp = self.search_heuristic(X, unryExpr), unryExpr.complexity()
                heapq.heappush(exprPQ,(unryHeur, unryComp-unryHeur, unryExpr))
                
             
        return (bfsf, -heur)

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
