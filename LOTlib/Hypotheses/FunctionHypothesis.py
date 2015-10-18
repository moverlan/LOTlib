"""
        A special type of hypothesis whose value is a function.
        The function is automatically eval-ed when we set_value, and is automatically hidden and unhidden when we pickle
        This can also be called like a function, as in fh(data)!
"""



from Hypothesis import Hypothesis

from LOTlib.Evaluation.Eval import evaluate_expression
from LOTlib.Evaluation.EvaluationException import EvaluationException
from LOTlib.Miscellaneous import lambdaNone
from copy import copy

class FunctionHypothesis(Hypothesis):
    """
            A special type of hypothesis whose value is a function.
            The function is automatically eval-ed when we set_value, and is automatically hidden and unhidden when we pickle
            This can also be called like a function, as in fh(data)!
    """

    def __init__(self, func, pyfunc):
        pass
        #"""
                #*value* - the value of this hypothesis

                #*f* - defaultly None, in which case this uses self.value2function

                #*args* - the arguments to the function
        #"""
        ##self.args = args # must come first since below calls value2function
        #Hypothesis.__init__(self, value, **kwargs) # this initializes prior and likleihood variables, so keep it here!
        #self.set_value(value,f)

    #def __str__(self):
        #"""
        #Strings of FunctionHypotheses wrap in an implicit lambda and args
        #"""
        #return 'lambda %s: %s' % (','.join(self.args), str(self.value))

    def __copy__(self):
        """ Create a copy, only deeply of f value """
        return FunctionHypothesis(func=copy(self.func), pyfunc=self.pyfunc)

    #def __call__(self, *vals):
        #"""
                #Make this callable just like a function (as in: myFunction(data)). Yay python!
        #"""
        ## The below assertions are useful but VERY slow
        ##assert not any([isinstance(x, FunctionData) for x in vals]), "*** Probably you mean to pass FunctionData.input instead of FunctionData?"
        ##assert callable(self.fvalue)

        #return self.fvalue(*vals)


    #def compile_function(self):
        #"""
        #Takes my value and returns what function I compute. Internally cached by set_value

        #NOTE: This must be overwritten by subclasses to something useful--see LOTHypothesis
     #def __copy__(self, copy_value=True):       """
        #raise NotImplementedError

    #def reset_function(self):
        #""" re-construct the function from the value -- useful after pickling """
        #self.set_value(self.value)


    #def set_value(self, value, f=None):
        #"""
                #Sets the value for the hypothesis.
                #Another option: send f if speed is necessary
        #"""

        #Hypothesis.set_value(self,value)

        #if f is not None:
            #self.fvalue = f
        #elif value is None:
            #self.fvalue = None
        #else:
            #self.fvalue = self.compile_function() # now that the value is set

    #def force_function(self, f)
        #"""
        #Sets the function to f, ignoring value.
        #:param f: - a python function (object)
        #:return:
        #"""
        #self.value = "<FORCED_FUNCTION>"
        #self.fvalue = f

    #def compute_single_likelihood(self, datum):
        #"""
                #A function that must be implemented by subclasses to compute the likelihood of a single datum/response pair.
                #This should NOT implement the temperature (that is handled by compute_likelihood)
        #"""
        #raise NotImplementedError


    ## ~~~~~~~~~
    ## Make this thing pickleable

    #def __getstate__(self):
        #""" We copy the current dict so that when we pickle, we destroy the function"""
        #dd = copy(self.__dict__)
        #dd['fvalue'] = None # clear the function out
        #return dd

    #def __setstate__(self, state):
        #"""
                #sets the state of the hypothesis (when we unpickle)
        #"""
        #self.__dict__.update(state)
        #self.set_value(self.value) # just re-set the value so that we re-compute the function
