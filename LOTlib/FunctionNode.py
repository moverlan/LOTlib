# -*- coding: utf-8 -*-

#from LOTlib.Miscellaneous import Cache
from LOTlib.Node import Node
from LOTlib.TerminalNode import TerminalNode
import inspect

def Immutable(Exception):
    pass

class FunctionNode(Node):

    """
    Arguments
    ---------
    parent:
        our parent node, None if this is the root
    rule : 
        The rule expansion that this node represents
    """

    # for a subclass named Cons with a call method call(self, a, b), fmtstring looks like:
    # "Cons({0},{1})"
    # and pyfmtstring looks like
    # "Cons.call({0},{1})"

    _fmtstring = None
    _pyfmtstring = None

    def __init__(self, rule, param=None, string=None, pystring=None, **kwargs):
        super(FunctionNode, self).__init__(**kwargs)
        self._rule = rule
        self._children = [None for _ in self.child_types]
        self._param = param
        # string stuff -- string can come from 3 places that form a hierarchy
        # if the rule specifies a string, it gets passed in and used
        # otherwise, if the inheriting class defines it, that is used
        # otherwise, it's the default fname(arg1, arg2) construction built here
        if string is not None:
            self._fmtstring = string
        if pystring is not None:
            self._pyfmtstring = pystring

        n_args = len(inspect.getargspec(type(self).call).args)
        arg_string = '('+','.join(['{'+str(i)+'}' for i in range(n_args)])+')'

        if self._fmtstring is None:
            self._fmtstring = self.name + arg_string
        if self._pyfmtstring is None:
            self._pyfmtstring = self.name + '.call' + arg_string

        #self._cache_down = {}

    def __str__(self):
        args = [str(child) if child is not None else self.rule.lhs for child in self.children]
        return self._fmtstring.format(*args)

    @property
    def pystring(self):
        args = [child.pystring for child in self.children]
        return self._pyfmtstring.format(*args)

    def debugstring(self, depth=0):
        string = '| '*depth + str(self.rule)
        for i, child in enumerate(self.children):
            if child is None:
                string += '\n' + self.rule.to[i]
            else:
                string += '\n' + child.debugstring(depth+1)
        return string

    #@classmethod
    #def name(cls):
        #return cls.__name__

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def child_types(self):
        return self.rule.to

    @property
    def children(self):
        return self._children

    def child(self, i):
        return self.children[i]

    def set_child(self, i, node):
        if self.children[i] is not None:
            # invalidate all caches
            pass
        self.children[i] = node
        node._set_parent(self, child_n=i)

    @staticmethod
    def call(self, *args):
        """
        The function that this class implements
        """
        raise NotImplementedError

    def evaluate(self, state={}):
        args = [child.evaluate(state) for child in self.children]
        return type(self).call(*args)

    @property
    def return_type(self):
        return self.rule.lhs

    @property
    def rule(self):
        return self._rule

    @property
    def log_prob(self):
        """
        """
        return self.grammar.gen_prob(self.rule) + sum(child.log_prob for child in self.children)

    def __iter__(self):
        """
        Iterates through the full tree for which this node is the root
        """
        yield self
        for descendent in self.descendents():
            yield descendent

    def descendents(self):
        """
        yields all nodes below this one
        """
        for child in self.children:
            if child is not None:
                for descendent in child:
                    yield descendent

    def nodes_where(self, name=None):
        """
        Iterates all nodes in the tree rooted by this node that satisfy the conditions
        """
        for node in self:
            if node.is_nonterminal and node.name == name:
                yield node

    def generate_child(self, i, chooser):
        """
        recursively instantiates child i
        """
        # bind chooser function to this node's grammar
        #chooser = getattr(self.grammar, chooser.__name__)
        #assert chooser.__self__ is self.grammar
        typ = self.child_types[i]
        #self._children[i] = None
        if typ in self.grammar.nonterminals:
            rule = chooser(self.grammar, lhs=typ, node=self)
            new_node = rule.make_node()
        else:
            new_node = TerminalNode(value=typ)

        self.set_child(i, new_node)
        new_node.generate_children(chooser)
        return new_node

    def duplicate(self):
        if self.is_root:
            new = self.rule.make_node(grammar=self.grammar)
        else:
            new = self.rule.make_node()
        return new

    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        return self.debugstring() == other.debugstring()

    def __hash__(self):
        return hash(str(self))

    def __cmp__(self, other):
        return cmp(hash(self), hash(other))

