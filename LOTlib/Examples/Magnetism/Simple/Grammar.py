from LOTlib.Miscellaneous import qq
from LOTlib.Grammar import Grammar


grammar = Grammar()

grammar.add_rule('START', '', ['Pabstraction'], 1.0) # a predicate abstraction

# lambdaUsePredicate is where you can use the predicate defined in lambdaDefinePredicate
grammar.add_rule('Pabstraction',  'apply_', ['lambdaUsePredicate', 'lambdaDefinePredicate'], 1.0, )
grammar.add_rule('lambdaUsePredicate', 'lambda', ['INNER-BOOL'],    5.0, bv_type='INNER-BOOL', bv_args=['OBJECT'], bv_prefix='F')
grammar.add_rule('lambdaUsePredicate', 'lambda', ['Pabstraction'], 1.0,  bv_type='INNER-BOOL', bv_args=['OBJECT'], bv_prefix='F')


# Define a predicate that will just check if something is in a BASE-SET
grammar.add_rule('lambdaDefinePredicate', 'lambda', ['lambdaDefinePredicateINNER'], 1.0,  bv_type='OBJECT', bv_args=None, bv_prefix='z')
# the function on objects, that allows them to be put into classes (analogous to a logical model here)
grammar.add_rule('lambdaDefinePredicateINNER', 'is_in_', ['OBJECT', 'BASE-SET'], 1.0)

# Here's how things will look with applylambda:
#grammar.add_rule('START', 'applylambda', ['INNER-BOOL'], 10.0,  bv_type='INNER-BOOL', bv_args=['OBJECT'], bv_prefix='F')
#grammar.add_rule('START', 'applylambda', ['START'],      1.0,   bv_type='INNER-BOOL', bv_args=['OBJECT'], bv_prefix='F')


grammar.add_rule('INNER-BOOL', 'is_in_', ['OBJECT', 'BASE-SET'], 10.0)


# After we've defined F, these are used to construct the concept
grammar.add_rule('INNER-BOOL', 'and_', ['INNER-BOOL', 'INNER-BOOL'], 1.0)
grammar.add_rule('INNER-BOOL', 'or_', ['INNER-BOOL', 'INNER-BOOL'], 1.0)
grammar.add_rule('INNER-BOOL', 'not_', ['INNER-BOOL'], 1.0)

grammar.add_rule('OBJECT', 'x', None, 1.0)
grammar.add_rule('OBJECT', 'y', None, 1.0)
grammar.add_rule('OBJECT', '', ['BASE-OBJECT'], 1.0) # maybe or maybe not?

# BASE-SET is here a set of BASE-OBJECTS (non-args)
grammar.add_rule('BASE-SET', 'set_add_', ['BASE-OBJECT', 'BASE-SET'], 1.0)
grammar.add_rule('BASE-SET', 'set_', [], 1.0)

grammar.add_rule('BASE-OBJECT', qq('p1'), None, 1.0)
grammar.add_rule('BASE-OBJECT', qq('p2'), None, 1.0)
grammar.add_rule('BASE-OBJECT', qq('n1'), None, 1.0)
grammar.add_rule('BASE-OBJECT', qq('n2'), None, 1.0)
