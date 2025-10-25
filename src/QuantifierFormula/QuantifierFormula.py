from BinaryFormula.BinaryFormula import BinaryFormula


class QuantifierFormula():
    def __init__(self, forAll = True, variable=None, formula=None):
        self.forAll = forAll
        self.variable = variable
        self.formula = formula

    def __eq__(self, other): 
        if not isinstance(other, QuantifierFormula):
            return NotImplemented

        return self.forAll == other.forAll and self.variable == other.variable and self.formula == other.formula
    
    def __ne__(self, other): 
        if not isinstance(other, QuantifierFormula):
            return NotImplemented

        return self.forAll != other.forAll or self.variable != other.variable or self.formula != other.formula

    def is_universal(self):
      return self.forAll

    def is_existential(self):
      return not self.forAll

    def toLatex(self, parentheses= False):
        if parentheses:
          if self.forAll:        
              return '(\\forall {} {})'.format(self.variable, self.formula.toLatex(parentheses=parentheses))
          else:
              return '(\\exists {} {})'.format(self.variable, self.formula.toLatex(parentheses=parentheses))
        elif not isinstance(self.formula, BinaryFormula):
          if self.forAll:        
              return '\\forall {} {}'.format(self.variable, self.formula.toLatex())
          else:
              return '\\exists {} {}'.format(self.variable, self.formula.toLatex())
        else:
          if self.forAll:        
              return '\\forall {} ({})'.format(self.variable, self.formula.toLatex())
          else:
              return '\\exists {} ({})'.format(self.variable, self.formula.toLatex())

    def toString(self, parentheses= False):
        if parentheses:
          if self.forAll:        
              return '(A{} {})'.format(self.variable, self.formula.toString(parentheses=parentheses))
          else:
              return '(E{} {})'.format(self.variable, self.formula.toString(parentheses=parentheses))
        if not isinstance(self.formula, BinaryFormula):
          if self.forAll:        
              return 'A{} {}'.format(self.variable, self.formula.toString())
          else:
              return 'E{} {}'.format(self.variable, self.formula.toString())
        else:
          if self.forAll:        
              return 'A{} ({})'.format(self.variable, self.formula.toString())
          else:
              return 'E{} ({})'.format(self.variable, self.formula.toString())

    def all_variables(self):
      result = self.formula.all_variables()
      result.add(self.variable)
      return result
      
    def bound_variables(self):
      return self.all_variables().difference(self.free_variables())

    def free_variables(self):
      result = self.formula.free_variables()
      result.discard(self.variable)
      return result 

    def is_substitutable(self, x, y):
      if (self.variable == y and x in self.formula.free_variables()):
        return False
      return self.formula.is_substitutable(x,y)

    def valid_substitution(self, formula):
      free_vars = formula.free_variables()
      if len(free_vars)==0:
         return self.formula==formula
      for v in free_vars:
        fAux = self.formula.substitution(self.variable, v)
        if (fAux==formula):
          return True
      return False

    def substitution(self, var_x, a):
      if self.variable == var_x:
        return self
      else:
        return QuantifierFormula(self.forAll,self.variable, self.formula.substitution(var_x, a))