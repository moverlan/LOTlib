# -*- coding: utf-8 -*-

from random import random
from math import log, exp

def metropolis_hastings(hyp, proposal_fn, samples):
    for _ in xrange(samples):
        new_hyp, proposal_ratio = proposal_fn(hyp)
        #print 'new', new
        #print 'a', exp(acceptance_ratio)
        prob_ratio = new_hyp.posterior - hyp.posterior
        acceptance_ratio = prob_ratio + proposal_ratio
        if acceptance_ratio > log(random()):
            #print 'accept'
            #if new == node:
                #print 'but they are same'
            hyp = new_hyp
        #else:
            #print 'reject'
        yield hyp
