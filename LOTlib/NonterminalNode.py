


    #class RuleCache(object):
        #def __init__(self):
            #self.cache = defaultdict(list)

        #def _add(self, rule):
            #self.cache[rule.lhs].append(rule)

        #def get_rule(self, rule, i):
            #"""
            #Takes a lambda rule and returns its i'th bv rule
            #"""
            ## populate cache with however many rules are needed to have i of them (should only ever iterate once at a time)
            #for n in range(len(self.cache[rule.bv_type]), i): 
                #varname = rule.bv_prefix + str(n)     # unique name for this var
                #self._add(rule.make_bv_rule(self._bv_p, varname))   # make the rule
            #return self.cache[rule.bv_type][i]

        #def new_state(self):
            #return BVState(self)
