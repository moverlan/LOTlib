# *- coding: utf-8 -*-
try: import numpy as np
except ImportError: import numpypy as np

from copy import copy
from collections import defaultdict
import itertools

from LOTlib import lot_iter
from LOTlib.Miscellaneous import *
from LOTlib.GrammarRule import GrammarRule, BVAddGrammarRule
from LOTlib.Hypotheses.Hypothesis import Hypothesis
from LOTlib.BVRuleContextManager import BVRuleContextManager
from LOTlib.FunctionNode import FunctionNode


class Grammar:
    """
    A PCFG-ish class that can handle special types of rules:
        - Rules that introduce bound variables
        - Rules that sample from a continuous distribution
        - Variable resampling probabilities among the rules

    Note:
        * In general, grammars should NOT allow rules of the same name and type signature.
        * This class fixes a bunch of problems that were in earlier versions, such as (doc?)

    """
    def __init__(self, BV_P=10.0, start='START'):
        self.__dict__.update(locals())
        self.rules = defaultdict(list)  # A dict from nonterminals to lists of GrammarRules.
        self.rule_count = 0
        self.bv_count = 0   # How many rules in the grammar introduce bound variables?

    def __str__(self):
        """Display a grammar."""
        return '\n'.join([str(r) for r in itertools.chain(*[self.rules[nt] for nt in self.rules.keys()])])

    def nrules(self):
        return sum([len(self.rules[nt]) for nt in self.rules.keys()])

    def is_nonterminal(self, x):
        """A nonterminal is just something that is a key for self.rules"""
        # if x is a string  &&  if x is a key
        return isinstance(x, str) and (x in self.rules)

    def display_rules(self):
        """Prints all the rules to the console."""
        for rule in self:
            print rule

    def __iter__(self):
        """Define an iterator over all rules so we can say 'for rule in grammar...'."""
        for k in self.rules.keys():
            for r in self.rules[k]:
                yield r

    def nonterminals(self):
        """Returns all non-terminals."""
        return self.rules.keys()

    def add_rule(self, nt, name, to, p, bv_type=None, bv_args=None, bv_prefix='y', bv_p=None):
        """Adds a rule and returns the added rule.

        Arguments
            nt (str): The Nonterminal. e.g. S in "S -> NP VP"
            name (str): The name of this function. NOTE: If you are introducing a bound variable,
              the name of this function must reflect that it is a lambda node! Currently, the only way to
              do this is to name it 'lambda'.
            to (list<str>): What you expand to (usually a FunctionNode).
            p (float): Unnormalized probability of expansion
            bv_type (str): What bound variable was introduced
            bv_args (list): What are the args when we use a bv (None is terminals, else a type signature)

        """
        self.rule_count += 1
        assert name is not None, "To use null names, use an empty string ('') as the name."
        if bv_type is not None:
            assert name.lower() == 'lambda', \
                "When introducing bound variables, the name of the expanded function must be 'lambda'."

            newrule = BVAddGrammarRule(nt, name,to, p=p, bv_type=bv_type, bv_args=bv_args, bv_prefix=bv_prefix, bv_p=bv_p)
        else:
            newrule = GrammarRule(nt,name,to, p=p)

        self.rules[nt].append(newrule)
        return newrule
    
    def is_terminal_rule(self, r):
        """
        Check if a rule is "terminal" - meaning that it doesn't contain any nonterminals in its expansion.
        """ 
        return not any([self.is_nonterminal(a) for a in None2Empty(r.to)])  

    def get_gp(self, lhs, rule_index, log=False):
        r = self.rules[lhs][rule_index]
        probsum = sum([rule.p for rule in self.rules[lhs]])
        if log:
            return math.log(r.p / probsum)
        else:
            return r.p / probsum
    # --------------------------------------------------------------------------------------------------------
    # Generation
    # --------------------------------------------------------------------------------------------------------
    def sample_rule(self, lhs):
        return weighted_sample(self.rules[lhs], probs=lambda x: x.p, return_probability=True, log=False)

    def make_pick_rule_fn(self):
        sofar = [self.start]
        def pick_rule(self, lhs):
            print sofar
            for i, rule in enumerate(self.rules[lhs]):
                print '[' + str(i+1) + '] ' + str(rule)

            selection = int(raw_input())-1

            r = self.rules[lhs][selection]
            gp = self.get_gp(lhs, selection, log=True)

            at = sofar.index(lhs) 
            if r.to is not None: 
                for node in reversed(r.to):
                    sofar.insert(at+1, node)
                if r.name is not '':
                    sofar.insert(at+1, r.name)
            else:
                sofar.insert(at+1, r.name)
            sofar.pop(at)

            return (r, gp)
        return pick_rule


    def generate(self, x=None, rule_sampler=sample_rule):
        """Generate from the PCFG -- default is to start from x - either a nonterminal or a FunctionNode

        Arguments:
            x (FunctionNode): What we start from -- can be None and then we use Grammar.start.

        """
        # print "# Calling grammar.generate", d, type(x), x

        # Decide what to start from based on the default if start is not specified
        if x is None:
            x = self.start
            assert self.start in self.rules, \
                "The default start symbol %s is not a defined nonterminal" % self.start

        # Dispatch different kinds of generation
        if isinstance(x,list):            
            # If we get a list, just map along it to generate.
            # We don't count lists as depth--only FunctionNodes.
            return map(lambda xi: self.generate(x=xi, rule_sampler=rule_sampler), x)
        elif self.is_nonterminal(x):

            # sample a grammar rule
            r, gp = rule_sampler(self, x)

            # Make a stub for this functionNode 
            fn = r.make_FunctionNodeStub(self, gp, None) 

            # Define a new context that is the grammar with the rule added
            # Then, when we exit, it's still right.
            with BVRuleContextManager(self, fn, recurse_up=False):      # not sure why we can't use with/as:
                # Can't recurse on None or else we genreate from self.start
                if fn.args is not None:
                    # and generate below *in* this context (e.g. with the new rules added)
                    try:
                        fn.args = self.generate(fn.args, rule_sampler=rule_sampler)
                    except RuntimeError as e:
                        print "*** Runtime error in %s" % fn
                        raise e


                # and set the parents
                for a in fn.argFunctionNodes():
                    a.parent = fn

            return fn

        else:  # must be a terminal
            assert isinstance(x, str), ("*** Terminal must be a string! x="+x)
            return x

    def enumerate(self, d=20, nt=None, leaves=True):
        """Enumerate all trees up to depth n.

        Parameters:
            d (int): how deep to go? (defaults to 20 -- if Infinity, enumerate() runs forever)
            nt (str): the nonterminal type
            leaves (bool): do we put terminals in the leaves or leave nonterminal types? This is useful in
              PartitionMCMC

        """
        for i in infrange(d):
            for t in self.enumerate_at_depth(i, nt=nt, leaves=leaves):
                yield t

    def enumerate_at_depth(self, d, nt=None, leaves=True):
        """Generate trees at depth d, no deeper or shallower.

        Parameters
            d (int): the depth of trees you want to generate
            nt (str): the type of the nonterminal you want to return (None reverts to self.start)
            leaves (bool): do we put terminals in the leaves or leave nonterminal types? This is useful in
              PartitionMCMC. This returns trees of depth d-1!

        Return:
            yields the ...

        """
        if nt is None:
            nt = self.start

        # handle garbage that may be passed in here
        if not self.is_nonterminal(nt):
            yield nt
            raise StopIteration

        Z = log(sum([r.p for r in self.rules[nt]]))
        if d == 0:
            if leaves:
                # Note: can NOT use filter here, or else it doesn't include added rules
                for r in self.rules[nt]:
                    if self.is_terminal_rule(r):
                        yield r.make_FunctionNodeStub(self, (log(r.p) - Z), None)
            else:
                # If not leaves, we just put the nonterminal type in the leaves
                yield nt
        else:
            # Note: can NOT use filter here, or else it doesn't include added rules. No sorting either!
            for r in self.rules[nt]:

                # No good since it won't be deep enough
                if self.is_terminal_rule(r):
                    continue


                fn = r.make_FunctionNodeStub(self, (log(r.p) - Z), None)

                # The possible depths for the i'th child
                # Here we just ensure that nonterminals vary up to d, and otherwise
                child_i_depths = lambda i: xrange(d) if self.is_nonterminal(fn.args[i]) else [0]

                # The depths of each kid
                for cd in lazyproduct(map(child_i_depths, xrange(len(fn.args))), child_i_depths):

                    # One must be equal to d-1
                    # TODO: can be made more efficient via permutations. Also can skip terminals in args.
                    if max(cd) < d-1:
                        continue
                    assert max(cd) == d-1

                    myiter = lazyproduct(
                        [self.enumerate_at_depth(di, nt=a, leaves=leaves) for di, a in zip(cd, fn.args)],
                        lambda i: self.enumerate_at_depth(cd[i], nt=fn.args[i], leaves=leaves))
                    try:
                        while True:
                            # Make a copy so we don't modify anything
                            yieldfn = copy(fn)

                            # BVRuleContextManager here makes us remove the rule BEFORE yielding,
                            # or else this will be incorrect. Wasteful but necessary.
                            with BVRuleContextManager(self, fn, recurse_up=False):
                                yieldfn.args = myiter.next()
                                for a in yieldfn.argFunctionNodes():
                                    # Update parents
                                    a.parent = yieldfn

                            yield copy(yieldfn)

                    except StopIteration:
                        # Catch this here so we continue in this loop over rules
                        pass

    def depth_to_terminal(self, x, openset=None, current_d=None):
        """
        Return a dictionary that maps both this grammar's rules and its nonterminals to a number,
        giving how quickly we can go from that nonterminal or rule to a terminal.

        Arguments:
            openset(doc?): stores the set of things we're currently trying to compute for. We must skip rules
              that contain anything in there, since they have to be defined still, and so we want to avoid
              a loop.

        """
        if current_d is None: 
            current_d = dict()
            
        if openset is None:
            openset = set()
            
        openset.add(x)
        
        if isinstance(x, GrammarRule):
            if x.to is None or len(x.to) == 0:
                current_d[x] = 0 # we are a terminal
            else:
                current_d[x] = 1 + max([(self.depth_to_terminal(a, openset=openset, current_d=current_d)
                                        if a not in openset else 0) for a in x.to])
        elif isinstance(x, str):
            if x not in self.rules:
                current_d[x] = 0    # A terminal
            else:
                current_d[x] = min([(self.depth_to_terminal(r, openset=openset, current_d=current_d)
                                    if r not in openset else Infinity) for r in self.rules[x]])
        else:
            assert False, "Shouldn't get here!"

        openset.remove(x)
        return current_d[x]

