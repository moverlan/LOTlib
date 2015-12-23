# -*- coding: utf-8 -*-

from LOTlib.FunctionNode import FunctionNode
import operator
from copy import copy
from LOTlib.GrammarRule import GrammarRule

####################
# Basic primitives supplied by the framework
####################

class apply_(FunctionNode):
    _fmtstring='{0} ({1})'
    _pyfmtstring = '({0})({1})'

    def evaluate(self, state={}):
        fn, arg = list(self.children)
        assert fn.name == 'lambda_'
        state[fn.varname] = arg.evaluate(state)
        return fn.evaluate(state)

    @property
    def arg_type(self):
        return self.rule.to[1]

    
class lambda_(FunctionNode):
    _fmtstring = 'λ{0}.{1}'
    _pyfmtstring = 'lambda {0}: {1}'

    def __init__(self, rule, bv_type, bv_prefix=None, **kwargs):
        super(lambda_, self).__init__(rule, **kwargs)
        self._bv_type = bv_type
        self._bv_prefix = bv_prefix
        if bv_prefix is None:
            self._bv_prefix = bv_type[0].lower()
        self._new_grammar = None
        self._varname = None
        self._bv_rule = None

    @property
    def grammar(self):
        if self._new_grammar is None:
            self._new_grammar = super(lambda_, self).grammar.copy_with(self.bv_rule)
        return self._new_grammar

    def __str__(self):
        return self._fmtstring.format(self.varname, str(self.child(0)) if self.child(0) is not None else self.rule.to[0])

    @property
    def pystring(self):
        return self._pyfmtstring.format(self.varname, self.child(0).pystring)

    def evaluate(self, state={}):
        return self.child(0).evaluate(state)

    @property
    def varname(self):
        if self._varname is None:
            parent_grammar = super(lambda_, self).grammar
            self._varname = self.bv_prefix + str(len(parent_grammar.bv_rules[self.bv_type])+1)
        return self._varname

    @property
    def bv_prefix(self):
        return self._bv_prefix

    @property
    def bv_type(self):
        return self._bv_type

    @property
    def bv_rule(self):
        """
        Ex:
            TOKEN -> x1, p=1.0
        """
        if self._bv_rule is None:
            parent_grammar = super(lambda_, self).grammar
            self._bv_rule = GrammarRule(self.bv_type, Nonterminal, [self.varname], parent_grammar.bv_p)
        return self._bv_rule


class Nonterminal(FunctionNode):
    _fmtstring = '{0}'
    _pyfmtstring = '{0}'

    def evaluate(self, state={}):
        return self.child(0).evaluate(state)

class concat(FunctionNode):

    @staticmethod
    def call(*args):
        #print 'concat call'
        #print 'args', args
        #print 'out', reduce(operator.concat, args)
        return reduce(operator.concat, args)

    def __str__(self):
        return ''.join([str(child) for child in self.children])

    @property
    def pystring(self):
        return '+'.join([child.pystring for child in self.children])




#import inspect

#"""
#Class and decorators that set up a primitive object, the basic unit of computation in a function tree.
#A primitive has three methods:
    #__call__(*args) : the computation this primitive performs
    #to_string() : returns a human readable string
    #to_pystring(): returns a python-eval-able string
#"""

# container to store all registered primitives
# takes one parameter, name, the name of the identifier for the object
# (so pystring knows how to call itself)
#class PrimitiveContainer(object):
    #def __init__(self, name):
        #self._name = name
        #self._state = ExecutionState()
        #self._primitives = []

    #@property
    #def name(self):
        #return self._name

    #@property
    #def state(self):
        #return self._state

    ## decorator to turn a function into a primitive object
    #def make(self, fn):
        #return self.register(Primitive(fn, self))

    ## stores the primitive in self
    #def register(self, p):
        #self._primitives.append(p)
        #setattr(self, p.fn.__name__, p)
        #return p

    #def __iter__(self):
        #for p in self._primitives:
            #yield p

#Primitives = PrimitiveContainer('Primitives')


#class Primitive(object):
    #def __init__(self, fn, container):
        #self.fn = fn
        #self.container = container
        #self.state = container.state
        #n_args = len(inspect.getargspec(fn).args)
        #self.string = self.name+'('+','.join(['{'+str(i)+'}' for i in range(n_args)])+')'
        #self.pystring = self.container.name + '.' + self.string

    #@property
    #def name(self):
        #return self.fn.__name__

    #def __call__(self, *args):
        #return self.fn(*args)

    
    ####
    # decorators to overwrite the default string functions
    ####

    #def stringfn(self, fn):
        #self.to_string = fn

    #def pystringfn(self, fn):
        #self.to_pystring = fn



