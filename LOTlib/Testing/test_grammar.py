from LOTlib.GrammarRule import GrammarRule
from LOTlib.Grammar import Grammar
from testtools import TestCase

from ipdb import set_trace as BP

basic = Grammar( \
    [
        GrammarRule('S', 'concat', ['a', 'S', 'b']),
        GrammarRule('S', 'concat', ['a', 'b']),
    ],
    start='S')

iters = 10

class test_grammar(TestCase):

    def test_basic_generation(self):
        for _ in xrange(iters):
            h = basic.generate()
            out = list(str(h))
            self.assertEqual(len(out) % 2, 0)
            self.assertEqual(out.count('a'), out.count('b'))
