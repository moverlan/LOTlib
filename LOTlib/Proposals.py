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

def abstract_inline(hyp):
    root = hyp.func_tree.copy()
    rules_where = root.grammar.rules_where

    # find all apply/lambda pairs
    abstraction_rule_pairs = set()
    for apply_rule in rules_where(func_name='apply_'):
        for lambda_rule in rules_where(lhs=apply_rule.to[0]):
            abstraction_rule_pairs.add((apply_rule, lambda_rule))

    # find all types that can go to both the apply's type and the type
    # being abstracted over
    parents = defaultdict(list)
    for apply_rule, lambda_rule in abstraction_rule_pairs:
        for rule1 in rules_where(to=[apply_rule.lhs]):
            for rule2 in rules_where(lhs=rule1.lhs, to=[lambda_rule.to[0]]):
                parents[(rule1, rule2)].append((apply_rule, lambda_rule))

    candidate_nodes = defaultdict(list)
    for node in root:
        for (rule1, rule2), rule_pair_list in parents.items():
            if node.rule == rule2:
                candidate_nodes[(node)].append((rule1, rule2))

    node = random.choice(candidate_nodes.keys())
    parent_rule_1, parent_rule_2 = random.choice(candidate_nodes[node])
    apply_rule, lambda_rule = random.choice(parents[(parent_rule_1, parent_rule_2)])

    print len(candidate_nodes), len(candidate_nodes[node]), len(parents[(parent_rule_1, parent_rule_2)])
    p = 1./len(candidate_nodes) * \
        1./len(candidate_nodes[node]) * \
        1./len(parents[(parent_rule_1, parent_rule_2)])
    print p

    new_parent = rule1.make_node(node.parent)
    apply_node = apply_rule.make_node(new_parent)
    lambda_node = lambda_rule.make_node(apply_node)

    print new_parent

    return hyp

