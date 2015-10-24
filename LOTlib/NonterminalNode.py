# -*- coding: utf-8 -*-

from LOTlib.Node import Node
from LOTlib.Miscellaneous import cached
from copy import copy
from LOTlib.TerminalNode import TerminalNode

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

    def __init__(self, parent, rule, gen_prob, rule_state=None):
        super(NonterminalNode, self).__init__(parent)
        self._rule = rule
        self._gen_prob = gen_prob
        if parent:
            self._rule_state = parent.rule_state
        else:
            self._rule_state = rule_state
        self._children = [None for _ in rule._to]
        if rule.is_lambda:
            self.update_state(rule)

    def __call__(self):
        return 

    @property
    def children(self):
        return self._children

    def child(self, i):
        return self.children[i]

    def set_child(self, i, node):
        if ((self.rule.is_lambda and not i == 0) or (not self.rule.is_lambda)) and self.children[i] is not None:
            raise Immutable()
        self.children[i] = node

    @property
    def rule(self):
        return self._rule

    @property
    def function(self):
        function = self.rule.function
        if not function:
            return 'nonterminal'
        else:
            return function

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
                if node.function.name == fname:
                    yield node
            except AttributeError: # not a function node
                pass

    @cached
    def __str__(self):
        args = [str(child) for child in self.children]
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

    def update_state(self, rule):
        assert rule.is_lambda
        # copy-on-write
        # shallow copy dict
        self._rule_state = copy(self.rule_state)
        # self._rule_state now points to new dict, but each key points to original list, 
        # shallow copy the bv rule list -- 
        state = self.rule_state[rule.bv_type] = copy(self.rule_state[rule.bv_type])
        # the bv rule's key now points to new list, but list elements point to original rules
        varname = rule.bv_prefix + str(len(state)+1)       # unique name for this var
        new_rule = rule.make_bv_rule(1.0, varname)   # make the rule
        state.append(new_rule)
        self.set_child(0, varname) # replace it with a terminal






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
