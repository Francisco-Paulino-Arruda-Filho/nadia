class AtomFormula():
    def __init__(self, key = None):
        self.key = key

    def __eq__(self, other): 
        if not isinstance(other, AtomFormula):
            return NotImplemented

        return self.key == other.key
    
    def __ne__(self, other): 
        if not isinstance(other, AtomFormula):
            return NotImplemented

        return self.key != other.key

    def toLatex(self, parentheses= False):
        if(self.key != '@'):
            return self.key  
        else:
            return '\\bot' 

    def toString(self, parentheses= False):
        return self.key  

    def all_variables(self):
      return set()

    def bound_variables(self):
      return set()

    def free_variables(self):
      return set()

    def is_substitutable(self, x, y):
      return True 

    def substitution(self, var_x, a):
      return AtomFormula(self.key)