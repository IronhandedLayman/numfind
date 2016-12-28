#!/opt/local/bin/python

import argparse
import math

class NumFinder:
    def __init__(self):
        self.constants = {}
        self.max_complexity = 30
        self.reset_constants()

    def reset_constants(self):
        self.constants = {}
        self.add_constant("pi",math.pi)
        self.add_constant("e",math.e)
        for n in range(1,101):
            self.add_constant(str(n),n)

    def add_constant(self, name, value):
        self.constants[name]=value

    def search_heuristic(self, X, Y):
        try:
            return math.log(1/abs(X-Y))
        except:
            return -999 #TODO: does this constant even make sense?

    def find(self, X):
        bfsf = None
        heur = None
        for name,val in self.constants.items():
            constHeur = self.search_heuristic(val,X)
            if heur is None or heur < constHeur:
                heur=constHeur
                bfsf=name
        return (bfsf, heur)

def main():
    parser = argparse.ArgumentParser(description='Find numbers close to a given constant or expression')
    parser.add_argument('inval', metavar='X', type=float, nargs=1, help='the number to approximate with a constant')
    pargs = parser.parse_args()
    X = pargs.inval[0]
    print("You're looking for: {0}".format(X))
    numfind = NumFinder()
    name, cert = numfind.find(X)
    print("It looks like: {0} with a certainty of: {1}".format(name,cert))
    
if __name__ == "__main__":
    main()
