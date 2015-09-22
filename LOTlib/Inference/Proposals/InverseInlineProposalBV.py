from LOTProposal import LOTProposal
from LOTlib.Miscellaneous import sample1, lambdaOne, dropfirst
from random import random
from math import log
from collections import defaultdict
from LOTlib.GrammarRule import *
from LOTlib.Inference.Proposals import ProposalFailedException
from LOTlib.FunctionNode import NodeSamplingException
from LOTlib.BVRuleContextManager import BVRuleContextManager

def lp_sample_equal_to(n, x, resampleProbability=lambdaOne):
    """
        What is the log probability of sampling x or something equal to it from n? 
    """
    #assert x in n, str(x)+"\t\t"+str(n)
    if not x in n:
        return float('-inf')
    
    Z = n.sample_node_normalizer(resampleProbability=resampleProbability)
    return log(sum([resampleProbability(t) if (t==x) else 0.0 for t in n])) - log(Z)

def instantiate_dict(): # because we can't pickle a lambda
    return defaultdict(list)

# variant to handle when bv type is not same as arg type
# totally breaks forward backward but idc
class InverseInlineProposalBV(LOTProposal):
    """
        Inverse inlinling proposals.
    """
    
    def __init__(self, grammar):
        """
            This takes a grammar and a regex to match variable names
        """
        self.__dict__.update(locals())
        LOTProposal.__init__(self, grammar)

        # check that we used "apply_" instead of "apply"
        for r in self.grammar:
            assert r.name is not "apply", "*** Need to use 'apply_' instead of 'apply' "
            assert r.name is not "lambda_", "*** Need to use 'lambda' instead of 'lambda' "
            # the asymmetry here is disturbing, but lambda is a keyword and apply is a function


        # Insertable rules for child type T and parent type P have the following properties:
        #   1) its an apply with type T'
        #   2) type P goes to T'
        #   3) type P goes to T
        #   4) its lambda goes to type T
        self.abstractable_rules = defaultdict(instantiate_dict) # Hash each nonterminal/parent nonterminal to (a,l) where a and l are the apply and lambda rules you need
        
        for parent_type in self.grammar.nonterminals():
            child_types = set() # set of all types that rules of parent type can go to
            for outer_rule in self.grammar.rules_where(nt=parent_type):
                if len(outer_rule.to) == 1: # only support single case
                    child_types.add(outer_rule.to[0])
            for apply_type in child_types: # all T' that P goes to (#2)
                for apply_rule in self.grammar.rules_where(nt=apply_type, name='apply_'): # apply rules of type T' (#1 and #2)
                    # get all the lambdas for this apply
                    lambda_type = apply_rule.to[0]
                    for lambda_rule in self.grammar.rules_where(nt=lambda_type, name='lambda'):
                        for child_type in child_types: # all T that P goes to (#3)
                            if lambda_rule.to[0] == child_type: # the lambda goes to T (#4)
                                self.abstractable_rules[child_type][parent_type].append((apply_rule, lambda_rule))



        #print "# Insertable rules:"
        #for T, P in self.abstractable_rules.items():
            #print T
            #for p, rules in P.items():
                #print '  ', p
                #for a, l in rules:
                    #print '    ', a, "----------", l



    def can_abstract_at(self, x):
        """
            Can I put a lambda at x?
        """
        if not x.parent:
            return False
        return len(self.abstractable_rules[x.returntype][x.parent.returntype]) > 0
    
    def is_valid_argument(self, n, x):
        """
            The only valid arguments that can be extracted contain lambdas defined above n OR below t
        """
        allowed_bvs = set()
        for t in dropfirst(n.up_to(to=None)):  # don't count n in the bvs we allow!
            if isinstance(t, BVAddFunctionNode):
                allowed_bvs.add(t.added_rule.name)
        
        for t in x:
            # we also allow bvs of things defined in t
            if isinstance(t, BVAddFunctionNode)  and t is not x:
                allowed_bvs.add(t.added_rule.name)
            elif isinstance(t, BVUseFunctionNode) and (t.name not in allowed_bvs):
                return False
        
        return True
                
                
    
    def can_inline_at(self, n):
        """
            Can we inline this? Only if its an apply whose lambda bv takes no args. ALSO, the argument must occur in the lambda, or else this could not have been created via inlining
        """

        if n.name != "apply_":
            return False

        assert len(n.args) == 2
        l, a = n.args

        assert (not isinstance(l.added_rule, BVUseFunctionNode)) or l.added_rule.bv_args is None # NOTE: l.added_rule.name checks if the bound variable is actually used, but only works for bv_args=None


        parent_rules = [rule.to[0] for rule in self.grammar.rules[n.parent.rule.nt]]

        #print 'can inline at', n, '?'
        #print parent_rules
        #print (l.rule.bv_args is None or len(l.rule.bv_args) == 0)
        ##print l.args[0].contains_function(l.added_rule.name)
        #print l.args[0].returntype in parent_rules
        #print self.is_valid_argument(l.args[0], a)
        #print self.can_abstract_at(l.args[0])

            #l.args[0].contains_function(l.added_rule.name) and \
        return (l.rule.bv_args is None or len(l.rule.bv_args) == 0) and \
            l.args[0].returntype in parent_rules and \
            self.is_valid_argument(l.args[0], a) and \
            self.can_abstract_at(l.args[0])

        
    def propose_tree(self, t):
        """
            Delete:
                - find an apply
                - take the interior of the lambdathunk and sub it in for the lambdaarg everywhere, remove the apply
            Insert:
                - Find a node
                - Find a subnode s
                - Remove all repetitions of s, create a lambda
                - and add an apply
        """
        
        newt = copy(t) 
        f,b = 0.0, 0.0
            
        # ------------------
        if random() < 0.5: # Am inverse-inlining move

            #print "# INVERSE-INLINE"

            # where the lambda goes
            try:
                n, np = newt.sample_subnode(resampleProbability=self.can_abstract_at)
            except NodeSamplingException:
                #print 'failed'
                raise ProposalFailedException

            # Pick the rule we will use
            ir = self.abstractable_rules[n.returntype][n.parent.returntype]
            ar, lr = sample1(ir) # the apply and lambda rules

            parent_rules = [rule.to[0] for rule in self.grammar.rules[n.parent.rule.nt]]
            assert ar.nt in parent_rules
            assert lr.nt == ar.to[0]
            
            def replaceable(z):
                #print z.returntype == ar.to[1]
                #print z
                #print z.returntype
                #print ar
                #print ar.to
                #print lr.bv_type
                #print
                #return z.returntype == ar.to[1] and self.is_valid_argument(n, z)
                return z.returntype == lr.bv_type and self.is_valid_argument(n, z) #how do we choose args?
            # what the argument is. Must have a returntype equal to the second apply type
            # NOPE. Must have returntype == bound variable type
            #arg_predicate = lambda z: z.returntype == ar.to[1] and self.is_valid_argument(n, z) #how do we choose args?
            try:
                #print n
                argval, _ = n.sample_subnode(resampleProbability=replaceable )
                #print 'argval', argval
            except NodeSamplingException:
                #print 'node samp ex'
                raise ProposalFailedException

            argval = copy(argval) # necessary since the argval in the tree gets overwritten
            below = copy(n) # necessary since n gets setto the new apply rule  
            
            # now make the function nodes. The generation_probabilities will be reset later, as will the parents for applyfn and bvfn
            n.setto(ar.make_FunctionNodeStub(self.grammar, 0.0, None)) # n's parent is preserved

            # set the parent node's rule to the proper one
            n.parent.rule = filter(lambda x: x.to[0] == ar.nt, self.grammar.rules[n.parent.rule.nt])[0]

            lambdafn = lr.make_FunctionNodeStub(self.grammar, 0.0, n) ## this must be n, not applyfn, since n will eventually be setto applyfn
            bvfn = lambdafn.added_rule.make_FunctionNodeStub(self.grammar, 0.0, None) # this takes the place of argval everywhere below

            below.replace_subnodes(lambda x:x==argval, bvfn) # substitute below the lambda

            lambdafn.args[0] = below

            below.parent = lambdafn
            argval.parent = n

            # build our little structure
            n.args = lambdafn, argval

            assert self.can_inline_at(n) # this had better be true

            # to go forward, you choose a node, a rule, and an argument
            f = np + (-log(len(ir))) + lp_sample_equal_to(n, argval, resampleProbability=replaceable)
            newZ = newt.sample_node_normalizer(self.can_inline_at)
            b = (log(self.can_inline_at(n)*1.0) - log(newZ))
            
        else: # An inlining move
            #print "# INLINE"
            try:
                n, np = newt.sample_subnode(resampleProbability=self.can_inline_at)
            except NodeSamplingException:
                #print 'failed'
                raise ProposalFailedException

            # Replace the subnodes 
            newn = n.args[0].args[0] # what's below the lambda
            argval = n.args[1]
            bvn = n.args[0].added_rule.name # the name of the added variable

            def replaceable(x):
                return isinstance(x,BVUseFunctionNode) and x.name == bvn and x.returntype == argval.returntype

            newn.replace_subnodes(replaceable, argval)

            n.setto(newn)            
            assert self.can_abstract_at(n) # this had better be true

            # clean up any nodes that didn't get replaced (because their type didn't match)
            # breaks forward backward but idgaf
            for subn in filter(lambda x: x.name == bvn, n.subnodes()):
                #print 'found', subn, subn.returntype
                with BVRuleContextManager(self.grammar, subn.parent, recurse_up=True):
                    subn.setto(self.grammar.generate(subn.returntype))

            # figure out which rule we are supposed to use
            #possible_rules = [r for r in self.grammar.rules[n.returntype] if r.name==n.name and tuple(r.to)[0] == tuple(n.argTypes())[0] ]
            possible_rules = [r for r in self.grammar.rules[n.returntype] if r.name==n.name and tuple(r.to)[0] == tuple(n.argTypes())[0] ] # made it only check first argtype since I have different types in arg and bv
            #if len(possible_rules) > 1:
                #print 'why does this happen?'
                #print possible_rules
            #if not len(possible_rules) == 1:
                #print len(possible_rules)
                #print n
                #print n.name
                #print n.argTypes()
                #for r in self.grammar.rules[n.returntype]:
                    #print '|', r
                    #print r.name, r.name == n.name
                    #print r.to
            assert len(possible_rules) == 1 # for now?
            n.rule = possible_rules[0]

            # set the parent node's rule to the proper one
            n.parent.rule = filter(lambda x: x.to[0] == n.rule.nt, self.grammar.rules[n.parent.rule.nt])[0]

            ir = self.abstractable_rules[n.returntype][n.parent.returntype] # for the backward probability
            f = np # just the probability of choosing this apply

            # choose n, choose a, choose the rule
            arg_predicate = lambda z: (z.returntype == argval.returntype) and self.is_valid_argument(newn, z)
            new_nZ = newt.sample_node_normalizer(self.can_abstract_at) # prob of choosing n
            argvalp = lp_sample_equal_to(newn, argval, resampleProbability=arg_predicate)
            assert len(ir)>0
            b = (log(self.can_abstract_at(newn)) - log(new_nZ)) + argvalp + (-log(len(ir)))
        
        ## and fix the generation probabilites, because otherwise they are ruined by all the mangling above
        newt.recompute_generation_probabilities(self.grammar)
        assert newt.check_parent_refs() # Can comment out -- here for debugging
        
        #print 'did we finish proposing??'
        
        return [newt, f-b]
            
            
    
if __name__ == "__main__":
        from LOTlib import lot_iter
        #from LOTlib.Examples.Magnetism.SimpleMagnetism import data, grammar,  make_h0  DOES NOT WORK FOR BV ARGS
        from LOTlib.Examples.Number.Model.Utilities import grammar, make_h0, generate_data, get_knower_pattern
        
        grammar.add_rule('LAMBDA_WORD', 'lambda', ['WORD'], 1.0, bv_type='WORD')
        grammar.add_rule('WORD', 'apply_', ['LAMBDA_WORD', 'WORD'], 1.0)
        
        p = InverseInlineProposal(grammar)
        
        """
        # Just look at some proposals
        for _ in xrange(200):    
            t = grammar.generate()
            print ">>", t
            #assert t.check_generation_probabilities(grammar)
            #assert t.check_parent_refs()
            
            for _ in xrange(10):
                t =  p.propose_tree(t)[0]
                print "\t", t
            
        """
        # Run MCMC -- more informative about f-b errors    
        from LOTlib.Inference.MetropolisHastings import MHSampler

        from LOTlib.Inference.Proposals.MixtureProposal import MixtureProposal          
        from LOTlib.Inference.Proposals.RegenerationProposal import RegenerationProposal
                
        h = make_h0(proposal_function=MixtureProposal([InverseInlineProposal(grammar), RegenerationProposal(grammar)] ))
        data = generate_data(100)
        for h in lot_iter(MHSampler(h, data)):
            print h.posterior_score, h.prior, h.likelihood, get_knower_pattern(h), h
        
            
