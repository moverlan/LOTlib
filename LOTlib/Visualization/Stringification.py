"""
    Functions for mappings FunctionNodes to strings
"""
from LOTlib.FunctionNode import isFunctionNode, BVUseFunctionNode, BVAddFunctionNode

def schemestring(x, d=0, bv_names=None):
    """Outputs a scheme string in (lambda (x) (+ x 3)) format.

    Arguments:
        x: We return the string for this FunctionNode.
        bv_names: A dictionary from the uuids to nicer names.

    """
    if isinstance(x, str):
        return x
    elif isFunctionNode(x):

        if bv_names is None:
            bv_names = dict()

        name = x.name
        if isinstance(x, BVUseFunctionNode):
            name = bv_names.get(x.name, x.name)

        if x.args is None:
            return name
        else:
            if x.args is None:
                return name
            elif isinstance(x, BVAddFunctionNode):
                assert name is 'lambda'
                return "(%s (%s) %s)" % (name, x.added_rule.name,
                                         map(lambda a: schemestring(a, d+1, bv_names=bv_names), x.args))
            else:
                return "(%s %s)" % (name, map(lambda a: schemestring(a,d+1, bv_names=bv_names), x.args))


def fullstring(x, d=0, bv_names=None):
    """
    A string mapping function that is for equality checking. This is necessary because pystring silently ignores
    FunctionNode.names that are ''. Here, we print out everything, including returntypes
    :param x:
    :param d:
    :param bv_names:
    :return:
    """

    if isinstance(x, str):
        return x
    elif isFunctionNode(x):

        if bv_names is None:
            bv_names = dict()


        if x.name == 'lambda':
            # On a lambda, we must add the introduced bv, and then remove it again afterwards

            bvn = ''
            if isinstance(x, BVAddFunctionNode) and x.added_rule is not None:
                bvn = x.added_rule.bv_prefix+str(d)
                bv_names[x.added_rule.name] = bvn

            assert len(x.args) == 1
            ret = 'lambda<%s> %s: %s' % ( x.returntype, bvn, fullstring(x.args[0], d=d+1, bv_names=bv_names) )

            if isinstance(x, BVAddFunctionNode) and x.added_rule is not None:
                try:
                    del bv_names[x.added_rule.name]
                except KeyError:
                    x.fullprint()

            return ret
        else:

            name = x.name
            if isinstance(x, BVUseFunctionNode):
                name = bv_names.get(x.name, x.name)

            if x.args is None:
                return "%s<%s>"%(name, x.returntype)
            else:
                return "%s<%s>(%s)" % (name,
                                       x.returntype,
                                       ', '.join(map(lambda a: fullstring(a, d=d+1, bv_names=bv_names), x.args)))





def pystring(x, d=0, bv_names=None):
    """Output a string that can be evaluated by python; gives bound variables names based on their depth.

    Args:
        bv_names: A dictionary from the uuids to nicer names.

    """
    if isinstance(x, str):
        return x
    elif isFunctionNode(x):

        if bv_names is None:
            bv_names = dict()

        if x._name == "if_": # this gets translated
            assert len(x._args) == 3, "if_ requires 3 arguments!"
            # This converts from scheme (if bool s t) to python (s if bool else t)
            b = pystring(x._args[0], d=d+1, bv_names=bv_names)
            s = pystring(x._args[1], d=d+1, bv_names=bv_names)
            t = pystring(x._args[2], d=d+1, bv_names=bv_names)
            return '( %s if %s else %s )' % (s, b, t)
        elif x._name == '':
            assert len(x._args) == 1, "Null names must have exactly 1 argument"
            return pystring(x._args[0], d=d, bv_names=bv_names)
        elif x._name == ',': # comma join
            return ','.join(map(lambda a: pystring(a, d=d, bv_names=bv_names), x._args))
        elif x._name == "apply_":
            assert x._args is not None and len(x._args)==2, "Apply requires exactly 2 arguments"
            #print ">>>>", self._args
            return '( %s )( %s )' % tuple(map(lambda a: pystring(a, d=d, bv_names=bv_names), x._args))
        elif x._name == "or_sc_": # short-circuit or
            return "(%s)" % ' or '.join(map(lambda a: pystring(a, d=d, bv_names=bv_names), x._args))
        elif x._name == "and_sc_": # short-circuit and
            return "(%s)" % ' and '.join(map(lambda a: pystring(a, d=d, bv_names=bv_names), x._args))
        elif x._name == 'lambda':
            # On a lambda, we must add the introduced bv, and then remove it again afterwards

            bvn = ''
            if isinstance(x, BVAddFunctionNode) and x.added_rule is not None:
                bvn = x.added_rule._bv_prefix+str(d)
                bv_names[x.added_rule._name] = bvn

            assert len(x._args) == 1
            ret = 'lambda %s: %s' % ( bvn, pystring(x._args[0], d=d+1, bv_names=bv_names) )

            if isinstance(x, BVAddFunctionNode) and x.added_rule is not None:
                try:
                    del bv_names[x.added_rule._name]
                except KeyError:
                    x.fullprint()

            return ret
        else:

            name = x._name
            if isinstance(x, BVUseFunctionNode):
                name = bv_names.get(x._name, x._name)

            if x._args is None:
                return name
            else:
                return name+'('+', '.join(map(lambda a: pystring(a, d=d+1, bv_names=bv_names), x._args))+')'


def lambdastring(fn, d=0, bv_names=None):
    """
            A nicer printer for pure lambda calculus. This can use unicode for lambdas
    """
    if bv_names is None:
        bv_names = dict()

    if fn is None: # just pass these through -- simplifies a lot
        return None
    elif fn.name == '':
        assert len(fn.args)==1
        return lambdastring(fn.args[0])
    elif isinstance(fn, BVAddFunctionNode):
        assert len(fn.args)==1 and fn.name == 'lambda'
        if fn.added_rule is not None:
            bvn = fn.added_rule.bv_prefix+str(d)
            bv_names[fn.added_rule.name] = bvn
        return u"\u03BB%s.%s" % (bvn, lambdastring(fn.args[0], d=d+1, bv_names=bv_names)) # unicode version with lambda
        #return "L%s.%s" % (bvn, lambda_str(fn.args[0], d=d+1, bv_names=bv_names))
    elif fn.name == 'apply_':
        assert len(fn.args)==2
        if fn.args[0].name == 'lambda':
            return "((%s)(%s))" % tuple(map(lambda a: lambdastring(a, d=d+1, bv_names=bv_names), fn.args))
        else:
            return "(%s(%s))"   % tuple(map(lambda a: lambdastring(a, d=d+1, bv_names=bv_names), fn.args))
    elif isinstance(fn, BVUseFunctionNode):
        assert fn.args is None
        return bv_names[fn.name]
    else:
        assert fn.args is None
        return str(fn.name)
