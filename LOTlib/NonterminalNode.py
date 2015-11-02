# -*- coding: utf-8 -*-

from LOTlib.Node import Node
from LOTlib.Miscellaneous import cached
from copy import copy
from LOTlib.TerminalNode import TerminalNode

def Immutable(Exception):
    pass

class NonterminalNode(Node):
    """
    Arguments
    ---------
    parent:
        our parent node, None if this is the root
    rule : 
        The rule expansion that this node represents
    gen_prob : float
        *Normalized* log generation probability.
    """

    def __init__(self, parent, rule, gen_prob, state=None):
        super(NonterminalNode, self).__init__(parent)
        self._rule = rule
        self._gen_prob = gen_prob
        if parent:
            self._rule_state = parent.rule_state
        else:
            self._rule_state = rule_state
        self._children = [None for _ in rule._to]
        if rule.is_lambda:
            new_rule = self.state.update_rules(rule)
            child = self.set_child(0, NonterminalNode(self, new_rule, 1.0))
            child.set_child(0, BVNode(child, state))

    #def __call__(self):
        #return self.

    @property
    def children(self):
        return self._children

    def child(self, i):
        return self.children[i]

    @property
    def varname(self):
        if not self.is_lambda:
            raise Exception('only lambda nodes have a varname')
        return child.child(0).string

    def set_child(self, i, node):
        if node.rule.is_lambda and i == 0 and self.children[i] is not None: # special handling for lambda's first arg, since it gets set by constructor
            # assert invariances -- first child already set
            # and its var is the most recent bv
            child = self.child(0)
            assert child is not None
            varname = self.state.rules[node.rule.bv_type][-1].to[0] # the most recent rule's arg; x1 in BV -> x1
            assert self.varname == varname
        else:
            if self.children[i] is not None:
                raise Immutable()
            self.children[i] = node
            return node

    @property
    def rule(self):
        return self._rule

    @property
    def function(self):
        return self.rule.function

    @property
    def fname(self):
        return self.function.name

    @property
    def rule_state(self):
        return self._rule_state

    @property
    @cached
    def log_prob(self):
        """Compute the log probability of a tree."""
        return self.gen_prob + sum([child.log_prob() for child in self.children])

    @property
    @cached
    def size(self):
        """
        Returns the size of the tree for which this node is the root
        """
        return 1 + sum([child.size for child in self.children])


    def __iter__(self):
        """
        Iterates through the full tree for which this node is the root
        """
        yield self
        for child in self.children:
            for gchild in child:
                yield gchild

    def nodes_where(self, fname=None):
        """
        Iterates all nodes in the tree rooted by this node that satisfy the conditions
        """
        for node in self:
            try:
                if node.fname == fname:
                    yield node
            except AttributeError: # not a function node
                pass

    @cached
    def __str__(self):
        args = [str(child) for child in self.children]
        if self.rule.string:
            return self.rule.string.format(*args)
        else:
            return self.function.to_string(*args)

    @property
    @cached
    def pystring(self):
        args = [child.pystring for child in self.children]
        return self.function.to_pystring(*args)

    def debugstring(self, depth=0):
        string = '|'*depth + 'N: ' + self.rule
        for child in self.children:
            string += '\n' + child.debugstring(depth+1)

    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        return fullstring(self) == fullstring(other)

    def __hash__(self):
        return hash(str(self))

    def __cmp__(self, other):
        return cmp(hash(self), hash(other))




    #class RuleCache(object):
        #def __init__(self):
            #self.cache = defaultdict(list)

        #def _add(self, rule):
            #self.cache[rule.lhs].append(rule)

        #def get_rule(self, rule, i):
            #"""
            #Takes a lambda rule and returns its i'th bv rule
            #"""
            ## populate cache with however many rules are needed to have i of them (should only ever iterate once at a time)
            #for n in range(len(self.cache[rule.bv_type]), i): 
                #varname = rule.bv_prefix + str(n)     # unique name for this var
                #self._add(rule.make_bv_rule(self._bv_p, varname))   # make the rule
            #return self.cache[rule.bv_type][i]

        #def new_state(self):
            #return BVState(self)
