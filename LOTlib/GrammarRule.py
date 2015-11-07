# *- coding: utf-8 -*-

from copy import copy

class GrammarRule(object):
    """
    A rule for a Grammar

    Arguments
    ---------
    lhs : str
        the nonterminal
    fname : str
        the name of the function, or something falsy if a simple nonterminal of type A->B
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
    def __init__(self, lhs, fname, to, p=1.0, string=None, pystring=None, bv_prefix=None):
        self._lhs = lhs
        if not fname:
            fname = 'nonterminal'
        self._function = getattr(primitives, fname)
        self._is_lambda = (self._fname == 'lambda_')
        self._to = to
        self._p = float(p)
        self._string = string
        self._pystring = pystring
        if self._is_lambda and bv_prefix is None:
            self._bv_prefix = self._to[0][0].lower()
        else:
            self._bv_prefix = bv_prefix

    @property
    def lhs(self):
        return self._lhs

    @property
    def function(self):
        return self._function

    @property
    def fname(self):
        return self.function.name

    @property
    def is_lambda(self):
        return self._is_lambda

    @property
    def bv_type(self):
        if self.is_lambda:
            return self.to[0]

    @property
    def to(self):
        return self._to

    @property
    def p(self):
        return self._p

    @property
    def string(self):
        return self._string

    @property
    def bv_prefix(self):
        if self.is_lambda:
            return self._bv_prefix
        else:
            return None

    def make_bv_rule(self, p, varname):
        """
        If this is a lambda rule, this returns a new rule to generate its bound var
        varname: (str) the name of the introduced variable
        p: the unnormalized probability of choosing this rule
        Ex:
            TOKEN -> x1, p=1.0
        """
        if not self.is_lambda:
            raise Exception('Only lambdas make bv rules')
        return GrammarRule(self.bv_type, None, [varname], p)


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
        return str(self.lhs)+' -> '+self.function.name+str(self.to)+'\t p='+str(self.p)


    #def short_str(self):
        #"""Print string in format: 'NT -> [TO]'."""
        #return str(self._lhs) + " -> " + self._fname + (str(self.to) if self.to is not None else '')


