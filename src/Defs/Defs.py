from BinaryFormula.BinaryFormula import BinaryFormula
from models.constants import constants



class PremisseDef():
    def __init__(self,line, formula):
        self.line = line
        self.formula = formula
        self.is_copied = False

    def evaluation(self,parser,deduction_result):
        return

    def toLatex(self, symbol_table):
        latex = '{'+self.formula.toLatex()+'}'
        return latex

class HypothesisDef():
    def __init__(self,line, formula):
        self.line = line
        self.formula = formula
        self.copied = None
        self.is_copied = False

    def evaluation(self,parser,deduction_result):
        return

    def toLatex(self, symbol_table):
        line = self.copied if self.copied else self.line
        if line not in hypothesis:
            hypothesis[line] = str(len(hypothesis) + 1)
        latex = '\\big['+self.formula.toLatex()+'\\big]^{_{'+hypothesis[line]+'}}'
        return latex

class HypothesisFirstOrderDef():
    def __init__(self,line, var, formula):
        self.line = line
        self.formula = formula
        self.variable = var
        self.copied = None
        self.is_copied = False

    def evaluation(self,parser,deduction_result):
      return

    def toLatex(self, symbol_table):
        line = self.copied if self.copied else self.line
        if line not in hypothesis:
            hypothesis[line] = str(len(hypothesis) + 1)
        latex = '\\big['+self.formula.toLatex()+'\\big]^{_{'+hypothesis[line]+'}}'
        return latex

class ImplicationEliminationDef():
    def __init__(self,line, formula, reference1, reference2):
        self.line = line
        self.formula = formula
        self.reference1 = reference1
        self.reference2 = reference2
        self.is_copied = False

    def evaluation(self,parser,deduction_result):
      # If the references lines occur before the rule line 
      before = parser.check_line_reference_before_rule_error(deduction_result,self)
      # If the reference1 line  and the refernce2 occur in the scope of the rule line 
      if before:
        parser.check_line_scope_reference_error(deduction_result,self, reference1=True, reference2=True)      

      formula_reference = parser.symbol_table.find_token(self.line)
      formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
      formula2 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference2.value)
      if(formula1 is None or formula2 is None or formula_reference is None):
        return

      if(BinaryFormula(key='->', left = formula1, right=self.formula) != formula2
      and BinaryFormula(key='->', left = formula2, right=self.formula) != formula1):
          deduction_result.add_error(parser.get_error(constants.INVALID_RESULT, self.reference1, self))

    def toLatex(self, symbol_table):
        latex = '\\infer[\\!\\!{\\rightarrow\\text{e}}]{'+self.formula.toLatex()+'}{{'+symbol_table.get_rule(self.reference1.value).toLatex(symbol_table)+'}&{'+symbol_table.get_rule(self.reference2.value).toLatex(symbol_table)+'}}'
        return latex

class ImplicationIntroductionDef():
    def __init__(self,line, formula, reference1, reference2):
        self.line = line
        self.formula = formula
        self.reference1 = reference1
        self.reference2 = reference2
        self.is_copied = False

    def evaluation(self,parser,deduction_result):
      # If the references lines occur before the rule line 
      parser.check_line_reference_before_rule_error(deduction_result,self)

      formula_reference = parser.symbol_table.find_token(self.line)
      formula1, formula2 = parser.symbol_table.check_scope_delimiter(self.reference1.value, self.reference2.value)
      if(formula1 is None or formula2 is None or formula_reference is None):
        return

      # If the formula is not an implicaton formula
      if(not isinstance(self.formula, BinaryFormula) or (isinstance(self.formula, BinaryFormula) and not self.formula.is_implication())):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_RESULT, formula_reference, self))
      else:
          # If the hypothese (reference1) is the left formula of the conclusion
          if(self.formula.left != formula1):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_HYPOTHESIS, self.reference1, self))
          # If the conclusion of the box (reference2) is the right formula of the conclusion
          if(self.formula.right != formula2):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_BOX_RESULT, self.reference2, self))


    def toLatex(self, symbol_table):
        hypothesis_number = str(len(hypothesis) + 1)
        hypothesis[self.reference1.value] = hypothesis_number
        latex = '\\infer[\\!\\!{\\rightarrow\\text{i}^{_'+ hypothesis_number +'}}]{'+self.formula.toLatex()+'}{'+symbol_table.get_rule(self.reference2.value).toLatex(symbol_table)+'}'
        return latex

class DisjunctionIntroductionDef():
    def __init__(self, line, formula, reference1):
        self.line = line
        self.formula = formula
        self.reference1 = reference1
        self.is_copied = False

    def evaluation(self,parser,deduction_result):
      # If the references lines occur before the rule line 
      before = parser.check_line_reference_before_rule_error(deduction_result,self)
      # If the reference1 line occurs in the scope of the rule line 
      if before:
        parser.check_line_scope_reference_error(deduction_result,self, reference1=True)      

      formula_reference = parser.symbol_table.find_token(self.line)
      formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
      if(formula1 is None):
        return

      # If the formula (reference 1) is not a disjunction formula
      if(not isinstance(self.formula, BinaryFormula) or (isinstance(self.formula, BinaryFormula) and not self.formula.is_disjunction())):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.IS_NOT_DISJUNCTION, formula_reference, self))
      else:
          # If the left formula of conclusion (the conjunction) is one of the references 
          if(not (self.formula.left == formula1 or self.formula.right == formula1)):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_LEFT_OR_RIGHT_DISJUNCTION, self.reference1, self))

    def toLatex(self, symbol_table):
        latex = '\\infer[\\!\\!{\\lor\\text{i}}]{'+self.formula.toLatex()+'}{'+symbol_table.get_rule(self.reference1.value).toLatex(symbol_table)+'}'
        return latex
        
class AndIntroductionDef():
    def __init__(self,line, formula, reference1, reference2):
        self.line = line
        self.formula = formula
        self.reference1 = reference1
        self.reference2 = reference2
        self.is_copied = False

    def evaluation(self,parser,deduction_result):
      # If the references lines occur before the rule line 
      before = parser.check_line_reference_before_rule_error(deduction_result,self)
      # If the reference1 and referece2 line occur in the scope of the rule line 
      if before:
        parser.check_line_scope_reference_error(deduction_result,self, reference1=True, reference2=True)      

      formula_reference = parser.symbol_table.find_token(self.line)
      formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
      formula2 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference2.value)
      if(formula1 is None or formula2 is None or formula_reference is None):
        return

      # If the formula (reference 1) is not a conjunction formula
      if(not isinstance(self.formula, BinaryFormula) or (isinstance(self.formula, BinaryFormula) and not self.formula.is_conjunction())):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.IS_NOT_CONJUNCTION, self.reference1, self))
      else:
          # If the left formula of conclusion (the conjunction) is one of the references 
          if(not (self.formula.left == formula1 or self.formula.left == formula2)):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_LEFT_CONJUNCTION, formula_reference, self))
          # If the right formula of conclusion (the conjunction) is one of the references 
          if(not (self.formula.right == formula1 or self.formula.right == formula2)):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_RIGHT_CONJUNCTION, formula_reference, self))

    def toLatex(self, symbol_table):
        latex = '\\infer[\\!\\!{\\land\\text{i}}]{'+self.formula.toLatex()+'}{{'+symbol_table.get_rule(self.reference1.value).toLatex(symbol_table)+'}&{'+symbol_table.get_rule(self.reference2.value).toLatex(symbol_table)+'}}'
        return latex

class AndEliminationDef():
    def __init__(self, line, formula, reference1):
        self.line = line
        self.formula = formula
        self.reference1 = reference1
        self.is_copied = False

    def evaluation(self,parser,deduction_result):
      # If the references lines occur before the rule line 
      before = parser.check_line_reference_before_rule_error(deduction_result,self)
      # If the reference1 line occurs in the scope of the rule line 
      if before:
        parser.check_line_scope_reference_error(deduction_result,self, reference1=True)      

      formula_reference = parser.symbol_table.find_token(self.line)
      formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
      if(formula1 is None):
        return

      # If the formula (reference 1) is not a conjunction formula
      if(not isinstance(formula1, BinaryFormula) or (isinstance(formula1, BinaryFormula) and not formula1.is_conjunction())):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.IS_NOT_CONJUNCTION, formula_reference, self))
      else:
          # If the left formula of conclusion (the conjunction) is one of the references 
          if(not (formula1.left == self.formula or formula1.right == self.formula)):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_LEFT_OR_RIGHT_CONJUNCTION, self.reference1, self))

    def toLatex(self, symbol_table):
        latex = '\\infer[\\!\\!{\\land\\text{e}}]{'+self.formula.toLatex()+'}{'+symbol_table.get_rule(self.reference1.value).toLatex(symbol_table)+'}'
        return latex

class DisjunctionEliminationDef():
    def __init__(self,line, formula, reference1, reference2, reference3, reference4, reference5):
        self.line = line
        self.formula = formula
        self.reference1 = reference1
        self.reference2 = reference2
        self.reference3 = reference3
        self.reference4 = reference4
        self.reference5 = reference5
        self.is_copied = False

    def evaluation(self,parser,deduction_result):
      # If the references lines occur before the rule line 
      before = parser.check_line_reference_before_rule_error(deduction_result,self)
      # If the reference1 line occurs in the scope of the rule line 
      if before:
        parser.check_line_scope_reference_error(deduction_result,self, reference1=True)      

      formula_reference = parser.symbol_table.find_token(self.line)
      formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
      if(formula1 is None):
        return
      formula2, formula3 = parser.symbol_table.check_scope_delimiter(self.reference2.value, self.reference3.value)
      formula4, formula5 = parser.symbol_table.check_scope_delimiter(self.reference4.value, self.reference5.value)
      if(formula1 is None or formula2 is None or formula3 is None or formula4 is None or formula_reference is None):
        return

      # If the formula (reference 1) is not a disjunction formula
      if(not isinstance(formula1, BinaryFormula) or (isinstance(formula1, BinaryFormula) and not formula1.is_disjunction())):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.IS_NOT_DISJUNCTION, self.reference1, self))
      else:
          # If the hypothese (reference1) is the left formula of the disjunction formula
          if(formula1.left != formula2):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_HYPOTHESIS, self.reference2, self))
          # If the conclusion of the box (reference2) is the right formula of the conclusion
          if(formula1.right != formula4):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_HYPOTHESIS, self.reference4, self))
          # If the conclusion of the box (reference3) it the same of the conclusion
          if(self.formula != formula3):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_BOX_RESULT, self.reference3, self))
          # If the conclusion of the box (reference5) it the same of the conclusion
          if(self.formula != formula5):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_BOX_RESULT, self.reference5, self))

    def toLatex(self, symbol_table):
        hypothesis_number1 = str(len(hypothesis) + 1)
        hypothesis[self.reference2.value] = hypothesis_number1
        hypothesis_number2 = str(len(hypothesis) + 1)
        hypothesis[self.reference4.value] = hypothesis_number2
        latex = '\\infer[\\!\\!{\\lor\\text{e}^{_{'+ hypothesis_number1 + ', ' + hypothesis_number2 +'} } }]{'+self.formula.toLatex()+'}{{'+symbol_table.get_rule(self.reference1.value).toLatex(symbol_table)+'}&{'+symbol_table.get_rule(self.reference3.value).toLatex(symbol_table)+'}&{'+symbol_table.get_rule(self.reference5.value).toLatex(symbol_table)+'}}'
        return latex

class NegationIntroductionDef():
    def __init__(self,line, formula, reference1, reference2):
        self.line = line
        self.formula = formula
        self.reference1 = reference1
        self.reference2 = reference2
        self.is_copied = False

    def evaluation(self,parser,deduction_result):

      formula_reference = parser.symbol_table.find_token(self.line)
      formula1, formula2 = parser.symbol_table.check_scope_delimiter(self.reference1.value, self.reference2.value)
      if(formula1 is None or formula2 is None or formula_reference is None):
        return

      # If the formula is not a negation formula
      if(not isinstance(self.formula, NegationFormula)):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_RESULT, formula_reference, self))
      else:
          # If the hypothese (reference1) is the left formula of the conclusion
          if(self.formula != NegationFormula(formula1)):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_HYPOTHESIS, self.reference1, self))
          # If the conclusion of the box (reference2) is the @
          if(formula2.toString() != '@'):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_BOX_RESULT, self.reference2, self))

    def toLatex(self, symbol_table):
        hypothesis_number = str(len(hypothesis) + 1)
        hypothesis[self.reference1.value] = hypothesis_number
        latex = '\\infer[\\!\\!{\\lnot\\text{i}^{_'+ hypothesis_number +'}}]{'+self.formula.toLatex()+'}{'+symbol_table.get_rule(self.reference2.value).toLatex(symbol_table)+'}'
        return latex

class NegationEliminationDef():
    def __init__(self,line, formula, reference1, reference2):
        self.line = line
        self.formula = formula
        self.reference1 = reference1
        self.reference2 = reference2
        self.is_copied = False

    def evaluation(self,parser,deduction_result):
      # If the references lines occur before the rule line 
      before = parser.check_line_reference_before_rule_error(deduction_result,self)
      # If the reference1 line occurs in the scope of the rule line 
      if before:
        parser.check_line_scope_reference_error(deduction_result,self, reference1=True, reference2=True)      

      formula_reference = parser.symbol_table.find_token(self.line)
      formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
      formula2 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference2.value)
      if(formula1 is None or formula2 is None or formula_reference is None):
        return

      # If the formula (reference 1) is not a contradiction
      if(self.formula.toString()!='@'):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_RESULT, formula_reference, self))
      else:
          # If the left formula of conclusion (the conjunction) is one of the references 
          if(not (NegationFormula(formula2) == formula1 or NegationFormula(formula1) == formula2)):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_NEGATION, self.reference1, self))

    def toLatex(self, symbol_table):
        latex = '\\infer[\\!\\!{\\lnot\\text{e}}]{'+self.formula.toLatex()+'}{{'+symbol_table.get_rule(self.reference1.value).toLatex(symbol_table)+'}&{'+symbol_table.get_rule(self.reference2.value).toLatex(symbol_table)+'}}'
        return latex

class BottomDef():
    def __init__(self,line, formula, reference1):
        self.line = line
        self.formula = formula
        self.reference1 = reference1
        self.is_copied = False
    
    def evaluation(self,parser,deduction_result):
      # If the references lines occur before the rule line 
      before = parser.check_line_reference_before_rule_error(deduction_result,self)
      # If the reference1 line occurs in the scope of the rule line 
      if before:
        parser.check_line_scope_reference_error(deduction_result,self, reference1=True)      

      formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
      if(formula1 is None):
        return

      # If the formula (reference 1) is not a bottom formula
      if(formula1.toString()!='@'):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.IS_NOT_BOTTOM, self.reference1, self))

    def toLatex(self, symbol_table):
        latex = '\\infer[\\!\\!{\\bot e}]{'+self.formula.toLatex()+'}{'+symbol_table.get_rule(self.reference1.value).toLatex(symbol_table)+'}'
        return latex

class RaaDef():
    def __init__(self,line, formula, reference1, reference2):
        self.line = line
        self.formula = formula
        self.reference1 = reference1
        self.reference2 = reference2
        self.is_copied = False

    def evaluation(self,parser,deduction_result):

      formula_reference = parser.symbol_table.find_token(self.line)
      formula1, formula2 = parser.symbol_table.check_scope_delimiter(self.reference1.value, self.reference2.value)
      if(formula1 is None or formula2 is None or formula_reference is None):
        return

      # If the hypothese (reference1) is the left formula of the conclusion
      if(formula1 != NegationFormula(self.formula)):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_HYPOTHESIS, self.reference1, self))
      # If the conclusion of the box (reference2) is the @
      if(formula2.toString() != '@'):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_BOX_RESULT, self.reference2, self))

    def toLatex(self, symbol_table):
        hypothesis_number = str(len(hypothesis) + 1)
        hypothesis[self.reference1.value] = hypothesis_number
        latex = '\\infer[\\!\\!{\\text{raa}^_{'+ hypothesis_number +'} }]{'+self.formula.toLatex()+'}{'+symbol_table.get_rule(self.reference2.value).toLatex(symbol_table)+'}'
        return latex

class CopyDef():
    def __init__(self, line, formula, reference1):
        self.line = line
        self.formula = formula
        self.reference1 = reference1
        self.is_copied = False

    def evaluation(self,parser,deduction_result):
      # If the references lines occur before the rule line 
      before = parser.check_line_reference_before_rule_error(deduction_result,self)
      # If the reference1 line occurs in the scope of the rule line 
      if before:
        parser.check_line_scope_reference_error(deduction_result,self, reference1=True)      

      formula_reference = parser.symbol_table.find_token(self.line)
      formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
      if(formula1 is None):
        return

      # If the formula (reference 1) is not a conjunction formula
      if(formula1!=self.formula):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.COPY_DIFFERENT_FORMULE, formula_reference, self))

    def toLatex(self, symbol_table):
        formula1 = symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
        latex = '{'+formula1.toLatex()+'}'
        return latex

class WrongDef():
    def __init__(self,line, formula):
        self.line = line
        self.formula = formula
        self.is_copied = False

class ForAllEliminationDef():
    def __init__(self, line, formula, reference1):
        self.line = line
        self.formula = formula
        self.reference1 = reference1
        self.is_copied = False

    def evaluation(self,parser,deduction_result):
      # If the references lines occur before the rule line 
      before = parser.check_line_reference_before_rule_error(deduction_result,self)
      # If the reference1 line occurs in the scope of the rule line 
      if before:
        parser.check_line_scope_reference_error(deduction_result,self, reference1=True)      

      formula_reference = parser.symbol_table.find_token(self.line)
      formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
      if(formula1 is None):
        return

      # If the formula is not a universal formula
      if(not isinstance(formula1, QuantifierFormula) or (isinstance(formula1, QuantifierFormula) and not formula1.is_universal())):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_UNIVERSAL_FORMULA, self.reference1, self))

      # If the conclusion is a valid substitution of the universal formula (referecence 1)
      if(isinstance(formula1, QuantifierFormula) and not formula1.valid_substitution(self.formula)):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_SUBSTITUTION_UNIVERSAL, formula_reference, self))

    def toLatex(self, symbol_table):
        latex = '\\infer[\\!\\!\\forall\\text{e}]{'
        latex += self.formula.toLatex()
        latex += '}{'
        latex += symbol_table.get_rule(self.reference1.value).toLatex(symbol_table)
        latex += '}'
        return latex


class ExistsIntroductionDef():
    def __init__(self, line, formula, reference1):
        self.line = line
        self.formula = formula
        self.reference1 = reference1
        self.is_copied = False

    def evaluation(self,parser,deduction_result):
      # If the references lines occur before the rule line 
      before = parser.check_line_reference_before_rule_error(deduction_result,self)
      # If the reference1 line occurs in the scope of the rule line 
      if before:
        parser.check_line_scope_reference_error(deduction_result,self, reference1=True)      


      formula_reference = parser.symbol_table.find_token(self.line)
      formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
      if(formula1 is None):
        return
      # If the formula is not a existential formula
      if(not isinstance(self.formula, QuantifierFormula) or (isinstance(self.formula, QuantifierFormula) and not self.formula.is_existential())):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_EXISTENTIAL_FORMULA, formula_reference, self))
      # If the conclusion is a valid substitution for the variable in formula1
      if(isinstance(self.formula, QuantifierFormula) and not self.formula.valid_substitution(formula1)):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_SUBSTITUTION_EXISTENTIAL, formula_reference, self))

    def toLatex(self, symbol_table):
        latex = '\\infer[\\!\\!\\exists\\text{i}]{'
        latex += self.formula.toLatex()
        latex += '}{'
        latex += symbol_table.get_rule(self.reference1.value).toLatex(symbol_table)
        latex += '}'
        return latex

class ExistsEliminationtionDef():
    def __init__(self,line, formula, reference1, reference2, reference3):
        self.line = line
        self.formula = formula
        self.reference1 = reference1
        self.reference2 = reference2
        self.reference3 = reference3
        self.is_copied = False

    def evaluation(self,parser,deduction_result):
      # If the references lines occur before the rule line 
      before = parser.check_line_reference_before_rule_error(deduction_result,self)
      # If the reference1 line occurs in the scope of the rule line 
      if before:
        parser.check_line_scope_reference_error(deduction_result,self, reference1=True)      

      variable = parser.symbol_table.find_scope_variable(self.reference2.value)
      # If no variable is at the hypothesis line.
      if variable is None:
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.BOX_MUST_HAVE_A_VARIABLE, self.reference2, self))
          return
      # If the variable is not a fresh variable 
      if(not parser.symbol_table.is_fresh_variable(self.reference2.value)):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.VARIABLE_IS_NOT_FRESH_VARIABLE, self.reference2, self))

      formula_reference = parser.symbol_table.find_token(self.line)
      formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
      formula2, formula3 = parser.symbol_table.check_scope_delimiter(self.reference2.value, self.reference3.value)
      if(formula1 is None or formula2 is None or formula3 is None or formula_reference is None):
        return

      # If the rule conclusion is the same as the last formula of the box
      if(self.formula != formula3):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_CONCLUSION_EXISTENTIAL_LAST_RULE, self.reference3, self))
      # If the formula of the first reference is not a existential formula
      if(not isinstance(formula1, QuantifierFormula) or (isinstance(formula1, QuantifierFormula) and not formula1.is_existential())):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_EXISTENTIAL_FORMULA, formula_reference, self))
      # If the hypothesis formula (reference line 2) is a valid subtitutotion of the existential formula (reference line 1)
      if(isinstance(formula1, QuantifierFormula) and formula1.formula.substitution(formula1.variable, variable)!=formula2):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_SUBSTITUTION_EXISTENTIAL, self.reference2, self))
      # if the variable is a free variable at the conclusion formula (referecne line 3)
      if(variable in formula3.free_variables()):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_CONCLUSION_EXISTENTIAL, self.reference2, self))

    def toLatex(self, symbol_table):
        hypothesis_number = str(len(hypothesis) + 1)
        hypothesis[self.reference2.value] = hypothesis_number
        latex = '\\infer[\\!\\!{\\exists\\text{e}^{_'+ hypothesis_number +'} }]{'
        latex += self.formula.toLatex()+'}{'
        latex += symbol_table.get_rule(self.reference1.value).toLatex(symbol_table)
        latex += ' & '+symbol_table.get_rule(self.reference3.value).toLatex(symbol_table)+ '}'
        return latex

class ForAllIntroductiontionDef():
    def __init__(self,line, formula, reference1, reference2):
        self.line = line
        self.formula = formula
        self.reference1 = reference1
        self.reference2 = reference2
        self.is_copied = False

    def evaluation(self,parser,deduction_result):

      variable = parser.symbol_table.find_scope_variable(self.reference1.value)
      first_rule = parser.symbol_table.get_first_rule_from_scope(self.reference1.value)
      # If no variable is at the hypothesis line.
      if variable is None:
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.BOX_MUST_HAVE_A_VARIABLE, self.reference1, self))
          return
      elif isinstance(first_rule, HypothesisFirstOrderDef):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.BOX_MUST_HAVE_ONLY_A_VARIABLE, self.reference1, self))
          return
        
      # If the variable is not a fresh variable 
      if(not parser.symbol_table.is_fresh_variable(self.reference1.value)):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.VARIABLE_IS_NOT_FRESH_VARIABLE, self.reference1, self))

      formula_reference = parser.symbol_table.find_token(self.line)
      formula1, formula2 = parser.symbol_table.check_scope_delimiter(self.reference1.value, self.reference2.value)
      if(formula1 is None or formula2 is None or formula_reference is None):
        return

      # If the formula of the first reference is not a existential formula
      if(not isinstance(self.formula, QuantifierFormula) or (isinstance(self.formula, QuantifierFormula) and not self.formula.is_universal())):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_EXISTENTIAL_FORMULA, formula_reference, self))
      # If the conclusion is a universal formula of the last formula (reference line 2) by substitution of the variable
      if(isinstance(self.formula, QuantifierFormula) and self.formula.formula.substitution(self.formula.variable, variable)!=formula2):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_CONCLUSION_UNIVERSAL_LAST_RULE, self.reference2, self))
      # if the variable is a free variable at the conclusion formula (reference line 3)
      if(variable in self.formula.free_variables()):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_CONCLUSION_UNIVERSAL, formula_reference, self))

    def toLatex(self, symbol_table):
        hypothesis_number = str(len(hypothesis) + 1)
        hypothesis[self.reference2.value] = hypothesis_number
        latex = '\\infer[\\!\\!{\\forall\\text{i}}]{'
        latex += self.formula.toLatex()+'}{'
        latex += symbol_table.get_rule(self.reference2.value).toLatex(symbol_table)+ '}'
        return latex