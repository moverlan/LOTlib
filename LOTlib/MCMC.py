# -*- coding: utf-8 -*-

from random import random
from math import log, exp

def metropolis_hastings(hyp, proposal_fn, samples):
    count = 0
    for _ in xrange(samples):
        new_hyp, acceptance_ratio = proposal_fn(hyp)
        #print 'old', hyp
        #print 'new', new_hyp
        #print 'proposal ratio', proposal_ratio
        #print 'new posterior', new_hyp.posterior
        #print 'old posterior', hyp.posterior
        #print 'prob ratio', prob_ratio
        #print 'acceptance ratio', acceptance_ratio
        if acceptance_ratio > log(random()):
            #print 'accept'
            #if new == node:
                #print 'but they are same'
            hyp = new_hyp
            count += 1
        #else:
            #print 'reject'

        #raw_input()
        yield hyp
    print count, samples, float(count)/samples
