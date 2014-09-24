from Primitives import LOTlib_primitive

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Lambda calculus & Scheme
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@LOTlib_primitive
def apply_(f,*args):
    return f(*args)

@LOTlib_primitive
def cons_(x,y):
    return [x,y]

@LOTlib_primitive
def cdr_(x):
    try:    return x[1:]
    except IndexError: return []

rest_  = cdr_

@LOTlib_primitive
def car_(x):
    try:    return x[0]
    except IndexError: return []

first_ = car_

## TODO: Add transitive closure of an operation
@LOTlib_primitive
def filter_(f,x):
    return filter(f,x)
