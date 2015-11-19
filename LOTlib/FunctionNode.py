# -*- coding: utf-8 -*-

from LOTlib.Miscellaneous import cached
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

    def __init__(self, parent, rule, string=None, pystring=None):
        super(FunctionNode, self).__init__(parent)
        self._rule = rule
        self._children = [None for _ in self.child_types]
        # string stuff -- string can come from 3 places that form a hierarchy
        # if the rule specifies a string, it gets passed in and used
        # otherwise, if the inheriting class defines it, that is used
        # otherwise, it's the default fname(arg1, arg2) construction built here
        n_args = len(inspect.getargspec(type(self).call).args)
        arg_string = '('+','.join(['{'+str(i)+'}' for i in range(n_args)])+')'
        if string is not None:
            self._fmtstring = string
        if pystring is not None:
            self._pyfmtstring = pystring
        if self._fmtstring is None:
            self._fmtstring = self.name + arg_string
        if self._pyfmtstring is None:
            self._pyfmtstring = self.name + '.call' + arg_string

    @cached
    def __str__(self):
        args = [str(child) for child in self.children]
        return self._fmtstring.format(*args)

    @property
    @cached
    def pystring(self):
        args = [child.pystring for child in self.children]
        return self._pyfmtstring.format(*args)

    def debugstring(self, depth=0):
        string = '|'*depth + 'N: ' + self.rule
        for child in self.children:
            string += '\n' + child.debugstring(depth+1)

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
            raise Immutable()
        self.children[i] = node
        #return node

    @staticmethod
    def call(self, *args):
        """
        The function that this class implements
        """
        raise NotImplementedError

    def evaluate(self, state={}):
        #if self.name == 'concat':
            #print 'evaluating concat'
            #print 'children', self.children
            #print 'state', state
            #print 'evaled', [child.evaluate(state) for child in self.children]
        #if self.name == 'minus':
            #print 'minus eval'
            #print 'state', state
        args = [child.evaluate(state) for child in self.children]
        #if self.name == 'minus':
            #print 'args', args
        return type(self).call(*args)

    @property
    def return_type(self):
        return self.rule.lhs

    @property
    def rule(self):
        return self._rule

    @property
    @cached
    def log_prob(self):
        """
        Returns the log probability of generating every node in the
        tree rooted by this node
        """
        return sum(node.grammar.gen_prob(node.rule) for node in self)


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
            for descendent in child:
                yield descendent

    def nodes_where(self, name=None):
        """
        Iterates all nodes in the tree rooted by this node that satisfy the conditions
        """
        for node in self:
            if node.name == name:
                yield node

    @staticmethod
    def new(chooser):
        """
        Returns a new tree using the given rule choosing function
        """
        grammar = chooser.__self__
        rule = chooser(grammar.start_symbol, None)
        new = rule.make_node(parent_node=None)
        new._grammar = grammar
        new.generate(chooser)
        return new

    def generate(self, chooser):
        """
        recursively instantiates the children of this node
        """
        chooser = getattr(self.grammar, chooser.__name__) # bind to new grammar
        for i, typ in enumerate(self.child_types):
            if typ in self.grammar.nonterminals:
                rule = chooser(lhs=typ, node=self)
                new_node = rule.make_node(parent_node=self)
                self.set_child(i, new_node)
                new_node.generate(chooser)
            else:
                self.set_child(i, TerminalNode(parent=self, string=typ))

    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        return fullstring(self) == fullstring(other)

    def __hash__(self):
        return hash(str(self))

    def __cmp__(self, other):
        return cmp(hash(self), hash(other))

