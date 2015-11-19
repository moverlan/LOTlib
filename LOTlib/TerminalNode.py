# -*- coding: utf-8 -*-

from LOTlib.Node import Node

class TerminalNode(Node):
    def __init__(self, parent, string):
        super(TerminalNode, self).__init__(parent)
        self._string = string

    def __str__(self):
        return self._string

    @property
    def pystring(self):
        raise NotImplementedError
        #if not isinstance(self._string, str):
            #return str(self._string)
        #elif self._string in self.grammar.bvs: # bound var
            #return self._string
        #else:
            #return "'"+self._string+"'"
        
    @property
    def returntype(self):
        return self._string

    def evaluate(self, state={}):
        value = self._string
        # resolve all variables
        while value in state:
            value = state[value]
        return value

    @property
    def log_prob(self):
        return 0.

    def __iter__(self):
        yield self

    def debugstring(self, depth=0):
        return '|'*depth + self.string
