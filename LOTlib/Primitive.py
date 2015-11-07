# -*- coding: utf-8 -*-

import inspect
from operator import concat
from contextlib import contextmanager

"""
class to track the state of bound vars during the execution of a
function tree
"""
class ExecutionState(object):
    """
    Keeps track of the values assigned to bound vars
    """
    def __init__(self):
        self._value = {}
        self._stored_value = None

    def store(self, value):
        """
        Stores the computed value of the argument to an apply statement
        """
        self._stored_value = value
  
    @contextmanager
    def bind_stored_to(varname):
        """
        binds the stored value (from previous apply) to the given variable
        and unbinds it on exit
        """
        assert self._stored_value is not None
        self._value[varname] = self._stored_value
        self._stored_value = None
        yield
        del self._value[varname]

    def value(self, varname):
        return self._value[varname]


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
        self._name = name
        self._state = ExecutionState()
        self._primitives = []

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    # decorator to turn a function into a primitive object
    def make(self, fn):
        return self.register(Primitive(fn, self))

    # stores the primitive in self
    def register(self, p):
        self._primitives.append(p)
        setattr(self, p.fn.__name__, p)
        return p

    def __iter__(self):
        for p in self._primitives:
            yield p

Primitives = PrimitiveContainer('Primitives')


class Primitive(object):
    def __init__(self, fn, container):
        self.fn = fn
        self.container = container
        self.state = container.state
        n_args = len(inspect.getargspec(fn).args)
        self.string = self.name+'('+','.join(['{'+str(i)+'}' for i in range(n_args)])+')'
        self.pystring = self.container.name + '.' + self.string

    @property
    def name(self):
        return self.fn.__name__

    def __call__(self, *args):
        return self.fn(*args)

    def to_string(self, *args):
        return self.string.format(*args)

    def to_pystring(self, *args):
        return self.pystring.format(*args)
    
    ####
    # decorators to overwrite the default string functions
    ####

    def stringfn(self, fn):
        self.to_string = fn

    def pystringfn(self, fn):
        self.to_pystring = fn



####################
# Basic primitives supplied by the framework
####################

@Primitives.make
def apply_(fn, arg):
    self.state.store((arg))
    return fn

apply_.string = '{0} ({1})'
apply_.pystring = '({0})({1})'

@Primitives.make
def lambda_(varname, body):
    with self.state.bind_stored_to(varname):
        return (body)

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

