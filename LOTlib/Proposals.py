# -*- coding: utf-8 -*-

import random
from math import log

def random_regen(hyp):
    #print 
    #print 'old', root.log_prob, root
    root = hyp.func_tree
    new_root = root.copy()
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

    #print 'new', new_root.log_prob, new_root
    forward = new.log_prob - log(1./root.size)
    backward = root.log_prob - log(1./new_root.size)
    
    return hyp.copy_with(func_tree=new_root), backward-forward

