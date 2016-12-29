#!/opt/local/bin/python

import argparse
import math
import heapq
import csv

from expressions import *

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
                print("Tried so far: {0:>7}".format(tryThisMany))
            _, newHeur, nextExpr = heapq.heappop(exprPQ)
            if nextExpr.complexity() > allExpr.get(nextExpr.value(),(100,0))[0]:
                continue
            if heur is None or heur > newHeur:
                heur,bfsf=newHeur,nextExpr
                if self.debug:
                    print("Maybe: {0:30} (Confidence: {1:.4f})".format(str(bfsf), -heur))
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
    parser = argparse.ArgumentParser(description='Find expressions close to a given constant X.')
    parser.add_argument('inval', metavar='X', type=float, nargs=1, help='the number to approximate with a constant')
    parser.add_argument('--max_comp', type=int, help='Maximum complexity search depth', default=15)
    parser.add_argument('--eps', type=float, help='Will exit search if term found within this epsilon', default=1e-9)
    parser.add_argument('--search_depth', type=int, help='Will attempt this many terms before exiting', default=100000)
    parser.add_argument('--confirm', type=float, help='If heuristic finds term with this Confidence, will exit.', default=10)
    parser.add_argument('--quiet', dest='debug', action='store_const', default=True, const=False, help='If set, will stay quiet until answer is found.')
    parser.add_argument('--cfile', type=argparse.FileType('r'), default=None)
    pargs = parser.parse_args()

    X = pargs.inval[0]
    if pargs.debug:
        print("Searching relevant terms for: {0}".format(X))
    
    numfind = NumFinder()
    numfind.set_max_complexity(pargs.max_comp).set_epsilon(pargs.eps)
    numfind.set_search_depth(pargs.search_depth).set_confirm_found(pargs.confirm)
    if pargs.cfile is not None:
        with pargs.cfile as csvfile:
            constantFile = csv.reader(csvfile)
            for row in constantFile:
                try:
                    numfind.add_constant(Constant(row[0],float(row[1])))
                except:
                    print("Warning: could not interpret row: {0}".format(",".join(row)))
    numfind.set_debug(pargs.debug)
    expr, cert = numfind.find(X)

    print("       {0:30} (Confidence: {1:.4f})".format(str(expr),cert))
    
if __name__ == "__main__":
    main()
