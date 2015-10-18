from FunctionNode import FunctionNode, BVAddFunctionNode, BVUseFunctionNode
from copy import copy
from LOTlib.Miscellaneous import None2Empty


class GrammarRule(object):
    """Represent a rule in the grammar.

    Arguments
    ---------
    lhs : str
        the nonterminal
    fname : str
        the name of the function, or something falsy if a regular expansion
    to : list<str>
        the types of the arguments to the function, or the terminals and types to expand to
    p (optional) : float
        unnormalized probability of expansion, default 1.0
    bv_type (optional) : str
        if this rule introduces a new bound variable when expanded (ie. a lambda), the lhs for that bv's rule

    Examples
    --------
    # A function of n variables, n >= 0, where n is the length of to
    >> GrammarRule( "EXPR", "plus", ["EXPR", "EXPR"], ...) -> plus(EXPR,EXPR)
    >> GrammarRule( "EXPR", "flip", [], ...) -> flip()
    # A normal rule
    >> GrammarRule( "EXPR", '', ['term', 'NONTERM', 'term'], ...) -> EXPR-> 'term'+NONTERM+'term'

    """
    def __init__(self, lhs, name, to, p=1.0, bv_type=None):
        p = float(p)

        self._lhs = lhs
        self._name = name
        self._to = to
        self._p = p
        self._bv_type = bv_type

        #for a in None2Empty(to):
            #assert isinstance(a,str)
        #if name == '':
            #assert (to is None) or (len(to) == 1), \
                #"*** GrammarRules with empty names must have only 1 argument"

    def __repr__(self):
        """Print string in format: 'NT -> [TO]   w/ p=1.0'."""
        return str(self._lhs) + " -> " + self._name + (str(self._to) if self._to is not None else '') + \
            "\tw/ p=" + str(self._p)

    def __eq__(self, other):
        """Equality is determined through "is" so that we can remove a rule from lists via list.remove()."""
        return self is other

    def short_str(self):
        """Print string in format: 'NT -> [TO]'."""
        return str(self._lhs) + " -> " + self._name + (str(self.to) if self.to is not None else '')

    def __ne__(self, other):
        return not self.__eq__(other)

    def bv_prefix(self):
        if self._bv_type is not None:
            return self._bv_type[0].to_lower()

    def make_FunctionNodeStub(self, grammar, gp, parent):
        # NOTE: It is VERY important to copy to, or else we end up wtih garbage
        return FunctionNode(parent, returntype=self._lhs, name=self._name, args=copy(self._to),
                            generation_probability=gp, rule=self)


#class BVAddGrammarRule(GrammarRule):
    #"""
    #A kind of GrammarRule that supports introduces a bound variable, as in at a lambda.

    #Arguments
    #---------
    #nt : str
        #the nonterminal
    #name : str
        #the name of this function
    #to : list<str>
        #what you expand to (usually a FunctionNode).
    #rid : ?
        #the rule id number
    #p : float
        #unnormalized probability of expansion
    #bv_type : str
        #return type of the introduced bound variable
    #bv_args : ?
        #what are the args when we use a bv (None is terminals, else a type signature)

    #Note
    #----
    #If we use this, we should have BV (i.e. argument `bv_type` should be specified).

    #"""
    #def __init__(self, lhs, name, to, p=1.0, bv_prefix="y", bv_type=None, bv_args=None, bv_p=None):
        #super(BVAddGrammarRule, self).__init__(lhs, name, to, p, bv_prefix)
        #self._bv_type = bv_type
        #self._bv_args = bv_args
        #self._bv_p = bv_p
        #self.add_rule = True
        #assert name is 'lambda' # For now, let's assume these must be lambdas.
        #assert bv_type is not None, "Did you mean to use a GrammarRule instead of a BVGrammarRule?"
        #assert isinstance(bv_type, str), "bv_type must be a string! Make sure it's not a tuple or list."
        
    #def __repr__(self):
        #return str(self._lhs) + " -> " + self._name + (str(self.to) if self.to is not None else '') + \
            #"\tw/ p=" + str(self.p) + "," + \
            #"\tBV:" + str(self._bv_type) + ";" + str(self._bv_args) + ";" + self._bv_prefix
    
    #def make_bv_rule(self, grammar):
        #"""Construct the rule that we introduce at a given depth.

        #Note:
            #* This is a GrammarRule and NOT a BVGrammarRule because the introduced rules should *not*
                #themselves introduce rules!
            #* This is a little awkward because it must look back in grammar, but I don't see how to avoid that

        #"""
        #bvp = self._bv_p
        #if bvp is None:
            #bvp = grammar.BV_P
        #return BVUseGrammarRule(self._bv_type, self._bv_args,
                                #p=bvp, bv_prefix=self._bv_prefix)
   
    #def make_FunctionNodeStub(self, grammar, gp, parent):
        #"""Return a FunctionNode with none of the arguments realized. That's a "stub"

        #Arguments
        #---------
        #d : int
            #the current depth
        #gp : float
            #the generation probability
        #parent : ?

        #Note
        #----
        #* The None's in the next line need to get set elsewhere, since they will depend on the depth and
        #other rules
        #* It is VERY important to copy to, or else we end up wtih garbage

        #"""
        #return BVAddFunctionNode(parent, returntype=self._lhs, name=self._name, args=copy(self._to),
                                 #generation_probability=gp, added_rule=self.make_bv_rule(grammar), rule=self)


#class BVUseGrammarRule(GrammarRule):
    #"""
    #A Grammar rule that is the use of a bound variable. (e.g. in (lambda (y) ...), this rule is active in the ...
    #and allows you to make y).

    #Each of these has a unique name via uuid.

    #"""
    #def __init__(self, lhs, to, p=1.0, bv_prefix=None):
        #self.add_rule = False
        #GrammarRule.__init__(self, lhs, 'bv__'+uuid4().hex, to, p, bv_prefix)

    #def make_FunctionNodeStub(self, grammar, gp, parent):
        ## NOTE: It is VERY important to copy to, or else we end up wtih garbage
        #return BVUseFunctionNode(parent, returntype=self._lhs, name=self._name, args=copy(self._to),
                                 #generation_probability=gp, rule=self)
