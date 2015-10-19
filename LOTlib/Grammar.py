# *- coding: utf-8 -*-
try: import numpy as np
except ImportError: import numpypy as np

from copy import copy
from collections import defaultdict
import itertools

from LOTlib import lot_iter
from LOTlib.Miscellaneous import *
from LOTlib.GrammarRule import GrammarRule#, BVAddGrammarRule
from LOTlib.Hypotheses.Hypothesis import Hypothesis
#from LOTlib.BVRuleContextManager import BVRuleContextManager
from LOTlib.FunctionNode import FunctionNode

class Immutable(Exception):
    pass


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
    def __init__(self, rules, bv_p=1.0, start='START'):
        self._bv_p = bv_p
        self._start = start
        self._rules = {}  # A dict from nonterminals to lists of GrammarRules.
        # TODO get params from rules
        self._params = {} # params for production probs. dict from name to (lhs, rule_index) pair
        #self.cached_probs = {} # list of unnormalized probs for a given lhs

        for rule in rules:
            if lhs not in self._rules:
                self.rules[lhs] = []
            if rule.is_lambda and rule.bv_type not in self.rules:
                self.rules[rule.bv_type] = []

        self._bv_rule_cache = RuleCache(self.nonterminals)


        # LEFT OFF HERE (whatever that means)


    def __str__(self):
        """Display a grammar."""
        return '\n'.join(self.rules)

    @property
    def rules(self):
        return self.rules

    @property
    def n_rules(self):
        return len(self.rules)

    @property
    def start_rule(self):
        return list(self.rules_where(lhs=self._start))[0]

    @property
    def nonterminals(self):
        """Returns all non-terminals."""
        return self._rules.keys()

    def is_nonterminal(self, x):
        """A nonterminal is just something that is a key for self._rules"""
        # if x is a string  &&  if x is a key
        #print 'is', x, 'in', self._rules.keys()
        #print (x in self._rules)
        return isinstance(x, str) and (x in self._rules or x in self._bv_rules)

    #def display_rules(self):
        #"""Prints all the rules to the console."""
        #for rule in self:
            #print rule

    @property
    def rules(self):
        return self.rules_where()

    def __iter__(self):
        self.freeze()
        for rule in self.rules_where(): # all
            yield rule
        #for k in self._rules.keys():
            #for r in self._rules[k]:
                #yield r

    def init_bv_rules(self):
        self._bv_rules = {bv_type: [] for bv_type in self._bv_prefix}

    def bv_rules(self, lhs):
        self.freeze()
        if lhs in self._bv_rules:
            return self._bv_rules[lhs]
        else:
            return []

    def static_rules(self, lhs):
        if lhs in self._rules:
            return self._rules[lhs]
        else:
            return []

    def cached_rules(self, lhs):
        self.freeze()
        if lhs in self._cached_rules:
            return self._cached_rules[lhs]
        else:
            return []

    def bv_prefix(self, bv_type):
        self.freeze()
        return self._bv_prefix[bv_type]

    def get_rule(self, lhs, index):
        """
        returns the index'th rule with the given lhs
        """
        self._frozen = True
        rules = self._rules_where(lhs=lhs) + self.bv_rules(lhs)
        return rules[index]

    # generates all rules that match the given criteria
    def rules_where(self, lhs=None, name=None, to=None):
        if lhs is None:
            nts = self.nonterminals
        else:
            if lhs not in self._rules and lhs not in self._bv_rules:
                return
                #raise Exception('Non-existant lhs')
            nts = [lhs]
        for lhs in nts:
            for r in self.static_rules(lhs) + self.bv_rules(lhs):
                if name is not None and not r._name == name:
                    continue
                if to is not None and not r._to == to:
                    continue
                yield r

    def is_terminal_rule(self, r):
        """
        Check if a rule is "terminal" - meaning that it doesn't contain any nonterminals in its expansion.
        """ 
        self.freeze()
        return not any([self.is_nonterminal(arg) in r.to])  

    def probs(self, lhs):
        """
        returns a list of the unnormalized probs for all rules with the given lhs
        """
        self.freeze()
        if lhs not in self.cached_probs:
            self.cached_probs[lhs] = [rule.p for rule in self.rules_where(lhs=lhs)]
        return self.cached_probs[lhs]

    def get_gp(self, rule, log=True):
        """
        returns normalized production probability for the given rule
        """
        self.freeze()
        Z = sum(self.probs(rule.lhs))
        if log:
            return math.log(rule.p / Z)
        else:
            return rule.p / Z

    # --------------------------------------------------------------------------------------------------------
    # Generation
    # --------------------------------------------------------------------------------------------------------
    def sample_rule(self, lhs, node=None):
        samp = weighted_sample(list(self.rules_where(lhs=lhs)), probs=lambda x: x._p, return_probability=True, log=False)
        if samp is None:
            raise Exception('No sample found')
        return samp[0]

    #def make_pick_rule_fn(self):
        #sofar = [self._start]
        #def pick_rule(self, lhs):
            #print sofar
            #for i, rule in enumerate(self.rules_where(lhs=lhs)):
                #print '[' + str(i+1) + '] ' + str(rule)

            #selection = int(raw_input())-1

            #r = self.get_rule(lhs, selection)

            #at = sofar.index(lhs) 
            #if r._to is not None: 
                #for node in reversed(r._to):
                    #sofar.insert(at+1, node)
                #if r.name is not '':
                    #sofar.insert(at+1, r._name)
            #else:
                #sofar.insert(at+1, r._name)
            #sofar.pop(at)

            #return (r, gp)
        #return pick_rule

    def manual_input(self, lhs, node):
        print node.root
        for i, rule in enumerate(self.rules_where(lhs=lhs)):
            print '[' + str(i+1) + '] ' + str(rule)
        selection = int(raw_input())-1
        return self.get_rule(lhs, selection)

    def from_list(self, rule_indexes):
        def frm_list(self, lhs, node):
            for i in rule_indexes:
                yield self.get_rule(lhs, i)
        return frm_list

    def generate(self, rule_sampler=sample_rule, node=None):
        self.freeze()
        """
        Generate a new function node with this grammar

        Arguments:
            rule_sampler (function): Function that takes a nonterminal and node for context, and
                returns a rule with lhs = that nonterminal
            node (FunctionNode): Node to generate from -- can be None and then we use Grammar.start.
        """

        if node is None:
            self.init_bv_rules()
            node = FunctionNode(parent=None, rule=self.start_rule, bv_rules=copy(self._bv_rules), gp=0.0)

        #self._bv_rules = node._bv_rules
        lhs = node._rule.lhs 
        print lhs, node._name, self.bv_rules('BV_TOKEN')

        for i, lhs in self.enumerate_unset_children(node):
            rule = rule_sampler(self, lhs, node)
            gp = self.get_gp(rule)

            new_node = FunctionNode(node, rule, bv_rules=copy(node._bv_rules), gp=gp)
            varname = self.update_bv_state(rule, new_node)
            if varname:
                new_node.set_varname(varname)
            #print 'setting child', i, lhs
            #print 'with bv state', node._bv_rules['BV_TOKEN']
            if varname, added_rule
            node.set_child(i, something)

        for child in node.children:
            #print 'child', type(child), child
            self.generate(rule_sampler, child)
            print 'resetting bv to', lhs, node._name, node._bv_rules['BV_TOKEN']
            self._bv_rules = node._bv_rules

        return node

    def iter(self, node):
        self._bv_rules = node._bv_rules
        yield node
        for child in node.children:
            for gchild in self.iter(child):
                yield gchild

    def enumerate_unset_children(self, node):
        #print node._rule.lhs, '->'
        for i, arg in enumerate(node.args):
            #print ' ', arg
            if self.is_nonterminal(arg):
                #print 'yielding it'
                yield i, arg
            #else:
                #print self._bv_rules

class RuleCache(object):
    def __init__(self, bv_types):
        self.cache = {bv_type: [] for bv_type in bv_types}

    def _add(self, rule):
        """
        This stores a bv rule --  BV_TYPE -> x1 style
        Not to be used externally
        """
        self.cache[rule.lhs].append(rule)

    def get_rule(self, rule, i):
        """
        This takes a lambda rule and returns its i'th bv rule
        """
        bv_type = rule._to[0]                                   # the type of the bv

        iters = 0
        for n in range(len(self.cache[bv_type]), i): 
            iters += 1
            varname = rule.bv_prefix + str(n)     # unique name for this var
            self.add(rule.make_bv_rule(self._bv_p, varname))   # make the rule
        assert iters == 1, "Since rules are added one at a time, this should only run once."
        return self.cache[bv_type][i]

    def new_state(self):
        return BVState(self, {bv_type: [] for bv_type in self.cache}



class BVState(object):
    def __init__(self, cache, initial_state):
        self.cache = cache
        self.state = initial_state

    def update(self, rule):
        if not rule.lambda_rule:
            raise Exception('how do I want to set this up')
        bv_type = rule.bv_type
        n_active = len(self.state(bv_type))
        new_rule = self.cache.get_rule(bv_type, n_active+1)       # else reuse the existing rule
        self.state(bv_type).append(new_rule)

    def __copy__(self):
        new = BVState(self.state.keys())
        new.state = copy(self.state)
        return new

    # find a unique variable name prefix for each bv type
    #bv_types = [rule._to[0] for rule in self.rules if rule._add_bv] # all bv_types

    #def first_unique_chars(bv_prefixes):
        #"""
        #for the given dict, sets the value of each key to the first character
        #in that key that is unique at its index among all the keys
        #"""
        ## assert no subsets (breaks this algo)
        #for t1 in bv_types:
            #for t2 in bv_types:
                #if not t1 == t2:
                    #assert t1 not in t2, 'types cant be substrings of each other'

        #cur = copy(bv_prefixes)
        #for i in xrange(100): # go letter by letter through the keys
            #cur = {bv_type: bv_type[i].lower() for bv_type in bv_prefixes}
            #for bv_type, prefix in cur.items():
                #if cur.values().count(prefix) == 1: # if it's unique
                    #bv_prefixes[bv_type] = cur.pop(bv_type) # keep it
            #if len(cur) == 0:
                #break

            #self._bv_prefix = {bv_type: None for bv_type in bv_types} # map from bv_type to its prefix
            #first_unique_chars(self._bv_prefix)
            #self._cached_rules = {bv_type: [] for bv_type in self._bv_prefix}
            #self.init_bv_state()

#class Context(object):
    #def __init__(self, node):
        #self.node = node
        ##self.grammar to be set later
        
    #def __enter__(self):
        #self.grammar.bv_state = self.node.bv_state

    #def __exit__(self, typ, val, tb):
        #self.grammar.init_bv_state()





    #def generate(self, rule_sampler=sample_rule, node=None):
        #print "# Calling grammar.generate", type(x), x

        # Decide what to start from based on the default if start is not specified
        #if x is None:
            #x = self.start
            #assert self.start in self._rules, \
                #"The default start symbol %s is not a defined nonterminal" % self.start

        ## Dispatch different kinds of generation
        #if isinstance(x,list):            
            ## If we get a list, just map along it to generate.
            ## We don't count lists as depth--only FunctionNodes.
            #return map(lambda xi: self.generate(xi, rule_sampler, parent), x)

        #elif self.is_nonterminal(x):

            ##print x, 'is a non terminal'

            #self._bv_rules = x._bv_rules

            ## sample a grammar rule
            #rule, prob = rule_sampler(self, x)

            #if rule.add_rule:
                #self.add_bv_rule(rule)

            ## Make a stub for this functionNode 
            #node = rule.make_FunctionNodeStub(self, prob, parent, copy(self._bv_rules)) 

            ## Define a new context that is the grammar with the rule added
            ## Then, when we exit, it's still right.
            ##with self.BVRuleContextManager(node, recurse_up=False):      # not sure why we can't use with/as:
                ## Can't recurse on None or else we genreate from self.start
            #if node._args is not None:
                ## and generate below *in* this context (e.g. with the new rules added)
                #try:
                    #node.set_args(self.generate(node._args, rule_sampler=rule_sampler, parent=node))
                #except RuntimeError as e:
                    #print "*** Runtime error in %s" % node
                    #raise e


                ## and set the parents
                ##for child in node.argFunctionNodes():
                    ##child.parent = node

            #return node

        #else:  # must be a terminal
            #assert isinstance(x, str), ("*** Terminal must be a string! x="+x)
            #return x

    #def enumerate(self, d=20, nt=None, leaves=True):
        #"""Enumerate all trees up to depth n.

        #Parameters:
            #d (int): how deep to go? (defaults to 20 -- if Infinity, enumerate() runs forever)
            #nt (str): the nonterminal type
            #leaves (bool): do we put terminals in the leaves or leave nonterminal types? This is useful in
              #PartitionMCMC

        #"""
        #for i in infrange(d):
            #for t in self.enumerate_at_depth(i, nt=nt, leaves=leaves):
                #yield t

    #def enumerate_at_depth(self, d, nt=None, leaves=True):
        #"""Generate trees at depth d, no deeper or shallower.

        #Parameters
            #d (int): the depth of trees you want to generate
            #nt (str): the type of the nonterminal you want to return (None reverts to self.start)
            #leaves (bool): do we put terminals in the leaves or leave nonterminal types? This is useful in
              #PartitionMCMC. This returns trees of depth d-1!

        #Return:
            #yields the ...

        #"""
        #if nt is None:
            #nt = self.start

        ## handle garbage that may be passed in here
        #if not self.is_nonterminal(nt):
            #yield nt
            #raise StopIteration

        #Z = log(sum([r.p for r in self._rules[nt]]))
        #if d == 0:
            #if leaves:
                ## Note: can NOT use filter here, or else it doesn't include added rules
                #for r in self._rules[nt]:
                    #if self.is_terminal_rule(r):
                        #yield r.make_FunctionNodeStub(self, (log(r.p) - Z), None)
            #else:
                ## If not leaves, we just put the nonterminal type in the leaves
                #yield nt
        #else:
            ## Note: can NOT use filter here, or else it doesn't include added rules. No sorting either!
            #for r in self._rules[nt]:

                ## No good since it won't be deep enough
                #if self.is_terminal_rule(r):
                    #continue


                #fn = r.make_FunctionNodeStub(self, (log(r.p) - Z), None)

                ## The possible depths for the i'th child
                ## Here we just ensure that nonterminals vary up to d, and otherwise
                #child_i_depths = lambda i: xrange(d) if self.is_nonterminal(fn.args[i]) else [0]

                ## The depths of each kid
                #for cd in lazyproduct(map(child_i_depths, xrange(len(fn.args))), child_i_depths):

                    ## One must be equal to d-1
                    ## TODO: can be made more efficient via permutations. Also can skip terminals in args.
                    #if max(cd) < d-1:
                        #continue
                    #assert max(cd) == d-1

                    #myiter = lazyproduct(
                        #[self.enumerate_at_depth(di, nt=a, leaves=leaves) for di, a in zip(cd, fn.args)],
                        #lambda i: self.enumerate_at_depth(cd[i], nt=fn.args[i], leaves=leaves))
                    #try:
                        #while True:
                            ## Make a copy so we don't modify anything
                            #yieldfn = copy(fn)

                            ## BVRuleContextManager here makes us remove the rule BEFORE yielding,
                            ## or else this will be incorrect. Wasteful but necessary.
                            #with BVRuleContextManager(self, fn, recurse_up=False):
                                #yieldfn.args = myiter.next()
                                #for a in yieldfn.argFunctionNodes():
                                    ## Update parents
                                    #a.parent = yieldfn

                            #yield copy(yieldfn)

                    #except StopIteration:
                        ## Catch this here so we continue in this loop over rules
                        #pass

    #def depth_to_terminal(self, x, openset=None, current_d=None):
        #"""
        #Return a dictionary that maps both this grammar's rules and its nonterminals to a number,
        #giving how quickly we can go from that nonterminal or rule to a terminal.

        #Arguments:
            #openset(doc?): stores the set of things we're currently trying to compute for. We must skip rules
              #that contain anything in there, since they have to be defined still, and so we want to avoid
              #a loop.

        #"""
        #if current_d is None: 
            #current_d = dict()
            
        #if openset is None:
            #openset = set()
            
        #openset.add(x)
        
        #if isinstance(x, GrammarRule):
            #if x.to is None or len(x.to) == 0:
                #current_d[x] = 0 # we are a terminal
            #else:
                #current_d[x] = 1 + max([(self.depth_to_terminal(a, openset=openset, current_d=current_d)
                                        #if a not in openset else 0) for a in x.to])
        #elif isinstance(x, str):
            #if x not in self._rules:
                #current_d[x] = 0    # A terminal
            #else:
                #current_d[x] = min([(self.depth_to_terminal(r, openset=openset, current_d=current_d)
                                    #if r not in openset else Infinity) for r in self._rules[x]])
        #else:
            #assert False, "Shouldn't get here!"

        #openset.remove(x)
        #return current_d[x]

    #def find(self, returntype, name, to):
        #"""
        #returns the rule that matches the given returntype, name, and to
        #where to is a list of strings
        #"""
        #for rule in self._rules[returntype]:
            #if rule.name == name and rule.to == to:
                #return rule
        #return None

