# -*- coding: utf-8 -*-

from random import random
from math import log, exp
from LOTlib import lot_iter as interruptible
from sys import maxint

def metropolis_hastings(hyp, proposal_fn, samples=maxint, print_every=maxint):
    count = 0
    for step in interruptible(xrange(samples)):
        new_hyp, acceptance_ratio = proposal_fn(hyp)
        if acceptance_ratio > log(random()):
            hyp = new_hyp
            count += 1
        yield hyp

