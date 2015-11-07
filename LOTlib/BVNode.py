# -*- coding: utf-8 -*-

from LOTlib.TerminalNode import TerminalNode

class BVNode(TerminalNode):

    @property
    def varname(self):
        return self.string

    #state.get_value(self.varname)

    #def __call__(self):
        #raise NotImplementedError()

