class BinaryFormula():
    def __init__(self, key = '', left = None, right = None):
        self.key = key
        self.left = left
        self.right = right

    def __eq__(self, other): 
        if not isinstance(other, BinaryFormula):
            return NotImplemented

        return self.key == other.key and self.left == other.left and self.right == other.right

    def __ne__(self, other): 
        if not isinstance(other, BinaryFormula):
            return NotImplemented

        return self.key != other.key or self.left != other.left or self.right != other.right

    def create_string_representation(self, formula, parentheses= False):
        if(parentheses):
          return formula.toString(parentheses=parentheses)
        elif isinstance(formula, BinaryFormula):
            return'({})'.format(formula.toString())
        else:
            return formula.toString()

    def create_latex_representation(self, formula, parentheses= False):
        if(parentheses):
          return formula.toLatex(parentheses=parentheses)
        elif isinstance(formula, BinaryFormula):
            return'({})'.format(formula.toLatex())
        else:
            return formula.toLatex()

    def is_implication(self):
      return self.key=='->'
    def is_conjunction(self):
      return self.key=='&'
    def is_disjunction(self):
      return self.key=='|'

    def toLatex(self, parentheses= False):
        operators = {
            '->': '\\rightarrow ',
            '&': '\\land ',
            '|': '\\lor ',
            '<->': '\\leftrightarrow ',
        }
        string = self.create_latex_representation(self.left, parentheses=parentheses)
        string += operators[self.key]
        string += self.create_latex_representation(self.right, parentheses=parentheses)
        if parentheses:
          return '('+string+')'
        return string

    def toString(self, parentheses= False):
        string = self.create_string_representation(self.left, parentheses=parentheses)
        string += self.key
        string += self.create_string_representation(self.right, parentheses=parentheses)
        if parentheses:
          return '('+string+')'
        return string

    def all_variables(self):
      return self.left.all_variables().union(self.right.all_variables())

    def bound_variables(self):
      return self.all_variables().difference(self.free_variables())

    def free_variables(self):
      return self.left.free_variables().union(self.right.free_variables())

    def is_substitutable(self, x, y):
      return self.left.substitutable(x,y) and self.right.substitutable(x,y) 

    def substitution(self, var_x, a):
      return BinaryFormula(self.key, self.left.substitution(var_x, a), self.right.substitution(var_x, a))