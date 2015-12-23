# -*- coding: utf-8 -*-

import random
from math import log
from collections import defaultdict

def random_regen(hyp):
    root = hyp.func_tree
    new_root = root.copy()

    node = random.choice(list(new_root))

    if node.is_root:
        new = type(node).new(node.grammar.random)
        new_root = new
    else:
        new = node.parent.generate_child(node.child_n, node.grammar.random)

    new_hyp = hyp.copy_with(func_tree=new_root)

    #forward = new.log_prob - log(root.size)
    #backward = node.log_prob - log(new_root.size)
    #acceptance_ratio = new_hyp.posterior - hyp.posterior + backward - forward

    simplified_ar = new_hyp.likelihood - hyp.likelihood - log(new_root.size) + log(root.size)

    #assert abs(acceptance_ratio-simplified_ar)<1e-10

    return new_hyp, simplified_ar

def random_regen_keeping(types):
    def propfun(hyp):
        while True:
            root = hyp.func_tree

            for node in root:
                if node.return_type in types:
                    keep = node
                    break

            while True:
                node = random.choice(list(root))
                if node.return_type not in types:
                    break

            if node.is_root:
                new_tree = root.grammar.new_tree(root.grammar.random)
            else:
                new_tree = root.copy(removing=node)
                new_tree.fill_out(new_tree.grammar.random)

            if keep.is_descendant_of(node):
                for n in new_tree:
                    if n.return_type in types:
                        remove = n
                        break
                new_keep = keep.copy(removing=[n for n in keep if n.return_type not in types])
                new_tree = new_tree.copy(removing=remove, replaced_with=new_keep)
                new_tree.fill_out(new_tree.grammar.random)

            if new_tree.size < 150:
                break
            
        new_hyp = hyp.copy_with(func_tree=new_tree)
        acceptance_ratio = new_hyp.likelihood - hyp.likelihood - log(new_tree.size) + log(root.size)
        return new_hyp, acceptance_ratio
    return propfun



#def abstract_inline(hyp):
    #root = hyp.func_tree
    #rules_where = root.grammar.rules_where

    ## find all apply/lambda pairs
    #abstraction_rule_pairs = set()
    #for apply_rule in rules_where(func_name='apply_'):
        #for lambda_rule in rules_where(lhs=apply_rule.to[0]):
            #abstraction_rule_pairs.add((apply_rule, lambda_rule))

    ## find all types that can go to both the apply's type and the type
    ## being abstracted over
    #parents = defaultdict(list)
    #for apply_rule, lambda_rule in abstraction_rule_pairs:
        #for rule1 in rules_where(to=[apply_rule.lhs]):
            #for rule2 in rules_where(lhs=rule1.lhs, to=[lambda_rule.to[0]]):
                #parents[(rule1, rule2)].append((apply_rule, lambda_rule))

    #if random.random() < 0.: # create lambda

        #candidate_nodes = defaultdict(list)
        #for node in root:
            #for (rule1, rule2), rule_pair_list in parents.items():
                #if node.rule == rule2:
                    #candidate_nodes[(node)].append((rule1, rule2))

        #node = random.choice(candidate_nodes.keys())
        #rule1, rule2 = random.choice(candidate_nodes[node])
        #apply_rule, lambda_rule = random.choice(parents[(rule1, rule2)])


        #p = -log(len(candidate_nodes)) \
            #-log(len(candidate_nodes[node])) \
            #-log(len(parents[(rule1, rule2)]))

        #new_node = rule1.make_node()
        #apply_node = apply_rule.make_node()
        #new_node.set_child(0, apply_node)
        #lambda_node = lambda_rule.make_node()
        #apply_node.set_child(0, lambda_node)
        #lambda_node.set_child(0, node.child(0).copy())

        #new_tree = root.copy(removing=node, replaced_with=new_node)

        #apply_node.generate_child(1, apply_node.grammar.random)

    #else: # remove lambda
        ##collapsable_rules = set(pair[0] for pair in parents.keys())
        #removable_nodes = {}
        #for node in root: 
            #if node.name == 'apply_':
                ## the apply/lambda rule pair
                #abstraction_pair = (node.rule, node.child(0).rule)
                #if abstraction_pair in abstraction_rule_pairs:
                    #for parent_pair in parents:
                        ## these parent rules can enclose this apply/lambda
                        #if abstraction_pair in parents[parent_pair]:
                            #rule1, rule2 = parent_pair
                            #if node.parent.rule is rule1 and rule2.to[0] == node.child(0).child(0).return_type:
                                #removable_nodes[node] = parent_pair
                                #break

        #if len(removable_nodes) > 0:
            #p = -log(len(removable_nodes))

            #apply_node = random.choice(removable_nodes.keys())
            #lambda_node = apply_node.child(0)
            #rule1, rule2 = removable_nodes[apply_node]
            #new_parent = rule2.make_node()
            #new_child = lambda_node.child(0).copy()

            #for node in new_child:
                #if node.rule is lambda_node.bv_rule:
                    #print 'found it', node
                    ##to_resample.append(node)
            ##for node in to_resample:
                ##if node in new_tree:
                    #new_tree = new_tree.copy(removing=node)
            #print new_tree
            #for node in new_tree:
                #for i, child in enumerate(node.children):
                    #if child is None:
                        #node.generate_child(i, node.grammar.random)
            ##replaced_with=node.grammar.new_node(lambda_node.bv_type, node.grammar.random))
                ##node.parent.generate_child(node.child_n, node.parent.grammar.random)

            #new_parent.set_child(0, new_child)
            #new_tree = root.copy(removing=apply_node.parent, replaced_with=new_parent)

        #else:
            #p = 0.
            #new_tree = root


    #return hyp.copy_with(func_tree=new_tree)

