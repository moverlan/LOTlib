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
        self.string = self.name+'('+','.join(['{'+str(i)+'}' for i in range(n_args)])+')'
        self.pystring = 'Primitives.'+self.string

    def __call__(self, *args):
        return self.fn(*args)

    def __str__(self):
        return self.string

    # for functions with a variable number of arguments
    # decorators to make a instance methods
    def to_string(self, fn):
        self.to_string = fn

    def to_pystring(self, fn):
        self.to_pystring = fn

def primitive(fn):
    obj = Primitive(fn)
    setattr(Primitives, fn.__name__, obj)
    return obj

# These are the basic ones supplied by the framework
@primitive
def apply_(fn, args):
    return fn(*args)

apply_.string = '{0} ({1})'
apply_.pystring = '({0})({1})'

@primitive
def lambda_(var, body):
    pass

lambda_.string = 'λ{0}.{1}'
lambda_.pystring = 'lambda {0}: {1}'

@primitive
def concat(*args):
    return reduce(operator.concat, args)

@concat.to_string
def concat(self, *args):
    return ''.join(args)

@concat.to_pystring
def concat(self, *args):
    return '+'.join(args)
