#!/opt/local/bin/python

import argparse
import math
import heapq

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

class NumFinder:
    def __init__(self):
        #defaults
        self.set_max_complexity(15).set_epsilon(1e-9)
        self.set_search_depth(100000).set_confirm_found(10)
        self.set_debug(True)

        #base set of constants
        self.reset_constants().reset_unaries().reset_binaries()

    def reset_constants(self):
        self.constants = set()
        self.add_constant(Constant("pi",math.pi)).add_constant(Constant("e",math.e))
        for n in range(1,11):
            self.add_constant(IntConst(n))
        return self

    def reset_unaries(self):
        self.unaries = set()
        self.add_unary(SqrtExpr).add_unary(SinExpr).add_unary(CosExpr).add_unary(TanExpr).add_unary(LogExpr)
        return self

    def reset_binaries(self):
        self.binaries = set()
        self.add_binary(AddExpr).add_binary(SubtractExpr).add_binary(MultExpr).add_binary(DivExpr).add_binary(PowExpr)
        return self

    def add_constant(self, expr):
        self.constants.add(expr)
        return self

    def add_unary(self, unary):
        self.unaries.add(unary)
        return self

    def add_binary(self, binary):
        self.binaries.add(binary)
        return self

    def search_heuristic(self, X, Y):
        diff = None
        value = None
        comp = Y.complexity()
        try:
            value = Y.value()
            diff = abs(X-Y.value())
        except (ValueError, OverflowError,ZeroDivisionError):
            return (100.0,None,comp)
        if diff < self.epsilon:
            return (-100.0, value, comp)
        try:
            return (-math.log(abs(X)/diff), value, comp)
        except:
            return (100.0, value, comp)

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

    def set_debug(self, debugflag):
        self.debug = debugflag
        return self

    def find(self, X):
        bfsf = None
        heur = None
        allExpr = {}
        exprPQ = []

        for expr in self.constants:
            heur, value, comp = self.search_heuristic(X, expr)
            allExpr[value]=(comp, expr)
            exprPQ.append((comp+heur,heur,expr))
        heapq.heapify(exprPQ)

        tryThisMany = 0
        while len(exprPQ) > 0 and tryThisMany < self.search_depth:
            tryThisMany += 1
            if self.debug and tryThisMany % 1000 == 0:
                print("Tried so far: {0}".format(tryThisMany))
            _, newHeur, nextExpr = heapq.heappop(exprPQ)
            if nextExpr.complexity() > allExpr.get(nextExpr.value(),(100,0))[0]:
                continue
            if heur is None or heur > newHeur:
                heur,bfsf=newHeur,nextExpr
                if self.debug:
                    print("best found so far: {0} (confidence: {1})".format(bfsf, -heur))
            if -heur > self.confirm_found:
                break

            #always try to expand along unaries
            for unry in self.unaries:
                unryExpr = unry(nextExpr)
                if unryExpr.complexity() >= self.max_complexity:
                    continue
                unryHeur, unryValue, unryComp = self.search_heuristic(X, unryExpr)
                if unryValue not in allExpr or allExpr[unryValue][0] > unryComp:
                    heapq.heappush(exprPQ,(unryComp+unryHeur, unryHeur, unryExpr))
                    allExpr[unryValue]=(unryComp, unryExpr)
                    
            #oh yeah this is wasteful but let's see if I can optimize it
            for bnry in self.binaries:
                othBinExpr={}
                for (_,lhs) in allExpr.values():
                    for (_,rhs) in allExpr.values():
                        bnryExpr = bnry(lhs, rhs)
                        if bnryExpr.complexity() >= self.max_complexity:
                            continue
                        bnryHeur, bnryValue, bnryComp = self.search_heuristic(X, bnryExpr)
                        if bnryValue not in allExpr or allExpr[bnryValue][0] > bnryComp:
                            heapq.heappush(exprPQ,(bnryComp+bnryHeur, bnryHeur, bnryExpr))
                            othBinExpr[bnryValue]=(bnryComp, bnryExpr)
            allExpr.update(othBinExpr)    
        return (bfsf, -heur)

def main():
    parser = argparse.ArgumentParser(description='Find numbers close to a given constant or expression')
    parser.add_argument('inval', metavar='X', type=float, nargs=1, help='the number to approximate with a constant')
    parser.add_argument('--max_comp', type=int, help='Maximum complexity search depth', default=15)
    parser.add_argument('--eps', type=float, help='Will exit search if term found within this epsilon', default=1e-9)
    parser.add_argument('--search_depth', type=int, help='Will attempt this many terms before exiting', default=100000)
    parser.add_argument('--confirm', type=float, help='If heuristic finds term with this confidence, will exit.', default=10)
    parser.add_argument('--nodebug', dest='debug', action='store_const', default=True, const=False, help='If set, will stay quiet until answer is found.')
    pargs = parser.parse_args()
    X = pargs.inval[0]
    if pargs.debug:
        print("Searching relevant terms for: {0}".format(X))
    
    numfind = NumFinder()
    numfind.set_max_complexity(pargs.max_comp).set_epsilon(pargs.eps)
    numfind.set_search_depth(pargs.search_depth).set_confirm_found(pargs.confirm)
    numfind.set_debug(pargs.debug)
    expr, cert = numfind.find(X)

    print(":: {0} (Confidence: {1:.2f})".format(expr,cert))
    
if __name__ == "__main__":
    main()
