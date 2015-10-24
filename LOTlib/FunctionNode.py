# -*- coding: utf-8 -*-
"""
A function node (fn): a tree part representing a function and its arguments.

Also used for PCFG rules, where the arguments are nonterminal symbols.

"""
import re
from copy import copy, deepcopy
from math import log
from random import random
from collections import defaultdict
from LOTlib.Miscellaneous import lambdaTrue, lambdaOne, Infinity
from LOTlib.Primitive import Primitives
from LOTlib.TerminalNode import TerminalNode
from Util import cached

class Immutable(Exception):
    pass

class FunctionNode(NonterminalNode):
    """
    A Nonterminal that acts as a function of its children
    """

    def __init__(self, parent, rule, gen_prob):
        super(NonterminalNode, self).__init__(parent, rule, gen_prob)



    ##this should be invariant, so put it in a test
    #def argTypes(self):
        ## A list of the strings or returntypes of by args
        ## This should be equal to what my rule produced
        #if self.args is None:
            #return None
        #else:
           #return [a._returntype if isinstance(a, FunctionNode) else a for a in self.args]

    #def sample_subnode(self, resampleProbability=lambdaOne):
        #"""Sample a subnode at random.

        #We return a sampled tree and the log probability of sampling it

        #"""
        #Z = self.sample_node_normalizer(resampleProbability=resampleProbability) # the total probability
        #if not (Z > 0.0):
            #raise NodeSamplingException

        #r = random() * Z # now select a random number (giving a random node)

        #for t in self:
            #trp = resampleProbability(t)
            #r -= 1.0 * trp
            #if r <= 0:
                #return [t, log(trp) - log(Z)]

        #assert False, "Should not get here"

    #@property
    #def debuginfo(self):
        #return ' | '.join([str(id(self)), self.rule.lhs, str(len(self.children))+' children', str(self.function)])
    











    #def iterdepth(self):
        #"""Iterates subnodes, yielding node and depth."""
        #yield (self, 0)

        #if self.args is not None:
            #for a in self.children:
                #for ssn, dd in a.iterdepth():
                    #yield (ssn, dd+1)

    #def leaves(self):
        #"""Returns a generator for all leaves of the subtree rooted at the instantiated FunctionNode."""
        #if self.args is not None:
            #for i in range(len(self.args)):  # loop through kids
                #if isFunctionNode(self.args[i]):
                    #for ssn in self.args[i].all_leaves():
                        #yield ssn
                #else:
                    #yield self.args[i]

                
    #def up_to(self, to=None):
        #"""Yield all nodes going up to "to". If "to" is None, we go until the root (default)."""
        #ptr = self
        #while (ptr is not to) and (ptr is not None):
            #yield ptr
            #ptr = ptr.parent

    #def __len__(self):
        #return len([a for a in self])

    #def depth(self):
        #"""Returns the depth of the tree (how many embeddings below)."""
        #depths = [a.depth() for a in self.children]
        #depths.append(-1)  # for no function nodes (+1=0)
        #return max(depths)+1

    #def sample_node_normalizer(self, resampleProbability=lambdaOne):
        #"""
        #Compute Z to be the sum of all subnodes' value from resampleProbability.
        #* resampleProbability -- a function that gives the resample probability (NOT log prob.) of each node.
        #NOTE: We allow resampleProbability to return a boolean, for 0/1 probability.
        #"""
        #return sum([ 1.0*resampleProbability(x) for x in self])

    # get a description of the input and output types
    # if collapse_terminal then we just map non-FunctionNodes to "TERMINAL"
    #def type(self):
        #"""The type of a FunctionNode is defined to be its returntype if it's not a lambda, or is defined
        #to be the correct (recursive) lambda structure if it is a lambda.

        #For instance (lambda x. lambda y . (and (empty? x) y))
        #is a (SET (BOOL BOOL)), where in types, (A B) is something that takes an A and returns a B

        #Note
        #----
        #If we don't have a function call (as in START) (i.e. self._name == ''), just use the type of
        #what's below

        #"""
        #if self._name == '':
            #assert len(self._args) == 1, "**** Nameless calls must have exactly 1 arg"
            #return self._args[0].type()
        #if not (isinstance(self, BVAddFunctionNode) and self.added_rule is not None):
            #return self._returntype
        #else:
            ## figure out what kind of lambda
            #t = []
            #if self.added_rule is not None and self.added_rule.to is not None:
                #t = tuple( [self.added_rule.nt,] + copy(self.self.added_rule.to) )
            #else:
                #t = self.added_rule.nt

            #return (self.args[0].type(), t)


    #def check_generation_probabilities(self, grammar):
        #"""Check this node's generation probabilities.

        #Note
        #----
        #The can only be called on root -- no bvs allowed unless they are introduced, or else
        #grammar.recompute_generation_probabilities will not work right.

        #"""
        ## and check the generation probabilities -- that these are set correctly
        #gps  = [t.generation_probability for t in self]
        #self.recompute_generation_probabilities(grammar) # re-check these
        #gps2 = [t.generation_probability for t in self]
        #for a,b,n in zip(gps, gps2, self.subnodes()):
            #if abs(a-b) > 0.0001:
                #print "# Wrong generation probabilities %s %s for %s" % (a, b, n)
                #return False
            
        #return True

    #def as_list(self, d=0, bv_names=None):
        #"""Returns a list representation of the FunctionNode with function/self._name as the first element.

        #This function is subclassed so by BVAdd and BVUse so that those handle other cases

        #Arguments
        #---------
        #d : int
            #An optional argument that keeps track of how far down the tree we are
        #bv_names : dict
            #A dictionary keeping track of the names of bound variables (keys = UUIDs, values = names)

        #"""
        ## the tree should be represented as the empty set if the function node has no name
        #if self._name == '':
            #x = []
        #else:
            #x = [self._name]
            
        ## and we're now ready to loop over the function node's arguments
        #if self.args is not None:
            #x.extend([a.as_list(d=d+1, bv_names=bv_names) if isFunctionNode(a) else a for a in self.args])
        
        #return x

    ## --------------------------------------------------------------------------------------------------------

    #def quickstring(self):
        #"""A (maybe??) faster string function used for hashing.

        #Doesn't handle any details and is meant to just be quick.

        #"""
        #if self.args is None:
            #return str(self._name)  # simple call

        #else:
            ## Don't use + to concatenate strings.
            #return '{} {}'.format(str(self._name), ','.join(map(str, self.args)))

    #def fullprint(self, d=0, show_rule=False):
        #"""A handy printer for debugging"""
        #tabstr = "  .  " * d
        #print tabstr, self._returntype, self._name, \
            #"\t", self._generation_probability, "\t", self.added_rule,

        #if show_rule:
           #print "\t\t", self.rule
        #else:
            #print


        #if self._args is not None:
            #for a in self._args:
                #if isFunctionNode(a):
                    #a.fullprint(d+1, show_rule=show_rule)
                #else:
                    #print tabstr, a


    #def liststring(self, cons="cons_"):
        #"""This "evals" cons_ so that we can conveniently build lists (of lists) without having to eval.

        #Mainly useful for combinatory logic, or "pure" trees

        #"""
        #if self.args is None:
            #return self._name
        #elif self._name == cons:
            #return map(lambda x: x.liststring(), self.args)
        #else:
            #assert False, "FunctionNode must only use cons to call liststring!"


    #def __repr__(self):
        #return pystring(self)


    #def recompute_generation_probabilities(self, grammar):
        #"""
        #Re-compute all the generation_probabilities.

        #"""
        #assert self.rule is not None
        #for t in self.iterate_subnodes(grammar, self, do_bv=True):
            #Z = log(sum([x.p for x in grammar.rules[t.returntype]]))
            #t.rule.p = grammar.find(t.returntype, t.rule._name, t.rule.to).p
            #t.generation_probability = log(t.rule.p) - Z
            ##print t.returntype
            ##print t.rule
            ##print t.rule.__dict__ 
            ##print grammar.rules[t.returntype]
            ##print [x.p for x in grammar.rules[t.returntype]]
            ##print sum([x.p for x in grammar.rules[t.returntype]])
            ##print Z
            ##print t.generation_probability

    #def compute_generation_probability(self, grammar):
        #"""
        #Compute the generation probability for this node's root (not considering children).

        #"""
        #assert self.rule is not None, "FunctionNode cannot calculate prob. when rule is None!"
        #Z = log(sum([x.p for x in grammar.rules[self.returntype]]))
        #return log(self.rule.p) - Z

    #def subnodes(self):
        #"""Return all subnodes -- no iterator. Useful for modifying (doc?)

        #Note
        #----
        #If you want iterate using the grammar, use iterate_subnodes

        #"""
        #return [g for g in self]


    #def string_below(self, sep=" "):
        #"""The string of terminals (leaves) below the current FunctionNode in the parse tree.

        #Arguments
        #---------
        #sep : str
            #is the delimiter between terminals. E.g. sep="," => "the,fuzzy,cat"

        #"""
        #return sep.join(map(str, self.all_leaves()))

    # --------------------------------------------------------------------------------------------------------
    #  Derived functions that build on the above core

    #def is_canonical_order(self, symmetric_ops):
        #"""Take a set of symmetric (commutative) ops (plus, minus, times, etc, not divide) and asserts that
            #the LHS ordering is less than the right (to prevent)

        #This is useful for removing duplicates of nodes. For instance,

                #AND(X, OR(Y,Z))

        #is logically the same as

                #AND(OR(Y,Z), X)

        #This function essentially checks if the tree is in sorted (alphbetical) order, but only for
        #functions whose name is in symmetric_ops.

        #"""
        #if self.args is None or len(self.args) == 0:
            #return True

        #if self._name in symmetric_ops:
            ## Then we must check children
            #if self.args is not None:
                #for i in xrange(len(self.args)-1):
                    #if self.args[i]._name > self.args[i+1]._name:
                        #return False

        ## Now check the children, whether or not we are symmetrical
        #return all([x.is_canonical_order(symmetric_ops) for x in self.argFunctionNodes() ])

    #def replace_subnodes(self, predicate, replace):
        #raise Deprecated('This is too dangerous')
        #"""Set all nodes satifying predicate to a copy of replace.

        #Note: we must fix probabilities after this since they may not be right--we can copy into a place
            #where a lambda is defined.

        #"""
        ## now go through and modify
        #for n in filter(predicate, self.subnodes()):  # NOTE: must use subnodes since we are modfiying
            #n.setto(copy(replace))

    #def partial_subtree_root_match(self, y):
        #"""Does *y* match from my root?

        #A partial tree here is one with some nonterminals (see random_partial_subtree) that
        #are not expanded

        #"""
        #if isFunctionNode(y):
            #if (y._returntype != self._returntype) or \
               #(y._name != self._name) or \
               #(len(y.args) != len(self.args)):
                #return False
            #if y.args is None:
                #return self.args is None

            #for a, b in zip(self.args, y.args):
                #if isFunctionNode(a):
                    #if not a.partial_subtree_root_match(b):
                        #return False
                #else:
                    #if isFunctionNode(b) or \
                            #(a != b):
                        #return False  # cannot work!
            #return True
        #else:
            ## else y is a string and we match if y is our returntype
            #assert isinstance(y, str)
            #return y == self._returntype

    #def partial_subtree_match(self, y):
        #"""Does `y` match a subtree anywhere?"""
        #for x in self:
            #if x.partial_subtree_root_match(y):
                #return True

        #return False

    #def random_partial_subtree(self, p=0.5):
        #"""Generate a random partial subtree of me.

        #We do this because there are waay too many unique subtrees to enumerate, and this allows a nice
        #variety of structures

        #Example
        #-------
        #>> prev_((seven_ if cardinality1_(x) else next_(next_(L_(x)))))
        #prev_(WORD)
        #prev_(WORD)
        #prev_((seven_ if cardinality1_(x) else WORD))
        #prev_(WORD)
        #prev_((seven_ if BOOL else next_(next_(L_(SET)))))
        #prev_(WORD)
        #prev_((seven_ if cardinality1_(SET) else next_(WORD)))
        #prev_(WORD)
        #prev_((seven_ if BOOL else next_(WORD)))
        #...

        #Note
        #----
        #Partial here means that we include nonterminals with probability p

        #"""
        #if self.args is None:
            #return copy(self)

        #newargs = []
        #for a in self.args:
            #if isFunctionNode(a):
                #if random() < p:
                    #newargs.append(a.returntype)
                #else:
                    #newargs.append(a.random_partial_subtree(p=p))
            #else:
                #newargs.append(a)  # string or something else

        #ret = self.__copy__(shallow=True)  # don't copy kids
        #ret.args = newargs

        #return ret

    #def uniquify_bv(self, remap=None):
        #"""
        #Go through and make each of my uuids on BVUseFunctionNodes unique

        #"""
        #from uuid import uuid4

        #if remap is None:
            #remap = dict()

        #if isinstance(self, BVAddFunctionNode):
            ## TODO: MAKE THIS THE SAME FUNCTION AS USED IN GRAMMAR_RULE
            #newbv = 'bv__'+uuid4().hex
            #if self.added_rule is not None:
                #remap[self.added_rule._name] = newbv
                #self.added_rule._name = newbv
        #elif isinstance(self, BVUseFunctionNode):
            #self._name = remap.get(self._name, self._name)

        #for a in self.argFunctionNodes():
            #a.uniquify_bv(remap)

    #def iterate_subnodes(self, t=None, d=0, predicate=lambdaTrue, do_bv=True, yield_depth=False):
        #"""Iterate through all subnodes of node *t*, while updating the added rules (bound variables)
        #so that at each subnode, the grammar is accurate to what it was.

        #Arguments
        #---------
        #grammar : LOTlib.Grammar
            #This is the grammar we're iterating through
        #t : doc?
            #doc?
        #yield_depth : bool
            #If True, we return (node, depth) instead of node.
        #predicate : function
            #Filter only the nodes that match this function (i.e. eval (function(fn) == True) on each fn).
        #do_bv : bool
            #If False, we don't do bound variables (useful for things like counting nodes,
          #instead of having to update the grammar).
        #yield_depth : bool
            #doc?

        #Note
        #----
        #if you DON'T iterate all the way through, you end up acculmulating bv rules so NEVER stop this
        #iteration in the middle!

        #TODO
        #----
        #Make this more elegant -- use BVCM

        #"""
        #if not t:
            #t = self
        #if predicate(t):
            #yield (t, d) if yield_depth else t

        ## Define a new context that is the grammar with the rule added.
        ## Then, when we exit, it's still right.
        ##with BVRuleContextManager(grammar, t, recurse_up=False):
        #for a in t.children:
            ## Pass up anything from below
            #for g in self.iterate_subnodes(a, d=d+1, do_bv=do_bv,
                                           #yield_depth=yield_depth, predicate=predicate):
                #yield g


# ============================================================================================================
# Other classes
# ============================================================================================================

#class BVAddFunctionNode(FunctionNode):
    #"""
    #(doc?)
    #"""
    #def __init__(self, parent, returntype, name, args,
                 #generation_probability=0.0, rule=None, added_rule=None):
        #FunctionNode.__init__(self, parent, returntype, name, args,
                              #generation_probability, rule)
        #self.added_rule = added_rule

    #def __copy__(self, shallow=False):
        #raise Deprecated()

    #def duplicate(self)
        #"""
        #Returns a new function node 

        #"""
        #fn = BVAddFunctionNode(self.parent, self.returntype, self._name, None,
            #generation_probability=self._generation_probability,
            #rule=self.rule, added_rule=copy(self.added_rule))

        #if (not shallow) and self.args is not None:
            #fn.args = map(copy, self.args)
        #else:
            #fn.args = self.args

        #for a in fn.children:
            #a.parent = fn

        #return fn

    #def as_list(self, d=0, bv_names=None):
        #"""Returns a list representation of the FunctionNode with function/self.name as the first element.

        #Arguments
        #---------
        #d : int
            #An optional argument that keeps track of how far down the tree we are.
        #bv_names : dict
            #A dictionary keeping track of the names of bound variables (keys = UUIDs, values = names).

        #"""
        ## initialize the bv_names variable if it's not defined
        #if bv_names is None:
            #bv_names = dict()    
        
        ## Since this is a lambda, we should add an item to the bv_names dictionary
        ## print "We are a lambda node...", self.name
        #bvn = ''
        #if self.added_rule is not None:
            #bvn = self.added_rule.bv_prefix+str(d)
            #bv_names[self.added_rule.name] = bvn
        
        ## Call super now that bv_names has been defined
        #x = FunctionNode.as_list(self, d, bv_names)
        
        ## afterwards, we should remove the BV name from the bv_names dictionary
        ## TODO: do we really need this?
        #if self.added_rule is not None:
            #del bv_names[self.added_rule.name]
 
        ## print "\tand dictionary ", bv_names, " returns: ", x
        #return x


#class BVUseFunctionNode(FunctionNode):
    #"""
    #(doc?)
    #"""
    #def __init__(self, parent, returntype, name, args,
                 #generation_probability=0.0, rule=None, bv_prefix=None):
        #FunctionNode.__init__(self, parent, returntype, name, args,
                              #generation_probability, rule)
        #self.bv_prefix = bv_prefix

    #def as_list(self, d=0, bv_names=None):
        #"""Returns a list representation of the FunctionNode with function/self.name as the first element.

        #Arguments
            #d: An optional argument that keeps track of how far down the tree we are
            #bv_names: A dictionary keeping track of the names of bound variables (keys = UUIDs,
            #values = names)

        #"""
        ## the tree should be represented as the empty set if the function node has no name
        #assert self._name is not None
        #assert self._name in bv_names
        #x = [bv_names[self._name]]

        ## and we're now ready to loop over the function node's arguments
        #if self.args is not None:
            #x.extend([a.as_list(d=d+1, bv_names=bv_names) if isFunctionNode(a) else a for a in self.args])
 
        #return x

    #def __copy__(self, shallow=False):
        #"""Copy a function node.
                
        #Note:
            #The rule is NOT deeply copied (regardless of shallow)

        #Arguments
            #shallow: if True, this does not copy the children (self.to points to the same as what we return)

        #"""
        #fn = BVUseFunctionNode(self.parent, self.returntype, self._name, None,
                               #generation_probability=self._generation_probability,
                               #rule=self.rule, bv_prefix=self.bv_prefix)
        
        #if (not shallow) and self.args is not None:
            #fn.args = map(copy, self.args)
        #else:
            #fn.args = self.args

        #for a in fn.children:
            #a.parent = fn

        #return fn

# ------------------------------------------------------------------------------------------------------------
# Helper functions

#def isFunctionNode(x):
    ## Just because this is nicer, and allows us to map, etc.
    #"""Returns true if *x* is of type FunctionNode."""
    #return isinstance(x, FunctionNode)


#def cleanFunctionNodeString(x):
    #"""Makes FunctionNode strings easier to read."""
    #s = re.sub("lambda", u"\u03BB", str(x))  # make lambdas the single char
    #s = re.sub("_", '', s)  # remove underscores
    #return s


# ------------------------------------------------------------------------------------------------------------
# Handle exceptions when sampling

#class NodeSamplingException(Exception):
    #"""Raised when we try to sample a subnode, but nothing has nonzero probability."""
    #pass


# ------------------------------------------------------------------------------------------------------------
# FunctionNode main class


## NOTE: This must come at the end to meet dependencies
#from LOTlib.Visualization.Stringification import pystring, fullstring
