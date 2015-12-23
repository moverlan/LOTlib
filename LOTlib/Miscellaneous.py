# -*- coding: utf-8 -*-

"""
Miscellaneous functions for LOTlib.

"""
# Special handling to deal with numpypy (which actually tends to be slower for LOTlib)
import collections
import math
from math import exp, log, pi
from random import random, sample
import re
import sys
import types    # For checking if something is a function: isinstance(f, types.FunctionType)
try: import numpy as np
except ImportError: import numpypy as np

# Some useful constants
Infinity = float("inf")
inf = Infinity
Inf = Infinity
Null = []
TAU = 6.28318530718     # fuck pi

# For R-friendly
T = True
F = False


# ------------------------------------------------------------------------------------------------------------

class CachedProperty(object):
    """
    decorator to cache results of a methods that are used as read-only properties
    useful for expensive properties of immutable objects
    """
    def __init__(self, fn, cachevar='_cache'):
        self.fn = fn
        self.cachevar = cachevar
        self.name = fn.__name__

    def __get__(self, obj, objtype=None):
        cache = getattr(obj, self.cachevar)
        if self.name not in cache:
            cache.store(self.name, self.fn(obj))
        return cache.get(self.name)

    #def stored(self, obj):
        #return cache[self.name]

    #def store(self, obj, value):
        #getattr(obj, self.cachevar)[self.name] = value

class Cache(object):
    """
    Cache to put in objects that use the decorator. Pass the name of this
    object to the decorator
    """
    def __init__(self):
        self._cache = {}

    def __contains__(self, name):
        return name in self._cache

    def get(self, name):
        if name not in self._cache:
            self._cache[name] = None
        return self._cache[name]

    def store(self, name, value):
        self._cache[name] = value

    def clear(self, obj):
        self._cache = {}


    
def first(x):
    return x[0]
def second(x):
    return x[1]
def third(x):
    return x[2]
def fourth(x):
    return x[3]
def fifth(x):
    return x[4]
def sixth(x):
    return x[5]
def seventh(x):
    return x[6]
def eighth(x):
    return x[7]


def dropfirst(g):
    """Yield all but the first in a generator."""
    keep = False
    for x in g:
        if keep: yield x
        keep = True        


def None2Empty(x):
    # Treat Nones as empty
    return [] if x is None else x


def make_mutable(x):
    # TODO: update with other types
    if isinstance(x, frozenset):
        return set(x)
    elif isinstance(x, tuple):
        return list(x)
    else: 
        raise NotImplementedError


def make_immutable(x):
    # TODO: update with other types
    if isinstance(x, set ):
        return frozenset(x)
    elif isinstance(x, list):
        return tuple(x)
    else:
        raise NotImplementedError


def unlist_singleton(x):
    """Remove any sequences of nested lists with one element.

    Example:
        [[[1,3,4]]] -> [1,3,4]

    """
    if isinstance(x,list) and len(x) == 1:
        return unlist_singleton(x[0])
    else:
        return x


def list2sexpstr(lst):
    """Prints a python list-of-lists as an s-expression.

    [['K', 'K'], [['S', 'K'], ['I', 'I']]] --> ((K K) ((S K)(I I)))

    """
    s = re.sub(r'[\'\",]', r'', str(lst))
    s = re.sub(r'\[', '(', s) # changed r'(' to '('
    s = re.sub(r'\]', ')', s) # changed r')' to ')'
    return s


# ------------------------------------------------------------------------------------------------------------
# Display functions
# ------------------------------------------------------------------------------------------------------------

def q(x, quote='\''):
    """Quotes a string."""
    if isinstance(x,str) or isinstance(x, unicode):
        return quote+x+quote
    else:
        return quote+str(x)+quote


def qq(x):
    return q(x,quote="\"")


def display(x):
    print x


# for functional programming, print something and return it
def printr(x):
    print x
    return x


def r2(x):
    return round(x,2)
def r3(x):
    return round(x,3)
def r4(x):
    return round(x,4)
def r5(x):
    return round(x,5)


def tf201(x):
    if x:
        return 1
    else:
        return 0


# Functions for I/O
def display_option_summary(obj):
    """Prints out a friendly format of all options -- for headers of output files.

    This takes in an OptionParser object as an argument. As in, (options, args) = parser.parse_args()

    """
    from time import strftime, time, localtime
    import os

    print "#"*90
    try: print "# Username: ", os.getlogin()
    except OSError: pass

    try: print "# Date: ", strftime("%Y %b %d (%a) %H:%M:%S", localtime(time()) )
    except OSError: pass

    try: print "# Uname: ", os.uname()
    except OSError: pass

    try: print "# Pid: ", os.getpid()
    except OSError: pass

    for slot in dir(obj):
        attr = getattr(obj, slot)
        if not isinstance(attr, (types.BuiltinFunctionType, types.FunctionType, types.MethodType)) \
           and (slot is not "__doc__") and (slot is not "__module__"):
            print "#", slot, "=", attr
    print "#"*90


# ------------------------------------------------------------------------------------------------------------
# Genuine Miscellany
# ------------------------------------------------------------------------------------------------------------

def infrange(n=Infinity):
    """
    yields 0, 1, 2, 3, ...
    """
    i = 0
    while i<n:
        yield i
        i += 1

def takeN(g, n):
    for i, v in enumerate(g):
        if i >= n:
            break
        yield v

# a wrapper so we can call this in the below weirdo composition
def raise_exception(e):
    raise e


def ifelse(x,y,z):
    if x: return y
    else: return z


def unique(gen):
    """Make a generator unique, returning each element only once."""
    s = set()
    for gi in gen:
        if gi not in s:
            yield gi
            s.add(gi)

def UniquifyFunction(gen):
        """A decorator to make a function only return unique values."""
        def f(*args, **kwargs):
                for x in unique(gen(*args, **kwargs)):
                        yield x
        return f

def flatten(expr):
    """
            Flatten lists of lists, via stackoverflow
    """
    def flatten_(expr):
        #print 'expr =', expr
        if expr is None or not isinstance(expr, collections.Iterable) or isinstance(expr, str):
            yield expr
        else:
            for node in expr:
                #print node, type(node)
                if (node is not None) and isinstance(node, collections.Iterable) and (not isinstance(node, str)):
                    #print 'recursing on', node
                    for sub_expr in flatten_(node):
                        yield sub_expr
                else:
                    #print 'yielding', node
                    yield node

    return tuple([x for x in flatten_(expr)])

def flatten2str(expr, sep=' '):
    try:
        if expr is None: return ''
        else:            return sep.join(flatten(expr))
    except TypeError:
        print "Error in flatter2str:", expr
        raise TypeError

def weave(*iterables):
    """
    Intersperse several iterables, until all are exhausted.
    This nicely will weave together multiple chains

    from: http://www.ibm.com/developerworks/linux/library/l-cpyiter/index.html
    """

    iterables = map(iter, iterables)
    while iterables:
        for i, it in enumerate(iterables):
            try: yield it.next()
            except StopIteration: del iterables[i]




def lazyproduct(iterators, restart_ith):
        """
            Compute a product of the iterators, without holding all of their values in memory.
            This requires a function restart_ith that returns a new (refreshed or restarted) version of the
            i'th iterator so we can start it anew

            for g in lazyproduct( [xrange(10), xrange(10)], lambda i: xrange(10)):
            	print g

        """

        iterators = map(iter, iterators)

        # initialize the state
        state = [it.next() for it in iterators]

        yield state

        while True:

            for idx in xrange(len(iterators)): # the "carry" loop
                try:
                    state[idx] = iterators[idx].next()
                    break # break the idx loop (which would process "carries")
                except StopIteration:

                    if idx == len(iterators)-1:
                        raise StopIteration # actually exit
                    else:
                        # restart the current one and increment the next
                        # by NOT breaking here
                        iterators[idx] = iter(restart_ith(idx))
                        state[idx] = iterators[idx].next() # reset this state (the next idx is increment on the next loop)

                        # and no break so we iterate the next
            yield state

# ------------------------------------------------------------------------------------------------------------
# Math functions
# ------------------------------------------------------------------------------------------------------------

# Special handilng for numpypy that doesn't use gammaln, assertion error otherwise
try:
    from scipy.special import gammaln
except ImportError:
    # Die if we try to use this in numpypy
    def gammaln(*args, **kwargs): assert False


try:
    from scipy.misc import logsumexp as logsumexp_base
except ImportError:
    try:
        from scipy.maxentropy import logsumexp as logsumexp_base
    except ImportError:
        # fine, our own version, no numpy
        def logsumexp_base(v):
            m = max(v)
            return m+log(sum(map( lambda x: exp(x-m), v)))

def logsumexp(v):
    """
            logsumexp - our own version wraps the version defined about (logsumexp_base)
            to avoid logsumexp([-inf, -inf, -inf...]) warnings
    """
    if len(v) == 0:
        return -Infinity
    elif max(v) > -Infinity:
        return logsumexp_base(v)
    else:
        return -Infinity

def lognormalize(v):
    return v - logsumexp(v)

def logplusexp(a, b):
    """
            Two argument version. No cast to numpy, so faster
    """
    m = max(a,b)
    return m+log(exp(a-m)+exp(b-m))

def beta(a):
    """ Here a is a vector (of ints or floats) and this computes the Beta normalizing function,"""
    return np.sum(gammaln(np.array(a, dtype=float))) - gammaln(float(sum(a)))


def normlogpdf(x, mu, sigma):
    """ The log pdf of a normal distribution """
    #print x, mu
    return math.log(math.sqrt(2. * pi) * sigma) - ((x - mu) * (x - mu)) / (2.0 * sigma * sigma)

def norm_lpdf_multivariate(x, mu, sigma):
    # Via http://stackoverflow.com/questions/11615664/multivariate-normal-density-in-python
    size = len(x)

    # some checks:
    if size != len(mu) or (size, size) != sigma.shape: raise NameError("The dimensions of the input don't match")
    det = np.linalg.det(sigma)
    if det == 0: raise NameError("The covariance matrix can't be singular")

    norm_const = - size*log(2.0*pi)/2.0 - log(det)/2.0
    #norm_const = 1.0/ ( math.pow((2*pi),float(size)/2) * math.pow(det,1.0/2) )
    x_mu = np.matrix(x - mu)
    inv = np.linalg.inv(sigma)
    result = -0.5 * (x_mu * inv * x_mu.T)
    return norm_const + result


def logrange(mn, mx, steps):
    """
            Logarithmically-spaced steps from mn to mx, with steps number inbetween
            mn - min value
            mx - max value
            steps - number of steps between. When 1, only mx is returned
    """
    mn = np.log(mn)
    mx = np.log(mx)
    r = np.arange(mn, mx-1e-5, (mx-mn)/(steps-1)) # 1e-5 for numerical precision; otherwise we may add an extra
    r = np.append(r, mx)
    return np.exp(r)


def geometric_ldensity(n,p):
    """ Log density of a geomtric distribution """
    return (n-1)*log(1.0-p)+log(p)

from math import expm1, log1p

def log1mexp(a):
    """
            Computes log(1-exp(a)) according to Machler, "Accurately computing ..."
            Note: a should be a large negative value!
    """
    if a > 0:
        print >>sys.stderr, "# Warning, log1mexp with a=", a, " > 0"
    
    if a < -log(2.0): return log1p(-exp(a))
    else:             return log(-expm1(a))


def EV(fn, *args):
    """
        Estimates (via sampling) the expected value of a function that returns
        a numerical value. Pass any args to specified function as additional args
        ex: EV(random.randint, 2, 5)
    """
    vals = [fn(*args) for _ in range(100)]
    return np.average(vals)

# ------------------------------------------------------------------------------------------------------------
# Sampling functions
# ------------------------------------------------------------------------------------------------------------

def sample1(*args):
    return sample_one(*args)


def sample_one(*args):
    if len(args) == 1:
        return sample(args[0], 1)[0]     # use the list you were given
        return sample(args[0], 1)[0]     # use the list you were given
    else:
        return sample(args, 1)[0]       # treat the arguments as a list


def flip(p):
    return random() < p


# TODO: THIS FUNCTION SUCKS PLEASE FIX IT
# TODO: Change this so that if N is large enough, you sort
def weighted_sample(objs, N=1, probs=None, log=False, return_probability=False, returnlist=False, Z=None):
    """When we return_probability, it is *always* a log probability.

    Takes unnormalized probabilities and returns a list of the log probability and the object returnlist
    makes the return always a list (even if N=1); otherwise it is a list for N>1 only

    Note:
        This now can take probs as a function, which is then mapped!

    """
    # Check how probabilities are specified either as an argument, or attribute of objs (either probability
    #  or log prob).  Note: This ALWAYS returns a log probability
    if len(objs) == 0: return None

    # Convert to support indexing if we need it
    if isinstance(objs, set):
        objs = list(objs)

    myprobs = None
    if probs is None:   # Defaultly, we use .lp
        myprobs = [1.0] * len(objs)     # Sample uniform
    elif isinstance(probs, types.FunctionType):     # Note: this does not work for class instance methods
        myprobs = map(probs, objs)
    else:
        myprobs = map(float, probs)

    # Now normalize and run
    if Z is None:
        if log: Z = logsumexp(myprobs)
        else: Z = sum(myprobs)
    #print log, myprobs, Z
    out = []

    for n in range(N):
        r = random()
        for i in range(len(objs)):
            # Set r based on log domain  or  probability domain.
            r = r - exp(myprobs[i] - Z) if log else r - (myprobs[i]/Z)

            # print r, myprobs
            if r <= 0:
                if return_probability:
                    lp = 0
                    if log:
                        lp = myprobs[i] - Z
                    else:
                        lp = math.log(myprobs[i]) - math.log(Z)

                    out.append([objs[i],lp])
                    break
                else:
                    out.append(objs[i])
                    break

    if N == 1 and (not returnlist):
        return out[0]   # Don't give back a list if you just want one.
    else:
        return out

# ------------------------------------------------------------------------------------------------------------
# Lambda calculus
# ------------------------------------------------------------------------------------------------------------

# Some innate lambdas
def lambdaZero(*x): return 0
def lambdaOne(*x): return 1
def lambdaNull(*x): return []
def lambdaNone(*x): return None
def lambdaTrue(*x): return True
def lambdaFalse(*x): return False
def lambdaNAN(*x): return float("nan")

# ------------------------------------------------------------------------------------------------------------
# Sorting utilities
# ------------------------------------------------------------------------------------------------------------

def scramble_sort(lst, keyfunction):
    """This is a sort that randomizes order among the ones with equal keys.

    Steve says: 'I have no idea why this is here.'

    """
    keys = map(lambda li: (keyfunction(li), random(), li), lst)
    
    return map(lambda x: x[2], sorted(keys))


