import traceback
from ParserFactory import ParserFactory
import constants
import sys

from models.BinaryFormula import BinaryFormula
from models.NegationFormula import NegationFormula
from models.QuantifierFormula import QuantifierFormula


class PredicateFormula():
    def __init__(self, name = '', variables = []):
        self.variables = variables
        self.name = name

    def __eq__(self, other): 
        if not isinstance(other, PredicateFormula):
            return NotImplemented
        return self.variables == other.variables and self.name == other.name
    
    def __ne__(self, other): 
        if not isinstance(other, PredicateFormula):
            return NotImplemented

        return self.variables != other.variables or self.name != other.name

    def toLatex(self, parentheses= False):
        if self.variables: 
            return self.name+'('+','.join(self.variables)+')'
        else:
            return self.name

    def toString(self, parentheses= False):
        if self.variables: 
            return self.name+'('+','.join(self.variables)+')'
        else:
            return self.name

    def all_variables(self):
      return set(self.variables)

    def bound_variables(self):
      return set()

    def free_variables(self):
      return set(self.variables)

    def is_substitutable(self, x, y):
      return True

    def substitution(self, var_x, a):
      aux_variables = []
      for v in self.variables:
        if(v==var_x): 
           aux_variables.append(a)
        else: 
           aux_variables.append(v)
      return PredicateFormula(self.name, aux_variables)

class SymbolTable:

    def toString(self):
      for i in range(len(self.symbol_table)):
        print(self.symbol_table['scope_{}'.format(i)])

    def len_symbol_table(self):
      r = 0
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['scope_{}'.format(i)]['rules']:
          r+=1
      return r

    def find_token(self, line):
      for i in range(len(self.symbol_table)):
        for j in range(len(self.symbol_table['scope_{}'.format(i)]['rules'])):
          if (self.symbol_table['scope_{}'.format(i)]['rules'][j].line==line):
            return self.symbol_table['scope_{}'.format(i)]['lines'][j]
      return None


    def check_is_visible(self, formula1_line, formula2_line):
      #Find formula1_line scope.
      if (int(formula1_line) <= int(formula2_line)): 
        return False
      current_scope = None
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['scope_{}'.format(i)]['rules']:
          if rule and (rule.line == formula1_line):
            current_scope = self.symbol_table['scope_{}'.format(i)]
            break
        if current_scope is not None: 
           break
      #Check if formula2_line in formula1_line scope 
      while current_scope is not None:
        for rule in current_scope['rules']:
          if rule and (rule.line == formula2_line):
            return True
        current_scope = self.symbol_table[current_scope['parent']] if 'parent' in current_scope else None
      return False

    def find_scope(self, line):
        for key, scope in self.symbol_table.items():
            for rule in scope['rules']:
                if rule and (rule.line == line):
                    return key 
        #Verifica se a linha não tem fórmula (introdução do universal)
        for key, scope in self.symbol_table.items():
          if(int(scope['start_line'])==int(line)):
            return key

        return None

    # Returns True if the scope variable of the line is a fresh variable, i.e., it did not occur before this scope. 
    def is_fresh_variable(self, line):
      current_scope = self.find_scope(line)
      variable = self.symbol_table[current_scope]['variable'] if current_scope is not None else None
      return variable not in self.get_free_variables_before_scope(line)

    def get_free_variables_before_scope(self, line):
      free_variables = set()
      #Find formula1_line scope.
      scope = self.find_scope(line)
      scope = self.symbol_table[scope]['parent'] if scope in self.symbol_table else None
      while scope is not None:
          for rule in self.symbol_table[scope]['rules']:
            if (int(rule.line) < int(line)):
              free_variables = free_variables.union(rule.formula.free_variables())
            #Adds the variable for the universal introduction rule, i.e., if the line does not have a formula
            if (int(self.symbol_table[scope]['start_line'])<int(line) and self.symbol_table[scope]['variable']):
              free_variables = free_variables.union(set(self.symbol_table[scope]['variable']))
          scope = self.symbol_table[scope]['parent']
      return free_variables

    def get_visible_lines(self, formula1_line):
      #Find formula1_line scope.
      lines = []
      current_scope = None
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['scope_{}'.format(i)]['rules']:
          if rule and (rule.line == formula1_line):
            current_scope = self.symbol_table['scope_{}'.format(i)]
            break
        if current_scope is not None: 
           break
      #Check if formula2_line in formula1_line scope 
      while current_scope is not None:
        for rule in current_scope['rules']:
          if rule and (int(rule.line) < int(formula1_line)):
            lines.append(rule.line)
        current_scope = self.symbol_table[current_scope['parent']] if current_scope['parent'] else None
      return lines
      
      
    def getPremisses(self):
      lines = []
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['scope_{}'.format(i)]['rules']:
          if(isinstance(rule, PremisseDef) ):
            lines.append(rule.line)
      return lines

    def getPremissesFormulas(self):
      formulas = []
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['scope_{}'.format(i)]['rules']:
          if(isinstance(rule, PremisseDef) and rule.formula not in formulas):
            formulas.append(rule.formula)
      return formulas

    def getConclusionFormula(self):
      if self.symbol_table["scope_0"]["rules"][-1]:
        return self.symbol_table["scope_0"]["rules"][-1].formula
      else:
        return None
    
    def theoremToString(self,parentheses=False):
      premissas = sorted([p.toString(parentheses=parentheses) for p in self.getPremissesFormulas()])
      fConclusion = self.getConclusionFormula()
      if(fConclusion):
        return (', '.join(premissas)+' |- '+fConclusion.toString(parentheses=parentheses))

    def theoremToLatex(self,parentheses=False):
      premisses = ([p.toLatex(parentheses=parentheses) for p in self.getPremissesFormulas()])
      fConclusion = self.getConclusionFormula()
      if(fConclusion):
        return (', '.join(premisses)+' \\vdash '+fConclusion.toLatex(parentheses=parentheses))

    def set_lines_visible(self):
        self.line_visible_lines = {}
        n = self.len_symbol_table()
        for i in range(1,n):
          self.line_visible_lines[str(i)] = self.get_visible_lines(str(i))



    def __init__(self):
        self.line_visible_lines = {}
        self.symbol_table = {
            'scope_0': {
                'name': 'scope_0',
                'parent': None,
                'rules': [],
                'lines': [],
                'variable': None,
                'start_line': '1', #Robson Não estava presente
                'end_line': '1'
            }
        }
        self.current_scope = 'scope_0'

    def insert(self, symbol, line):
        self.symbol_table[self.current_scope]['rules'].append(symbol)
        self.symbol_table[self.current_scope]['lines'].append(line)

    def start_scope(self, scope):
        self.current_scope = scope

    def end_scope(self, end_line):
        self.symbol_table[self.current_scope]['end_line'] = end_line
        if(self.symbol_table[self.current_scope]['parent'] is not None):
            self.current_scope = self.symbol_table[self.current_scope]['parent']

    def add_scope(self, start_line, variable=None):
        scope = 'scope_{}'.format(len(self.symbol_table))
        self.symbol_table[scope] = {
            'name': scope,
            'parent': self.current_scope,
            'rules': [],
            'lines': [],
            'variable': variable,
            'start_line': start_line,
            'end_line': start_line#Robson, não ser start_line        
            }
        self.start_scope(scope)

    def find_scope_variable(self, line):
        scope = self.find_scope(line)
        if scope is not None:
          return self.symbol_table[scope]['variable']
        #Verifica se a linha não tem fórmula (introdução do universal)
        for key, scope in self.symbol_table.items():
          if(int(scope['start_line'])==int(line)):
            return scope['variable']          
        return None

    def check_scope_is_valid(self, scope):
        current_scope = self.current_scope
        while current_scope is not None:
            if current_scope == scope:
                return True
            current_scope = self.symbol_table[current_scope]['parent']
        return False

    def lookup_formula_by_line(self, symbol_line, line):
        scope = self.find_scope(symbol_line)
        while scope is not None:
            for rule in self.symbol_table[scope]['rules']:
                if rule.line == line:
                    return rule.formula
            scope = self.symbol_table[scope]['parent']
        return None

    def check_scope_delimiter(self, line1, line2):
        for key, scope in self.symbol_table.items():
            if key != 'scope_0':
                if(scope['start_line'] == line1 and scope['end_line'] == line2):
                    start_rule = scope['rules'][0].formula if scope['rules'][0] is not None else None
                    end_rule = scope['rules'][-1].formula if scope['rules'][-1] is not None else None
                    return (start_rule, end_rule)
        return None, None

    def get_box_start(self):
        if self.current_scope != 'scope_0':
            return self.symbol_table[self.current_scope]['start_line']
        return None

    def get_box_end(self):
        if self.current_scope != 'scope_0':
            return self.symbol_table[self.current_scope]['end_line']
        return None      

    def get_first_rule_from_scope(self, line):
        scope = self.find_scope(line)
        if self.symbol_table[scope]['rules']==[]:
           return None
        return self.symbol_table[scope]['rules'][0]
   
    def get_last_rule_from_scope(self):
        if self.symbol_table[self.current_scope]['rules']==[]: 
           return None
        return self.symbol_table[self.current_scope]['rules'][-1]

    def get_rule(self, rule_line):
        for key, scope in self.symbol_table.items():
            for key, line in enumerate(scope['lines']):
                if line.value == rule_line:
                    return scope['rules'][key]
        return None

    def count_formulas_by_end_box(self, line):
        for key, scope in self.symbol_table.items():
            if key != 'scope_0':
                if(scope['end_line'] == line):
                    return (line - int(scope['start_line']))
        return 0

## dados_json.py
#import json

class natural_deduction_return:
    def __init__(self):
        self.premisses = []
        self.conclusion = None
        self.gentzen = ""
        self.fitch = ""
        self.errors = []

    def add_error(self, error):
        self.errors.append(error)

## File ast.py
hypothesis = {}

def limpaHipotese():
    global hypothesis
    hypothesis = {}


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


## File analisys.py

deduction_result = natural_deduction_return()

def value_error_handle(exctype, value, tb):
    deduction_result.add_error(str(value))

sys.excepthook = value_error_handle

def check_proof(input_proof, input_theorem=None, display_theorem=True, display_fitch=True, display_gentzen=True):
    try:
        parser_nadia = ParserFactory.create_nadia_parser(input_proof)
        parser_theorem = ParserFactory.create_theorem_parser(input_theorem) if input_theorem else None
        result = parser_nadia.getProof(input_proof)
        r = ''

        if(result.errors==[]):
            s_theorem = parser_theorem.toString(result.premisses, result.conclusion)
            if input_theorem is not None: 
                premisses, conclusion = parser_theorem.getTheorem(input_theorem)
                if conclusion is None:
                    return f'{input_theorem} não é um teorema válido!'

                set_premisses = set([p.toString() for p in premisses])
                set_premisses_result = set([p.toString() for p in result.premisses])
                if(conclusion==result.conclusion and set_premisses==set_premisses_result):
                    r += "A demonstração está correta."
                    if display_theorem:
                       r += "\n"+s_theorem
                else:
                    r += f"Sua demostração de {s_theorem} é válida, mas é diferente da demonstração solicitada {input_theorem}"
            else:
                r += "A demonstração está correta."
                if display_theorem:
                    r += "\n"+s_theorem
            if display_fitch:
                r += "\n\nCódigo da demonstração no estilo Fitch em Latex:\n"
                r += str(result.fitch)
            if display_gentzen:
                r += "\n\nCódigo da demonstração no estilo Gentzen em Latex:\n"
                r += str(result.gentzen)
        else:
            r += "Os seguintes erros foram encontrados:\n\n"
            for error in result.errors:
                r += str(error)
        return r
    except ValueError:
        s = traceback.format_exc()
        result = (s.split("@@"))[-1]
        r = "Os seguintes erros foram encontrados:\n\n"
        r += result
        return r
    else:
        pass