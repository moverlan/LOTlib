
class BVRuleContextManager(object):
    
    def __init__(self, fn, recurse_up=False):
        """
        This manages the state of added rules as a derivation tree is generated
        """
        self.__dict__.update(locals())
        self.added_rules = []
                
    def __str__(self):
        return "<Managing context for %s>"%str(self.fn)
    
    
    def __enter__(self):
        if self.fn is None: # skip these
            return
        
        assert len(self.added_rules) == 0 # Should not call __enter__ twice
        
        for x in self.fn.up_to(to=None) if self.recurse_up else [self.fn]:
            if x.added_rule is not None:
                #print "# Adding rule ", x.added_rule
                r = x.added_rule
                self.added_rules.append(r)
                self.grammar.add_bv_rule(r)
                        
    def __exit__(self, t, value, traceback):
        
        if self.fn is None: # skip these
            return
        
        for r in self.added_rules:
            #print "# Removing rule", r
            self.grammar.remove_bv_rule(r)
            
        # reset these
        self.added_rules = []
        
        return False #re-raise exceptions
        
    
