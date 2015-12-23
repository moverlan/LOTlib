# -*- coding: utf-8 -*-

from LOTlib.Node import Node

class TerminalNode(Node):
    def __init__(self, value, **kwargs):
        super(TerminalNode, self).__init__(**kwargs)
        self._value = value

    def __str__(self):
        return str(self._value)

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
    def return_type(self):
        return str(self)

    @property
    def name(self):
        return str(self)

    def evaluate(self, state={}):
        value = self._value
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
        return '| '*depth + str(self)

    @property
    def children(self):
        return []

    @property
    def rule(self):
        return None

    def duplicate(self):
        return TerminalNode(value=str(self))
