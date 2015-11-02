# -*- coding: utf-8 -*-

import inspect
from operator import concat

"""
Class and decorators that set up a primitive object, the basic unit of computation in a function tree.
A primitive has three methods:
    __call__(*args) : the computation this primitive performs
    to_string() : returns a human readable string
    to_pystring(): returns a python-eval-able string
"""

# container to store all registered primitives
# takes one parameter, name, the name of the identifier for the object
# (so pystring knows how to call itself)
class PrimitiveContainer(object):
    def __init__(self, name):
        self.name = name
        self._primitives = []

    # decorator to turn a function into a primitive object and
    # store it in self
    def make(self, fn):
        return self.register(Primitive(fn, self.name))

    def register(self, p):
        self._primitives.append(p)
        setattr(self, p.fn.__name__, p)
        return p

    def __iter__(self):
        for p in self._primitives:
            yield p

Primitives = PrimitiveContainer('Primitives')


class Primitive(object):
    def __init__(self, fn, container_name):
        self.fn = fn
        self.container_name = container_name
        n_args = len(inspect.getargspec(fn).args)
        self.string = self.name+'('+','.join(['{'+str(i)+'}' for i in range(n_args)])+')'
        self.pystring = self.container_name + '.' + self.string

    @property
    def name(self):
        return self.fn.__name__

    def __call__(self, *args):
        return self.fn(*args)

    #def __str__(self):
        #return self.to_string()

    def to_string(self, *args):
        return self.string.format(*args)

    def to_pystring(self, *args):
        return self.pystring.format(*args)
    
    # decorators to overwrite the default functions
    def stringfn(self, fn):
        self.to_string = fn

    def pystringfn(self, fn):
        self.to_pystring = fn


####################
# Basic primitives supplied by the framework
####################

@Primitives.make
def apply_(fn, arg):
    from ipdb import set_trace as bp
    bp()
    return fn(arg)

apply_.string = '{0} ({1})'
apply_.pystring = '({0})({1})'

@Primitives.make
def lambda_(varname, body):
    return body

lambda_.string = 'λ{0}.{1}'
lambda_.pystring = 'lambda {0}: {1}'

@Primitives.make
def concat(*args):
    return reduce(concat, args)

@concat.stringfn
def concat_stringfn(*args):
    return ''.join(args)

@concat.pystringfn
def concat_pystringfn(*args):
    return '+'.join(args)

@Primitives.make
def nonterminal(arg):
    return arg

nonterminal.string = '{0}'
nonterminal.pystring = '{0}'

