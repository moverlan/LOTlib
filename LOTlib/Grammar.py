# *- coding: utf-8 -*-

import numpy as np
import math
#from LOTlib.Miscellaneous import cached
from collections import defaultdict
from copy import copy
from LOTlib.TerminalNode import TerminalNode

class Grammar:
    """
    oyea
    """
    def __init__(self, rules, bv_p=1.0, start='START'):
        self._bv_p = bv_p
        self._start_symbol = start
        # TODO get params from rules
        self._params = {} # params for production probs. dict from name to (lhs, rule_index) pair
        self._static_rules = defaultdict(list) # maps nonterm to list of rules
        self._bv_rules = defaultdict(list)

        for rule in rules:
            self._static_rules[rule.lhs].append(rule)
            #if rule.primitive.name() == 'lambda_':
                #print 'adding bv type', rule.primitive.bv_type
                #self._bv_rules[rule.primitive.bv_type] = []
            #else:
                #print rule.primitive.name()


    @property
    def bv_p(self):
        return self._bv_p

    def __str__(self):
        return '\n'.join(self.rules)

    @property
    def rules(self):
        """
        returns dict with union of static and bv rules
        """
        rules = copy(self._static_rules)
        for lhs, bv_rules in self._bv_rules.iteritems():
            if bv_rules: # not empty
                rules[lhs] = copy(rules[lhs])
                rules[lhs].extend(bv_rules)
        return rules

    @property
    def all_rules(self):
        """
        iterates over all rules
        """
        for rule_list in self.rules.values():
            for rule in rule_list:
                yield rule

    #@property
    #def bvs(self):
        #bvs = set()
        #for bv_rules in self._bv_rules.values():
            #for rule in bv_rules:
                #bvs.add(rule.to[0])
        #return bvs
    
    @property
    def bv_rules(self):
        return self._bv_rules

    #@property
    #def n_rules(self):
        #return len(self.rules)

    @property
    def start_symbol(self):
        return self._start_symbol

    #@property
    #def start_rules(self):
        #return self.rules_where(lhs=self.start)

    @property
    def nonterminals(self):
        return self.rules.keys()

    @property
    def terminals(self):
        terminals = set()
        for rule in rules:
            for token in rule.to:
                if token not in self.nonterminals:
                    terminals.add(token)
        return terminals

    #@contextmanager
    #def context(self, node):
        #"""
        #Sets grammar to represent the state of the rules in the context of a particular node
        #"""
        #self._rule_state = node.rule_state
        #yield
        #self._rule_state = self._rules

    def copy_with(self, rule):
        """
        returns a copy of self with the given bv_rule added
        """
        # copy all and only the things that will be mutated
        new = copy(self) # self
        new._bv_rules = copy(new._bv_rules) # the bv rule dict
        new._bv_rules[rule.lhs] = copy(new._bv_rules[rule.lhs]) # the list of rules of this type
        new._bv_rules[rule.lhs].append(rule)
        #new.clear_cache()
        return new

    def get_rule(self, lhs, index):
        """
        returns the index'th rule with the given lhs
        """
        return self.rules[lhs][index]

    # iterates all rules that match the given criteria
    def rules_where(self, lhs=None, func_name=None, to=None):
        if lhs is None:
            lhss = self.nonterminals
        else:
            lhss = [lhs]
        for lhs in lhss:
            for rule in self.rules[lhs]:
                if func_name is not None and not rule.func_name == func_name:
                    continue
                if to is not None and not rule.to == to:
                    continue
                yield rule

    def probs(self, lhs, normalized=True):
        probs = np.array([rule.p for rule in self.rules_where(lhs=lhs)])
        if normalized:
            return probs / np.sum(probs)
        else:
            return probs

    def Z(self, lhs):
        return np.sum(self.probs(lhs, normalized=False))

    def gen_prob(self, rule):
        return math.log(rule.p / self.Z(rule.lhs))

    #def generate(self, chooser):
        #if chooser is None:
            #chooser = self.random

        #if node is None:
            #rule = chooser(lhs=self.start_symbol, node=None)
            #node = rule.make_node(parent_node=None)
            #node.set_grammar(self)

        #for i, typ in enumerate(node.child_types):
            #if typ in self.nonterminals:
                #rule = chooser(lhs=typ, node=node)
                #new_node = rule.make_node(parent_node=node)
                #node.set_child(i, new_node)
                #self.generate(chooser, new_node)
            #else:
                #node.set_child(i, TerminalNode(parent=node, string=typ))

        #return node

    def new_tree(self, chooser):
        """
        Returns a new tree using the given rule choosing function
        """
        rule = chooser(self.start_symbol, None)
        root = rule.make_root(grammar=self)
        root.generate_children(chooser)
        return root


    ####
    # Functions to choose a rule
    ####

    # wraps a function that returns an index so that it returns a rule
    def chooser(index_chooser):
        def rule_chooser(self, lhs, node=None):
            index = index_chooser(self, lhs, node)
            return self.get_rule(lhs, index)
        rule_chooser.__name__ = index_chooser.__name__
        return rule_chooser

    @chooser
    def random(self, lhs, node=None):
        rules = list(self.rules_where(lhs=lhs))
        #if len(rules) == 0:
            #from ipdb import set_trace as BP
            #BP()
        assert len(rules) > 0, 'no rules for lhs {0}'.format(lhs)
        return np.random.choice(range(len(rules)), p=self.probs(lhs))

    @chooser
    def manual_input(self, lhs, node):
        print node.root
        rules = self.rules_where(lhs=lhs)
        for i, rule in enumerate(rules):
            print '[' + str(i+1) + '] ' + rule
        while True:
            selection = int(raw_input())-1
            if selection in range(1, len(rules)):
                return selection
            else:
                print 'nope'

    def from_list(self, rule_indexes):
        @chooser
        def frm_list(self, lhs, node):
            for i in rule_indexes:
                yield i
        return frm_list

    #@chooser
    #def enumerate(self, lhs=None, node=None):



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
                #if r.name is not ''
                    #sofar.insert(at+1, r._name)
            #else:
                #sofar.insert(at+1, r._name)
            #sofar.pop(at)

            #return (r, gp)
        #return pick_rule


    #def first_unique_chars(strings):
        #"""
        #returns a list that for each string, gives 
        #the first character in that string that is unique at its index
        #among all the strings

        #"""
        ## assert no subsets (breaks this algo)
        #for s1 in strings:
            #for s2 in strings:
                #if not s1 == s2:
                    #assert s1 not in s2, 'types cant be substrings of each other'

        #cur = [None for _ in strings]
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






    # find a unique variable name prefix for each bv type
    #bv_types = [rule._to[0] for rule in self.rules if rule._add_bv] # all bv_types


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

        #yield node
        #for child in node.children:
            #for gchild in self.iter(child):
                #yield gchild

    #def enumerate_unset_children(self, node):
        ##print node._rule.lhs, '->'
        #for i, arg in enumerate(node.args):
            ##print ' ', arg
            #if self.is_nonterminal(arg):
                ##print 'yielding it'
                #yield i, arg
            ##else:
                ##print self._bv_rules
