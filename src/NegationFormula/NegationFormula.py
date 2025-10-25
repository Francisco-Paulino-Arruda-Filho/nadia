from BinaryFormula.BinaryFormula import BinaryFormula


class NegationFormula():
    def __init__(self, formula = None):
        self.formula = formula

    def __eq__(self, other): 
        if not isinstance(other, NegationFormula):
            return NotImplemented

        return self.formula == other.formula

    def __ne__(self, other): 
        if not isinstance(other, NegationFormula):
            return NotImplemented

        return self.formula != other.formula

    def toLatex(self, parentheses= False):
        if(parentheses):
          return '('+'\\lnot ' + self.formula.toLatex(parentheses=parentheses)+')'
        if not isinstance(self.formula, BinaryFormula):
            string = '\\lnot ' + self.formula.toLatex()
        else:
            string = '\\lnot({})'.format(self.formula.toLatex())
        return string   

    def toString(self, parentheses= False):
        if parentheses:
            string = '(~' + self.formula.toString(parentheses=parentheses)+')'
        elif not isinstance(self.formula, BinaryFormula):
            string = '~' + self.formula.toString()
        else:
            string = '~({})'.format(self.formula.toString())
        return string 

    def all_variables(self):
      return self.formula.all_variables()

    def bound_variables(self):
      return self.all_variables().difference(self.free_variables())

    def free_variables(self):
      return self.formula.free_variables()

    def is_substitutable(self, x, y):
      return self.formula.substitutable(x,y)

    def substitution(self, var_x, a):
      return NegationFormula(self.formula.substitution(var_x, a))