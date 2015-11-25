# -*- coding: utf-8 -*-

import random
from math import log

def random_regen(hyp):
    #print 
    #print 'old', root.log_prob, root
    root = hyp.func_tree
    new_root = root.copy()

    #all_ids = [id(node) for node in root] + [id(node) for node in new_root]
    #unique = set()
    #for idd in all_ids:
        #assert idd not in unique
        #unique.add(idd)

    node = random.choice(list(new_root))
    #print 'node', node

    if node.is_root:
        #print 'replacing root'
        new = type(node).new(node.grammar.random)
        new_root = new
    else:
        new = node.parent.generate_child(node.child_n, node.grammar.random)
        #assert (new_root.log_prob-root.log_prob) - (new.log_prob-node.log_prob) < 10e-8
        #if new == node:
            #print 'same', new, node

        #print 'new', new

    new_hyp = hyp.copy_with(func_tree=new_root)

    #print 'new', new_root.log_prob, new_root
    #forward = new.log_prob - log(root.size)
    #backward = node.log_prob - log(new_root.size)
    #acceptance_ratio = new_hyp.posterior - hyp.posterior + backward - forward

    simplified_ar = new_hyp.likelihood - hyp.likelihood - log(new_root.size) + log(root.size)

    #assert abs(acceptance_ratio-simplified_ar)<1e-10

    return new_hyp, simplified_ar

