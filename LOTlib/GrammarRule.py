# *- coding: utf-8 -*-

class GrammarRule(object):
    """
    A rule for a Grammar

    Arguments
    ---------
    lhs : str
        the nonterminal
    to : list<str>
        the types of the arguments to the function, or the terminals and types to expand to
    p (optional) : float
        unnormalized probability of expansion, default 1.0
    string (optional): format string
        overrides the default format string for the function
    pystring (optional): format string
        ovverrides the default format pystring for the function
    bv_prefix (optional) : str
        if this a lambda rule, the prefix}for the introduced variable

    Examples
    --------
    # A function of n variables, n >= 0, where n is the length of to
    >> GrammarRule( "EXPR", "plus", ["EXPR", "EXPR"], ...) -> plus(EXPR,EXPR)
    >> GrammarRule( "EXPR", "flip", [], ...) -> flip()
    >> GrammarRule( "EXPR", "lambda", [BV_TYPE, BODY_TYPE], ...) -> lambda <BV_TYPE>:x BODY_TYPE
    # A normal rule
    >> GrammarRule( "EXPR", None, ['term', 'NONTERM', 'term'], ...) -> EXPR-> 'term'+NONTERM+'term'

    """
    def __init__(self, lhs, primitive, to, p=1.0, **kwargs):
        self._lhs = lhs
        self._primitive = primitive
        self._to = to
        self._p = float(p)
        self._kwargs = kwargs # to pass along to node constructor


    @property
    def lhs(self):
        return self._lhs

    #@property
    #def primitive(self):
        #return self._primitive

    #@property
    #def fname(self):
        #return self.function.name

    #@property
    #def is_lambda(self):
        #return self._is_lambda

    @property
    def primitive(self):
        return self._primitive

    #@property
    #def bv_type(self):
        #if self.is_lambda:
            #return self.to[0]

    @property
    def to(self):
        return self._to

    @property
    def p(self):
        return self._p

    #@property
    #def string(self):
        #return self._string

    def make_node(self, parent_node):
        """
        creates a new node of this rule's primitive, passing along
        all arguments
        """
        #print self._primitive
        #print self._kwargs
        return self._primitive(parent=parent_node, rule=self, **self._kwargs)

    #def make_root(self, gen_prob, rules, **kwargs):
        #"""
        #creates a new root node
        #"""
        #node = self.make_node(None, gen_prob)
        #node.init_state(rules)
        #return node

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        """
        returns string in format: 'NT -> [TO]   p=1.0'.
        """
        return str(self.lhs)+' -> '+self.primitive.__name__+str(self.to)+'\t p='+str(self.p)


    #def short_str(self):
        #"""Print string in format: 'NT -> [TO]'."""
        #return str(self._lhs) + " -> " + self._fname + (str(self.to) if self.to is not None else '')


