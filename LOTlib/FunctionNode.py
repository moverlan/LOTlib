# -*- coding: utf-8 -*-

"""
        A function node -- a tree part representing a function and its arguments.
        Also used for PCFG rules, where the arguments are nonterminal symbols.

"""

import re
from copy import copy, deepcopy
from math import log
from random import random
import graphviz
from LOTlib.Miscellaneous import None2Empty, lambdaTrue, Infinity

"""
==============================================================================================================================================
== Helper functions 
==============================================================================================================================================
"""

def isFunctionNode(x):
    # just because this is nicer, and allows us to map, etc.
    """
            Returns true if *x* is of type FunctionNode.
    """
    return isinstance(x, FunctionNode)


def cleanFunctionNodeString(x):
    """
            Makes FunctionNode strings easier to read
    """
    s = re.sub("lambda", u"\u03BB", str(x))  # make lambdas the single char
    s = re.sub("_", '', s)  # remove underscores
    return s



def DOTstring_old(x, d=0, bv_names=dict()):
    """
    Outputs a string in (lambda (x) (+ x 3)) format.

    """

    if d == 0:
        return 'digraph g {'+DOTstring(x,d=1)+'\n}'

    if isinstance(x, str):
        return x
    elif isFunctionNode(x):

        name = x.name
        if isinstance(x, BVUseFunctionNode):
            name = bv_names.get(x.name, x.name)

        if x.args is None:
            s = name+';\n'
            return name
        else:
            if x.args is None:
                return name
            elif isinstance(x, BVAddFunctionNode):
                assert name is 'lambda'
                s = name + ';\n\t'
                s = s+x.added_rule.name+';\n\t'
                s = s+map(lambda a: DOTstring(a, d+1, bv_names=bv_names), x.args) + ';\n\t'
                return s
                # return "(%s (%s) %s)" % (name, x.added_rule.name, map(lambda a: DOTstring(a,d+1,bv_names=bv_names), x.args))
            else:
                s = name + ';\n\t'
                s = s+map(lambda a: DOTstring(a, d+1, bv_names=bv_names), x.args) + ';\n\t'
                return s
                # return "(%s %s)" % (name, map(lambda a: DOTstring(a,d+1,bv_names=bv_names), x.args))


"""
==============================================================================================================================================
== String casting functions
==============================================================================================================================================
"""

def schemestring(x, d=0, bv_names=None):
    """
    Outputs a scheme string in (lambda (x) (+ x 3)) format.

    *bv_names* - a dictionary from the uuids to nicer names
    """

    if isinstance(x, str):
        return x
    elif isFunctionNode(x):

        if bv_names is None:
            bv_names = dict()

        name = x.name
        if isinstance(x, BVUseFunctionNode):
            name = bv_names.get(x.name, x.name)

        if x.args is None:
            return name
        else:
            if x.args is None:
                return name
            elif isinstance(x, BVAddFunctionNode):
                assert name is 'lambda'
                return "(%s (%s) %s)" % (name, x.added_rule.name, map(lambda a: schemestring(a,d+1,bv_names=bv_names), x.args))
            else:
                return "(%s %s)" % (name, map(lambda a: schemestring(a,d+1,bv_names=bv_names), x.args))

def pystring(x, d=0, bv_names=None):
    """
    Outputs a string that can be evaluated by python. This gives bound variables names based on their depth
    
    *bv_names* - a dictionary from the uuids to nicer names
    """
    
    if isinstance(x, str): 
        return x 
    elif isFunctionNode(x):
        
        if bv_names is None:
            bv_names = dict()    
        
        if x.name == "if_": # this gets translated
            assert len(x.args) == 3, "if_ requires 3 arguments!"
            # This converts from scheme (if bool s t) to python (s if bool else t)
            b = pystring(x.args[0], d=d+1, bv_names=bv_names)
            s = pystring(x.args[1], d=d+1, bv_names=bv_names)
            t = pystring(x.args[2], d=d+1, bv_names=bv_names)
            return '( %s if %s else %s )' % (s, b, t)
        elif x.name == '':
            assert len(x.args) == 1, "Null names must have exactly 1 argument"
            return pystring(x.args[0], d=d, bv_names=bv_names)
        elif x.name == "apply_":
            assert x.args is not None and len(x.args)==2, "Apply requires exactly 2 arguments"
            #print ">>>>", self.args
            return '( %s )( %s )' % tuple(map(lambda x: pystring(x, d=d, bv_names=bv_names), x.args))
        elif x.name == "or_sc_": # short-circuit or
            return "(%s)" % ' or '.join(map(lambda x: pystring(x, d=d, bv_names=bv_names), x.args))
        elif x.name == "and_sc_": # short-circuit and
            return "(%s)" % ' and '.join(map(lambda x: pystring(x, d=d, bv_names=bv_names), x.args))
        elif x.name == 'lambda':
            # On a lambda, we must add the introduced bv, and then remove it again afterwards
            
            bvn = ''
            if isinstance(x, BVAddFunctionNode) and x.added_rule is not None:
                bvn = x.added_rule.bv_prefix+str(d)
                bv_names[x.added_rule.name] = bvn
            
            assert len(x.args) == 1
            ret = 'lambda %s: %s' % ( bvn, pystring(x.args[0], d=d+1, bv_names=bv_names) )
            
            if x.added_rule is not None:
                del bv_names[x.added_rule.name]
                
            return ret  
        else:
            
            name = x.name
            if isinstance(x, BVUseFunctionNode):
                name = bv_names.get(x.name, x.name) 
        
            if x.args is None:             
                return name
            else:
                return name+'('+', '.join(map(lambda a: pystring(a, d=d+1, bv_names=bv_names), x.args))+')'


"""
==============================================================================================================================================
== FunctionNode main class
==============================================================================================================================================
"""

class FunctionNode(object):
    """
    Args:
    *returntype*
            The return type of the FunctionNode

    *name*
            The name of the function

    *args*
            Arguments of the function

    *generation_probability*
            Unnormalized generation probability.

    *resample_p*
            The probability of choosing this node in resampling. Takes any number >0 (all are normalized)

    *rule* - The rule that was used in generating the FunctionNode

    NOTE: If a node has [ None ] as args, it is treated as a thunk

    bv - stores the actual *rule* that was added (so that we can re-add it when we loop through the tree)

    """
    def __init__(self, parent, returntype, name, args, generation_probability=0.0, resample_p=1.0, rule=None, a_args=None):
        self.__dict__.update(locals())
        self.added_rule = None
        
        assert self.name is None or isinstance(self.name, str)
        
        if self.name is not None and self.name.lower() == 'applylambda':
            raise NotImplementedError # Let's not support any applylambda for now
    
    def setto(self, q):
        """
                Makes all the parts the same as q, not copies. 
                Note that this sets the parent of q to my current parent! 
        """
        
        old_parent = self.parent # preserve my parent
        
        self.__dict__ = q.__dict__
        self.__class__ = q.__class__ # to update in case q is a different subtype of FunctionNode. NOTE: Setting __class__ is not a recommended thing to do.
        
        # and we must fix the kid refs. Everything else should be right.
        for a in self.argFunctionNodes():
            a.parent = self
        
        self.parent = old_parent

    def __copy__(self, shallow=False):
        """
                Copy a function node. 
                
                NOTE: The rule is NOT deeply copied (regardless of shallow)

                *shallow* - if True, this does not copy the children (self.to points to the same as what we return)
        """
        
        fn = FunctionNode(self.parent, self.returntype, self.name, None,
                          generation_probability=self.generation_probability,
                          resample_p=self.resample_p, rule=self.rule)
        
        if (not shallow) and self.args is not None:
            fn.args = map(copy, self.args)
        else:
            fn.args = self.args

        # and update 
        for a in fn.argFunctionNodes():
            a.parent = fn 

        return fn 
        
    def is_nonfunction(self):
        """
                Returns True if the Node contains no function arguments, False otherwise.
        """
        return (self.args is None)

    def is_function(self):
        """
                Returns True if the Node contains function arguments, False otherwise.
        """
        return not self.is_nonfunction()

    def is_leaf(self):
        """
                Returns True if none of the kids are FunctionNodes, meaning that this should be considered a "leaf"
                NOTE: A leaf may be a function, but its args are specified in the grammar.
        """
        return (self.args is None) or all([not isFunctionNode(c) for c in self.args])

    def is_root(self):
        return self.parent is None
    
    def check_parent_refs(self):
        """
            Recurse through the tree and ensure that the parent refs are good
        """
        for t in self.argFunctionNodes():
            if (t.parent is not self) or (t.check_parent_refs() is not True):
                print "Bad parent reference at %s"%t.name
                print "If it prints, the full string is %s, a subnode of %s, whose parent is %s" % (t, self, t.parent)
                return False
            
        return True
    
    def check_generation_probabilities(self, grammar):
        """
            Check this node's generation probabilities. NOTE: The can only be called on root -- no bvs allowed unless they are introduced, 
            or else grammar.recompute_generation_probabilities will not work right
        """
        # and check the generation probabilities -- that these are set correctly
        gps  = [t.generation_probability for t in self]
        grammar.recompute_generation_probabilities(self) # re-check these
        gps2 = [t.generation_probability for t in self]
        for a,b,n in zip(gps, gps2, self.subnodes()):
            if abs(a-b) > 0.0001:
                print "# Wrong generation probabilities %s %s for %s" % (a, b, n)
                return False
            
        return True

    def as_list(self, d=0, bv_names=None):
        """Returns a list representation of the FunctionNode with function/self.name as the first element.

        This function is subclassed so by BVAdd and BVUse so that those handle other cases

        Args:
            d: An optional argument that keeps track of how far down the tree we are
            bv_names: A dictionary keeping track of the names of bound variables (keys = UUIDs,
                values = names)

        """
        # the tree should be represented as the empty set if the function node has no name
        if self.name == '':
            x = []
        else:
            x = [self.name]
            
        # and we're now ready to loop over the function node's arguments
        if self.args is not None:
            x.extend([a.as_list(d=d+1, bv_names=bv_names) if isFunctionNode(a) else a for a in self.args])
        
        return x
        
    
    def quickstring(self):
        """
            A (maybe??) faster string function used for hashing -- doesn't handle any details and is meant
            to just be quick
        """

        if self.args is None:
            return str(self.name)  # simple call

        else:
            # Don't use + to concatenate strings.
            return '{} {}'.format(str(self.name), ','.join(map(str, self.args)))

    def fullprint(self, d=0):
        """ A handy printer for debugging"""
        tabstr = "  .  " * d
        print tabstr, self.returntype, self.name, "\t", self.generation_probability, "\t", self.resample_p, self.added_rule
        if self.args is not None:
            for a in self.args:
                if isFunctionNode(a):
                    a.fullprint(d+1)
                else:
                    print tabstr, a

    def liststring(self, cons="cons_"):
        """
            This "evals" cons_ so that we can conveniently build lists (of lists) without having to eval.
            Mainly useful for combinatory logic, or "pure" trees
        """
        if self.args is None:
            return self.name
        elif self.name == cons:
            return map(lambda x: x.liststring(), self.args)
        else:
            assert False, "FunctionNode must only use cons to call liststring!"

    def make_dot(self, ls=None, n='0', parent_n=None):
        print '*'*80
        print 'ls = ', ls
        print 'n = ', n
        print 'parent_n = ', parent_n
        print '*'*80
        # Initialize
        if not hasattr(self, 'dot'):
            self.dot = graphviz.Digraph(comment='The DOT Graph')
        if ls is None:
            ls = self.as_list()[0]
        this_n = n
        d = self.dot

        # Draw the graph
        if not isinstance(ls, list):
            d.node(this_n, label=str(ls), shape='square')
            if not (parent_n is None):
                d.edge(parent_n, this_n, style='dotted')
                # do something fun!
        elif len(ls) >= 1:
            d.node(this_n, label=str(ls[0]), shape='plaintext')
            if not (parent_n is None):
                d.edge(parent_n, this_n, style='solid')
        if len(ls) > 1:
            for i in range(0, len(ls)):
                # Recursive call
                self.make_dot(ls[i], n=this_n+str(i), parent_n=this_n)

    def to_dot(self):
        return self.dot.source

    # NOTE: in the future we may want to change this to do fancy things
    def __str__(self):
        return pystring(self)

    def __repr__(self):
        return pystring(self)

    def __ne__(self, other):
        return (not self.__eq__(other))

    
    def __eq__(self, other):
        """
            Check if two FunctionNodes are equal. This is actually a little subtle due to bound variables. In (lambda (x) x) and (lambda (y) y) will be equal (since they map
            to identical strings via pystring), even though the nodes below x and y will not themselves be equal. This is because pystring(x) and pystring(y) will not know 
            where these came from and will just cmopare the uuids. But pystring on the lambda keeps track of where bound variables were introduced. 
        """
        return pystring(self) == pystring(other)
    
    
    ## TODO: overwrite these with something faster
    # hash trees. This just converts to string -- maybe too slow?
    def __hash__(self):

        # An attempt to speed things up -- not so great!
        #hsh = self.ruleid
        #if self.args is not None:
            #for a in filter(isFunctionNode, self.args):
                #hsh = hsh ^ hash(a)
        #return hsh

        # normal string hash -- faster?
        return hash(str(self))

        # use a quicker string hash
        #return hash(self.quickstring())

    def __cmp__(self, x):
        return cmp(str(self), str(x))

    def __len__(self):
        return len([a for a in self])

    def log_probability(self):
        """
                Compute the log probability of a tree
        """
        return self.generation_probability + sum([x.log_probability() for x in self.argFunctionNodes()])

    def subnodes(self):
        """
                Return all subnodes -- no iterator.
                Useful for modifying

                NOTE: If you want iterate using the grammar, use Grammar.iterate_subnodes
        """
        return [g for g in self]

    def argFunctionNodes(self):
        """
                Yield FunctionNode immediately below
                Also handles args is None, so we don't have to check constantly
        """
        if self.args is not None:
            # TODO: In python 3, use yeild from
            for n in filter(isFunctionNode, self.args):
                yield n

    def is_terminal(self):
        """
            A FunctionNode is considered a "terminal" if it has no FunctionNodes below
        """
        return self.args is None or len(filter(isFunctionNode, self.args)) == 0

    def __iter__(self):
        """
                Iterater for subnodes.
                NOTE: This will NOT work if you modify the tree. Then all goes to hell.
                      If the tree must be modified, use self.subnodes()
        """
        yield self

        for a in self.argFunctionNodes():
            for ssn in a:
                yield ssn

    def iterdepth(self):
        """
                Iterates subnodes, yielding node and depth
        """
        yield (self, 0)

        if self.args is not None:
            for a in self.argFunctionNodes():
                for ssn, dd in a.iterdepth():
                    yield (ssn, dd+1)

    def all_leaves(self):
        """
                Returns a generator for all leaves of the subtree rooted at the instantiated FunctionNode.
        """
        if self.args is not None:
            for i in range(len(self.args)):  # loop through kids
                if isFunctionNode(self.args[i]):
                    for ssn in self.args[i].all_leaves():
                        yield ssn
                else:
                    yield self.args[i]

    def string_below(self, sep=" "):
        """
                The string of terminals (leaves) below the current FunctionNode in the parse tree.

                *sep* is the delimiter between terminals. E.g. sep="," => "the,fuzzy,cat"
        """
        return sep.join(map(str, self.all_leaves()))


    ############################################################
    ## Derived functions that build on the above core
    ############################################################

    def contains_function(self, x):
        """
                Checks if the FunctionNode contains x as function below
        """
        for n in self:
            if n.name == x:
                return True
        return False

            
    def up_to(self, to=None):
        """
            Yield all nodes going up to "to". If "to" is None, we go until the root (default)
        """
        ptr = self
        while (ptr is not to) and (ptr is not None):
            yield ptr
            ptr = ptr.parent

    def count_nodes(self):
        """
                Returns the subnode count.
        """
        return self.count_subnodes()

    def count_subnodes(self, predicate=lambdaTrue):
        """
                Returns the subnode count.
        """
        return len(filter(predicate, self))

    def depth(self):
        """
                Returns the depth of the tree (how many embeddings below)
        """
        depths = [a.depth() for a in self.argFunctionNodes()]
        depths.append(-1)  # for no function nodes (+1=0)
        return max(depths)+1

    def sample_node_normalizer(self, predicate=lambdaTrue):
        """
            Compute Z to be the sum of all subnodes' resample_p
        """
        return sum([ t.resample_p for t in filter(predicate, self)])
    
    def sample_subnode(self, predicate=lambdaTrue):
        """
            Sample a subnode at random. 
            We return a sampled tree and the log probability of sampling it
        """
        Z = self.sample_node_normalizer(predicate=predicate) # the total probability
        
        if Z == 0.0: return None, -Infinity # nothing works!
        
        r = random() * Z # now select a random number (giving a random node)
        
        for t in filter(predicate, self):
            r -= t.resample_p
            if r <= 0:
                return [t, log(t.resample_p) - log(Z)]

    # get a description of the input and output types
    # if collapse_terminal then we just map non-FunctionNodes to "TERMINAL"
    def type(self):
        """
                The type of a FunctionNode is defined to be its returntype if it's not a lambda,
                or is defined to be the correct (recursive) lambda structure if it is a lambda.
                For instance (lambda x. lambda y . (and (empty? x) y))
                is a (SET (BOOL BOOL)), where in types, (A B) is something that takes an A and returns a B
        """

        if self.name == '':  # If we don't have a function call (as in START), just use the type of what's below
            assert len(self.args) == 1, "**** Nameless calls must have exactly 1 arg"
            return self.args[0].type()
        if not (isinstance(self, BVAddFunctionNode) and self.added_rule is not None):
            return self.returntype
        else:
            # figure out what kind of lambda
            t = []
            if self.added_rule is not None and self.added_rule.to is not None:
                t = tuple( [self.added_rule.nt,] + copy(self.self.added_rule.to) )
            else:
                t = self.added_rule.nt

            return (self.args[0].type(), t)

    def is_canonical_order(self, symmetric_ops):
        """
                Takes a set of symmetric (commutative) ops (plus, minus, times, etc, not divide)
                and asserts that the LHS ordering is less than the right (to prevent)

                This is useful for removing duplicates of nodes. For instance,

                        AND(X, OR(Y,Z))

                is logically the same as

                        AND(OR(Y,Z), X)

                This function essentially checks if the tree is in sorted (alphbetical)
                order, but only for functions whose name is in symmetric_ops.
        """
        if self.args is None or len(self.args) == 0:
            return True

        if self.name in symmetric_ops:

            # Then we must check children
            if self.args is not None:
                for i in xrange(len(self.args)-1):
                    if self.args[i].name > self.args[i+1].name:
                        return False

        # Now check the children, whether or not we are symmetrical
        return all([x.is_canonical_order(symmetric_ops) for x in self.argFunctionNodes() ])

    def replace_subnodes(self, predicate, replace):
        """
              Set all nodes satifying predicate to a copy of replace. 
              NOTE: we must fix probabilities after this since they may not be right--we can copy into a place
              where a lambda is defined. 
        """

        # now go through and modify
        for n in filter(predicate, self.subnodes()):  # NOTE: must use subnodes since we are modfiying
            n.setto(copy(replace))

    def partial_subtree_root_match(self, y):
        """
                Does *y* match from my root?

                A partial tree here is one with some nonterminals (see random_partial_subtree) that
                are not expanded
        """
        if isFunctionNode(y):
            if y.returntype != self.returntype:
                return False

            if y.name != self.name:
                return False

            if y.args is None:
                return self.args is None

            if len(y.args) != len(self.args):
                return False

            for a, b in zip(self.args, y.args):
                if isFunctionNode(a):
                    if not a.partial_subtree_root_match(b):
                        return False
                else:
                    if isFunctionNode(b):
                        return False  # cannot work!

                    # neither is a function node
                    if a != b:
                        return False

            return True
        else:
            # else y is a string and we match if y is our returntype
            assert isinstance(y, str)
            return y == self.returntype

    def partial_subtree_match(self, y):
        """
                Does *y* match a subtree anywhere?
        """
        for x in self:
            if x.partial_subtree_root_match(y):
                return True

        return False

    def random_partial_subtree(self, p=0.5):
        """
                Generate a random partial subtree of me. So that

                this:
                        prev_((seven_ if cardinality1_(x) else next_(next_(L_(x)))))
                yeilds:

                        prev_(WORD)
                        prev_(WORD)
                        prev_((seven_ if cardinality1_(x) else WORD))
                        prev_(WORD)
                        prev_((seven_ if BOOL else next_(next_(L_(SET)))))
                        prev_(WORD)
                        prev_((seven_ if cardinality1_(SET) else next_(WORD)))
                        prev_(WORD)
                        prev_((seven_ if BOOL else next_(WORD)))
                        ...

                We do this because there are waay too many unique subtrees to enumerate,
                and this allows a nice variety of structures
                NOTE: Partial here means that we include nonterminals with probability p
        """

        if self.args is None:
            return copy(self)

        newargs = []
        for a in self.args:
            if isFunctionNode(a):
                if random() < p:
                    newargs.append(a.returntype)
                else:
                    newargs.append(a.random_partial_subtree(p=p))
            else:
                newargs.append(a)  # string or something else

        ret = self.__copy__(shallow=True)  # don't copy kids
        ret.args = newargs

        return ret

class BVAddFunctionNode(FunctionNode):
    def __init__(self, parent, returntype, name, args, generation_probability=0.0, resample_p=1.0, rule=None, a_args=None, added_rule=None):
        FunctionNode.__init__(self, parent, returntype, name, args, generation_probability, resample_p, rule, a_args)
        self.added_rule = added_rule


    def __copy__(self, shallow=False):
        """
                Copy a function node. 
                
                NOTE: The rule is NOT deeply copied (regardless of shallow)

                *shallow* - if True, this does not copy the children (self.to points to the same as what we return)
        """
        fn = BVAddFunctionNode(self.parent, self.returntype, self.name, None,
                          generation_probability=self.generation_probability,
                          resample_p=self.resample_p, rule=self.rule, a_args=self.a_args, added_rule=self.added_rule)
        
        if (not shallow) and self.args is not None:
            fn.args = map(copy, self.args)
        else:
            fn.args = self.args

        for a in fn.argFunctionNodes():
            a.parent = fn

        return fn

    
    def as_list(self, d=0, bv_names=None):
        """
                Returns a list representation of the FunctionNode with function/self.name as the first element.

                *d* An optional argument that keeps track of how far down the tree we are

                *bv_names* A dictionary keeping track of the names of bound variables (keys = UUIDs, values = names)
        """
        
        # initialize the bv_names variable if it's not defined
        if bv_names is None:
            bv_names = dict()    
        
        # Since this is a lambda, we should add an item to the bv_names dictionary
        # print "We are a lambda node...", self.name
        bvn = ''
        if self.added_rule is not None:
            bvn = self.added_rule.bv_prefix+str(d)
            bv_names[self.added_rule.name] = bvn
        
        # Call super now that bv_names has been defined
        x = FunctionNode.as_list(self, d, bv_names)
        
        # afterwards, we should remove the BV name from the bv_names dictionary
        # TODO: do we really need this?
        if self.added_rule is not None:
            del bv_names[self.added_rule.name]
 
        # print "\tand dictionary ", bv_names, " returns: ", x
        return x


class BVUseFunctionNode(FunctionNode):
    def __init__(self, parent, returntype, name, args, generation_probability=0.0, resample_p=1.0, rule=None, a_args=None, bv_prefix=None):
        FunctionNode.__init__(self, parent, returntype, name, args, generation_probability, resample_p, rule, a_args)
        self.bv_prefix = bv_prefix

    def as_list(self, d=0, bv_names=None):
        """
                Returns a list representation of the FunctionNode with function/self.name as the first element.

                *d* An optional argument that keeps track of how far down the tree we are

                *bv_names* A dictionary keeping track of the names of bound variables (keys = UUIDs, values = names)
        """
        
        # the tree should be represented as the empty set if the function node has no name
        assert self.name is not None
        assert self.name in bv_names
        x = [bv_names[self.name]]

        # and we're now ready to loop over the function node's arguments
        if self.args is not None:
            x.extend([a.as_list(d=d+1, bv_names=bv_names) if isFunctionNode(a) else a for a in self.args])
 
        return x

    def __copy__(self, shallow=False):
        """
                Copy a function node. 
                
                NOTE: The rule is NOT deeply copied (regardless of shallow)

                *shallow* - if True, this does not copy the children (self.to points to the same as what we return)
        """
        fn = BVUseFunctionNode(self.parent, self.returntype, self.name, None,
                          generation_probability=self.generation_probability,
                          resample_p=self.resample_p, rule=self.rule, a_args=self.a_args, bv_prefix=self.bv_prefix)
        
        if (not shallow) and self.args is not None:
            fn.args = map(copy, self.args)
        else:
            fn.args = self.args

        for a in fn.argFunctionNodes():
            a.parent = fn

        return fn


