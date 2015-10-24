# -*- coding: utf-8 -*-

import inspect
import operator

"""
Decorators that set up a primitive object, the basic unit of computation in a function tree.
A primitive has three methods:
    __call__(*args) : the computation this primitive performs
    __str__() : returns a human readable string
    pystring(): returns a python-eval-able string
"""

class PrimitiveContainer(object): # can't setattr on bare object
    pass
# store all registered primitives
Primitives = PrimitiveContainer()


class Primitive(object):
    def __init__(self, fn):
        self.fn = fn
        self.name = fn.__name__
        n_args = len(inspect.getargspec(fn).args)
        self._string = self.name+'('+','.join(['{'+str(i)+'}' for i in range(n_args)])+')'
        self._pystring = 'Primitives.'+self._string

    def __call__(self, *args):
        return self.fn(*args)

    def __str__(self):
        return self.to_string()

    def to_string(self, *args):
        return self._string.format(*args)

    def to_pystring(self, *args):
        return self._pystring.format(*args)


    # for functions with a variable number of arguments
    # decorators to make a instance methods
    def stringfn(self, fn):
        self.to_string = fn

    def pystringfn(self, fn):
        self.to_pystring = fn

def primitive(fn):
    obj = Primitive(fn)
    setattr(Primitives, fn.__name__, obj)
    return obj

####################
# Basic primitives supplied by the framework
####################

@primitive
def apply_(fn, args):
    return fn(*args)

apply_.string = '{0} ({1})'
apply_.pystring = '({0})({1})'

@primitive
def lambda_(varname, body):
    pass

lambda_.string = 'λ{0}.{1}'
lambda_.pystring = 'lambda {0}: {1}'

@primitive
def concat(*args):
    return reduce(operator.concat, args)

@concat.stringfn
def concat_str(self, *args):
    return ''.join(args)

@concat.pystringfn
def concat_pystr(self, *args):
    return '+'.join(args)

@primitive
def nonterminal(arg):
    return arg

nonterminal.string = '{0}'
nonterminal.pystring = '{0}'

