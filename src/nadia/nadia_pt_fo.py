import traceback
from rply import ParserGenerator
import sys
import copy

# Import das novas classes
from AtomFormula.AtomFormula import AtomFormula
from BinaryFormula.AndFormula import AndFormula
from BinaryFormula.BinaryFormula import BinaryFormula
from BinaryFormula.ImplicationFormula import ImplicationFormula
from BinaryFormula.OrFormula import OrFormula
from Factory.DisjunctionEliminationDef import DisjunctionEliminationDef
from Factory.ImplicationIntroductionDef import ImplicationIntroductionDef
from Factory.NegationIntroductionDef import NegationIntroductionDef
from Factory.RaaDef import RaaDef
from Factory.ForAllIntroductionDef import ForAllIntroductionDef
from Factory.RuleFactory import RuleFactory
from Factory.ExistsEliminationDef import ExistsEliminationDef
from NegationFormula.NegationFormula import NegationFormula
from PredicatedFormula.PredicatedFormula import PredicateFormula
from QuantifierFormula.ExistentialFormula import ExistentialFormula
from QuantifierFormula.UniversalFormula import UniversalFormula
from nadia.parser.parser_theorem import ParserTheorem
from utils.HypothesisManager import HypothesisManager
from models.constants import constants
from nadia.Lexer.lexer import Lexer
from nadia.errors.error_strategy import ErrorContext

## File symbol_table.py
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
          # Usando RuleBase em vez de PremisseDef específico
          if rule and hasattr(rule, 'formula') and not hasattr(rule, 'reference1'):
            # Lógica para identificar premissas pode precisar de ajuste
            lines.append(rule.line)
      return lines

    def getPremissesFormulas(self):
      formulas = []
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['scope_{}'.format(i)]['rules']:
          # Lógica para identificar premissas - pode precisar de ajuste
          if rule and hasattr(rule, 'formula') and not hasattr(rule, 'reference1'):
            if rule.formula not in formulas:
              formulas.append(rule.formula)
      return formulas

    def getConclusionFormula(self):
      if self.symbol_table["scope_0"]["rules"] and self.symbol_table["scope_0"]["rules"][-1]:
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
                'start_line': '1',
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
            'end_line': start_line        
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
class natural_deduction_return:
    def __init__(self):
        self.premisses = []
        self.conclusion = None
        self.gentzen = ""
        self.fitch = ""
        self.errors = []

    def add_error(self, error):
        self.errors.append(error)

## File analisys.py

deduction_result = natural_deduction_return()

def value_error_handle(exctype, value, tb):
    deduction_result.add_error(str(value))

sys.excepthook = value_error_handle

## dados_json.py
class natural_deduction_return:
    def __init__(self):
        self.premisses = []
        self.conclusion = None
        self.gentzen = ""
        self.fitch = ""
        self.errors = []

    def add_error(self, error):
        self.errors.append(error)

## File analisys.py

deduction_result = natural_deduction_return()

def value_error_handle(exctype, value, tb):
    deduction_result.add_error(str(value))

sys.excepthook = value_error_handle

class ParserNadia():
    def __init__(self, state):
        self.state = state
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            ['NUM', 'DOT', 'COMMA', 'OPEN_PAREN', 'CLOSE_PAREN', 'NOT', 'RAA',
             'AND', 'OR', 'OR_INTROD', 'OR_ELIM', 'BOTTOM','BOTTOM_ELIM', 'OPEN_BRACKET', 'AND_INTROD',
             'AND_ELIM', 'NEG_INTROD', 'NEG_ELIM', 'HYPOTHESIS', 'PREMISE', 'ATOM', 'CLOSE_BRACKET',
             'DASH', 'COPY', 'IMP_ELIM', 'IMPLIE', 'IMP_INTROD',
             'VAR', 'EXT', 'ALL', 'ALL_ELIM', 'EXT_INTROD', 'EXT_ELIM', 'ALL_INTROD' ],
            precedence=[
                ('right', ['IMPLIE']),
                ('right', ['OR']),
                ('right', ['AND']),
                ('right', ['EXT']),
                ('right', ['ALL']),
                ('right', ['NOT']),
            ]
        )
        self.symbol_table = SymbolTable()
        self.box_latex = "\\begin{logicproof}{6}\n"
        self.has_error = False
        self.rule_factory = RuleFactory()
        self.error_context = ErrorContext()  # Instância do contexto de erros

    def verify_sequence_lines_error(self, deduction_result):
        productions = self.state.splitlines()
        i = 1
        for p in productions:
          x = p.split('.')[0]
          if x.isdigit():
            if int(x)!=i: 
              self.has_error = True
              if(i==1): 
                deduction_result.add_error("{}\n^, A numeração da linha {} deveria ser {}, pois a numeração da prova deve ser sequencial e iniciar em 1.\n".format(p,x,i))
              else: 
                deduction_result.add_error("{}\n^, A numeração da linha {} deveria ser {}, pois a numeração da prova deve ser sequencial.\n".format(p,x,i))
              break
            i+=1

    def check_is_closed_boxes_by_rule(self,deduction_result):
      current_scope = None
      for i in range(1,len(self.symbol_table.symbol_table)):
        current_scope = self.symbol_table.symbol_table['scope_{}'.format(i)]
        current_scope_parent = self.symbol_table.symbol_table[current_scope['parent']] if current_scope['parent'] else None
        if(current_scope_parent is None):
          self.has_error = True
          deduction_result.add_error("Erro no escopo da demontração: escopo pai não encontrado.")
        rule_next = None
        for rule in current_scope_parent['rules']:
          if(int(rule.line)>int(current_scope['end_line'])):
            rule_next = rule
            break
        # Verificação genérica usando RuleBase
        if (rule_next is None or not hasattr(rule_next, 'evaluation')):
          self.has_error = True
          begin_rule = current_scope["rules"][0]
          begin_token = current_scope["lines"][0]
          deduction_result.add_error(self.get_error(constants.BOX_MUST_BE_DISPOSED, begin_token, begin_rule))

    def check_line_reference_before_rule_error(self, deduction_result, rule):
      result = True
      for i in range(1, 6):
        ref_attr = f'reference{i}'
        if hasattr(rule, ref_attr):
            ref = getattr(rule, ref_attr)
            if ref and int(ref.value) >= int(rule.line):
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.REFERENCED_LINE_NOT_DEFINED, ref, rule))
                result = False
      return result

    def check_line_scope_reference_error(self, deduction_result, rule, **references):
      result = True
      for ref_name, should_check in references.items():
        if should_check and hasattr(rule, ref_name):
            ref = getattr(rule, ref_name)
            if self.symbol_table.lookup_formula_by_line(rule.line, ref.value) is None:
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.USING_DESCARTED_RULE, ref, rule))
                result = False
      return result

    def check_scope_reference_error(self, deduction_result, rule):
        result = True
        if (isinstance(rule, NegationIntroductionDef) or isinstance(rule, RaaDef)
          or isinstance(rule, ImplicationIntroductionDef) or isinstance(rule, ForAllIntroductionDef)):
          formula1, formula2 = self.symbol_table.check_scope_delimiter(rule.reference1.value, rule.reference2.value)
          # If the box references does not form a valid box 
          if(formula1 is None):
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.INVALID_SCOPE_DELIMITER, rule.reference1, rule))
              result = False
          #If the box references are not followed by each other.
          elif not (int(rule.line) > int(rule.reference2.value) and int(rule.reference2.value)>= int(rule.reference1.value)):
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.INVALID_SCOPE_DELIMITER, rule.reference1, rule))
              result = False
          # If box is not imediatally closed by the rule 
          if int(rule.line) != int(rule.reference2.value)+1 and not rule.is_copied:
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.BOX_MUST_BE_DISPOSED_BY_RULE, rule.reference1, rule))
              result = False

        elif (isinstance(rule, ExistsEliminationDef)):
          formula1, formula2 = self.symbol_table.check_scope_delimiter(rule.reference2.value, rule.reference3.value)
          # If the box references does not form a valid box 
          if(formula1 is None):
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.INVALID_SCOPE_DELIMITER, rule.reference2, rule))
              result = False
          #If the box references are not followed by each other.
          elif not (int(rule.line) > int(rule.reference3.value) and int(rule.reference3.value)>= int(rule.reference2.value) 
                and int(rule.reference2.value)>= int(rule.reference1.value)):
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.INVALID_SCOPE_DELIMITER, rule.reference2, rule))
              result = False
          # If box is not imediatally closed by the rule 
          if int(rule.line) != int(rule.reference3.value)+1:
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.BOX_MUST_BE_DISPOSED_BY_RULE, rule.reference2, rule))
              result = False

        elif isinstance(rule, DisjunctionEliminationDef):   
          formula1, formula2 = self.symbol_table.check_scope_delimiter(rule.reference2.value, rule.reference3.value)
          # If the box references does not form a valid box 
          if(formula1 is None):
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.INVALID_SCOPE_DELIMITER, rule.reference2, rule))
              result = False
          #If the box references are not followed by each other.
          elif not (int(rule.line) > int(rule.reference3.value) and int(rule.reference3.value)>= int(rule.reference2.value) 
                and int(rule.reference2.value)>= int(rule.reference1.value)):
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.INVALID_SCOPE_DELIMITER, rule.reference2, rule))
              result = False
          formula1, formula2 = self.symbol_table.check_scope_delimiter(rule.reference4.value, rule.reference5.value)
          # If the box references does not form a valid box 
          if(formula1 is None):
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.INVALID_SCOPE_DELIMITER, rule.reference4, rule))
              result = False
          #If the box references are not followed by each other.
          elif not (int(rule.line) > int(rule.reference5.value) and int(rule.reference5.value)>= int(rule.reference4.value) 
                and int(rule.reference4.value)== int(rule.reference3.value)+1):
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.INVALID_SCOPE_DELIMITER, rule.reference4, rule))
              result = False
          # If box is not imediatally closed by the rule 
          if int(rule.line) != int(rule.reference5.value)+1:
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.BOX_MUST_BE_DISPOSED_BY_RULE, rule.reference4, rule))
              result = False
        
        return result

    def parse(self):
        deduction_result = natural_deduction_return()
        
        @self.pg.production('program : steps')
        def program(p):
            self.symbol_table.set_lines_visible()
            self.verify_sequence_lines_error(deduction_result)
            self.check_is_closed_boxes_by_rule(deduction_result)

            rule_info = p[0]
            for i in rule_info:
                rule_line, formula_reference = rule_info[i]
                rule = self.symbol_table.get_rule(rule_line.value)

                # Avaliação genérica de todas as regras
                if rule and hasattr(rule, 'evaluation'):
                    rule.evaluation(self, deduction_result)

            if not self.has_error:
                latex = '\\['
                formula_reference = str(sorted(list(map(int, rule_info.keys())))[-1])
                rule = self.symbol_table.get_rule(rule_info[formula_reference][0].value)
                latex += rule.toLatex(self.symbol_table)
                latex += '\\]'
                
                HypothesisManager.reset()  # Usando HypothesisManager em vez de limpaHipotese
                
                deduction_result.premisses = self.symbol_table.getPremissesFormulas()
                deduction_result.conclusion = self.symbol_table.getConclusionFormula()
                deduction_result.fitch = self.box_latex[:-3] + '\n\end{logicproof}'
                deduction_result.gentzen = latex + "\n"
            return deduction_result

        @self.pg.production('steps : steps step')
        @self.pg.production('steps : step')
        def steps(p):
            if len(p) == 1:
                result = p[0]
                return {result[0].value: result}
            else:
                result = p[1]
                p[0][result[0].value] = result
                return p[0]

        # Produções usando a Factory
        @self.pg.production('step : NUM DOT formula PREMISE')
        def Premisse(p):
            formula_result = p[2]
            formula = formula_result[1]
            premisse = self.rule_factory.create_rule('premise', p[0].value, formula)
            self.symbol_table.insert(premisse, p[0])
            self.box_latex += "{} & premissa\\\\\n".format(formula.toLatex())
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT OPEN_BRACKET formula HYPOTHESIS')
        @self.pg.production('step : NUM DOT OPEN_BRACKET VAR')
        @self.pg.production('step : NUM DOT OPEN_BRACKET VAR formula HYPOTHESIS')
        def Hypothesis(p):
            formula_result = {}
            if len(p) == 4 and p[3].gettokentype() == 'VAR':
                variable = p[3].value
                self.symbol_table.add_scope(p[0].value,variable=variable)
                self.box_latex += "\\begin{subproof}\n"
                self.box_latex += "\\llap{$"+str(variable)+"\\quad$} &"+"\\\\\n"
                return p[0], None
            elif len(p) == 5:
                formula_result = p[3]
                self.symbol_table.add_scope(p[0].value)
                formula = formula_result[1]
                self.box_latex += "\\begin{subproof}\n"
                self.box_latex += "{} & hipótese\\\\\n".format(formula.toLatex())
                hypothesis = self.rule_factory.create_rule('hypothesis', p[0].value, formula)
            elif len(p) == 6:
                variable = p[3].value
                formula_result = p[4]
                self.symbol_table.add_scope(p[0].value,variable=variable)
                formula = formula_result[1]
                self.box_latex += "\\begin{subproof}\n"
                self.box_latex += "\\llap{$"+str(variable)+"\\quad$}"+"{} & hipótese\\\\\n".format(formula.toLatex())
                hypothesis = self.rule_factory.create_rule('hypothesis_first_order', p[0].value, formula, variable)
            elif len(p) == 4 and p[3].gettokentype() != 'VAR':
                formula_result = p[2]
                formula = formula_result[1]
                self.box_latex += "{} & hipótese\\\\\n".format(formula.toLatex())
                hypothesis = self.rule_factory.create_rule('hypothesis', p[0].value, formula)

            self.symbol_table.insert(hypothesis, p[0])
            if self.symbol_table.current_scope == "scope_0":
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.HYPOTHESIS_WITHOUT_BOX, formula_result[0], hypothesis))
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula HYPOTHESIS')
        @self.pg.production('step : NUM DOT formula ATOM')
        @self.pg.production('step : NUM DOT OPEN_BRACKET formula ATOM')
        def Wrong_pre_hip(p):
            self.has_error = True
            wrong_rule = RuleFactory._create_wrong(p[0].value, p[-2])
            deduction_result.add_error(self.get_error(constants.INVALID_HIP_PRE_WRITE, p[-1], wrong_rule))
            return p[0], p[-2]

        @self.pg.production('step : NUM DOT formula NEG_ELIM NUM COMMA NUM')
        def Neg_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            negationElimination = self.rule_factory.create_rule('negation_elimination', p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(negationElimination, p[0])
            self.box_latex += "{} & $\lnot e$ {}, {}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula IMP_ELIM NUM COMMA NUM')
        def Imp_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            implicationElimination = self.rule_factory.create_rule('implication_elimination', p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(implicationElimination, p[0])
            self.box_latex += "{} & $\\rightarrow e$ {}, {}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]
            
        @self.pg.production('step : NUM DOT formula IMP_INTROD NUM DASH NUM')
        def Imp_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            implicationIntrod = self.rule_factory.create_rule('implication_introduction', p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(implicationIntrod, p[0])
            self.box_latex += "{} & $\\rightarrow i$ {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula OR_INTROD NUM')
        def Or_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            disjunctionIntrod = self.rule_factory.create_rule('disjunction_introduction', p[0].value, formula, p[4])
            self.symbol_table.insert(disjunctionIntrod, p[0])
            self.box_latex += "{} & $\\lor i$ {}\\\\\n".format(formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula AND_INTROD NUM COMMA NUM')
        def And_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            andIntrod = self.rule_factory.create_rule('and_introduction', p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(andIntrod, p[0])
            self.box_latex += "{} & $\\land i$ {},{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula AND_ELIM NUM')
        def And_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            andElim = self.rule_factory.create_rule('and_elimination', p[0].value, formula, p[4])
            self.symbol_table.insert(andElim, p[0])
            self.box_latex += "{} & $\\land e$ {}\\\\\n".format(formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula OR_ELIM NUM COMMA NUM DASH NUM COMMA NUM DASH NUM')
        def Or_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            orElim = self.rule_factory.create_rule('disjunction_elimination', p[0].value, formula, p[4], p[6], p[8], p[10], p[12])
            self.symbol_table.insert(orElim, p[0])
            self.box_latex += "{} & $\\lor e$ {}, {}-{}, {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value, p[8].value, p[10].value, p[12].value)
            return p[0], formula_result[0]
        
        @self.pg.production('step : NUM DOT formula NEG_INTROD NUM DASH NUM')
        def Neg_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            negationIntrod = self.rule_factory.create_rule('negation_introduction', p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(negationIntrod, p[0])
            self.box_latex += "{} & $\lnot i$ {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula BOTTOM_ELIM NUM')
        def Bottom(p):
            formula_result = p[2]
            formula = formula_result[1]
            bottom = self.rule_factory.create_rule('bottom_elimination', p[0].value, formula, p[4])
            self.symbol_table.insert(bottom, p[0])
            self.box_latex += "{} & $\\bot e$ {}\\\\\n".format(formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula RAA NUM DASH NUM')
        def Raa(p):
            formula_result = p[2]
            formula = formula_result[1]
            raa = self.rule_factory.create_rule('raa', p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(raa, p[0])
            self.box_latex += "{} & raa {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula COPY NUM')
        def Copy(p):
            copied_scope = self.symbol_table.find_scope(p[4].value)
            if self.symbol_table.check_scope_is_valid(copied_scope):
                line = p[4].value
                formula_result = p[2]
                original_rule = self.symbol_table.get_rule(line)
                
                if original_rule is not None:
                    # Cria uma NOVA instância da regra copiada
                    rule = copy.deepcopy(original_rule)
                    rule._is_copied = True  # Usar _is_copied em vez de is_copied
                    
                    if hasattr(rule, 'copied'):
                        rule.copied = original_rule.line
                    
                    formula = formula_result[1]
                    
                    # Verifica se a fórmula é a mesma
                    if rule.formula != formula:
                        formula_diff = rule.formula
                        rule._formula = formula  # Usar _formula em vez de formula
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.COPY_DIFFERENT_FORMULE, formula_result[0], rule))
                        rule._formula = formula_diff
                    
                    self.box_latex += "{} & copie {}\\\\\n".format(formula.toLatex(), p[4].value)
                    
                    # Cria uma nova instância do CopyDef para a linha atual
                    copy_rule = self.rule_factory.create_rule('copy', p[0].value, formula, p[4])
                    copy_rule._is_copied = True
                    self.symbol_table.insert(copy_rule, p[0])
                else:
                    self.has_error = True
                    deduction_result.add_error(self.get_error(constants.NONE_COPY, p[4], None))
            else:
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.USING_DESCARTED_RULE, p[4], None))
            
            return p[0], p[2][0]

        @self.pg.production('step : CLOSE_BRACKET')
        def close_box(p):
            rule = self.symbol_table.get_last_rule_from_scope()
            if rule is None:
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.BOX_MUST_BE_DISPOSED_BY_RULE, p[0], rule))              
                return p[0], rule
            elif self.symbol_table.get_box_start():
                self.symbol_table.end_scope(rule.line)
                self.box_latex = self.box_latex[:-3] + '\n'
                self.box_latex += "\end{subproof}\n"
            else:
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.CLOSE_BRACKET_WITHOUT_BOX, p[0], rule))
            token = p[0]
            token.value = rule.line
            return p[0], rule.formula

        @self.pg.production('step : NUM DOT formula ALL_ELIM NUM')
        def For_all_elim(p):
          formula_result = p[2]
          formula = formula_result[1]
          forAllElimination = self.rule_factory.create_rule('forall_elimination', p[0].value, formula, p[4])
          self.symbol_table.insert(forAllElimination, p[0])
          self.box_latex += "{} & $\\forall e$ {}\\\\\n".format(formula.toLatex(), p[4].value)
          return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula EXT_INTROD NUM')
        def Exists_intro(p):
          formula_result = p[2]
          formula = formula_result[1]
          existsIntroduction = self.rule_factory.create_rule('exists_introduction', p[0].value, formula, p[4])
          self.symbol_table.insert(existsIntroduction, p[0])
          self.box_latex += "{} & $\\exists i$ {}\\\\\n".format(formula.toLatex(), p[4].value)
          return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula EXT_ELIM NUM COMMA NUM DASH NUM')
        def Exists_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            existsElim = self.rule_factory.create_rule('exists_elimination', p[0].value, formula, p[4], p[6], p[8])
            self.symbol_table.insert(existsElim, p[0])
            self.box_latex += "{} & $\\exists e$ {},{}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value, p[8].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula ALL_INTROD NUM DASH NUM')
        def For_all_intro(p):
            formula_result = p[2]
            formula = formula_result[1]
            allIntrod = self.rule_factory.create_rule('forall_introduction', p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(allIntrod, p[0])
            self.box_latex += "{} & $\\forall i$ {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula IMP_ELIM NUM ')
        @self.pg.production('step : NUM DOT formula IMP_ELIM NUM DASH NUM')
        @self.pg.production('step : NUM DOT formula AND_INTROD NUM ')
        @self.pg.production('step : NUM DOT formula AND_INTROD NUM DASH NUM')
        @self.pg.production('step : NUM DOT formula NEG_ELIM NUM ')
        @self.pg.production('step : NUM DOT formula NEG_ELIM NUM DASH NUM')
        def Wrong_use_conective_references(p):
            self.has_error = True
            from Factory.WrongDef import WrongDef
            wrong_rule = WrongDef(p[0].value, p[2])
            deduction_result.add_error(self.get_error(constants.INVALID_RULE, p[3], wrong_rule))
            return p[0], p[2]

        @self.pg.production('step : NUM DOT formula AND_ELIM NUM COMMA NUM ')
        @self.pg.production('step : NUM DOT formula AND_ELIM NUM DASH NUM')
        def Wrong_use_conective_reference(p):
            self.has_error = True
            from Factory.WrongDef import WrongDef
            wrong_rule = WrongDef(p[0].value, p[2])
            deduction_result.add_error(self.get_error(constants.INVALID_RULE_ONE_REFERENCE, p[3], wrong_rule))
            return p[0], p[2]

        @self.pg.production('formula : EXT formula')
        @self.pg.production('formula : ALL formula')
        @self.pg.production('formula : formula OR formula')
        @self.pg.production('formula : formula AND formula')
        @self.pg.production('formula : formula IMPLIE formula')
        @self.pg.production('formula : NOT formula')
        @self.pg.production('formula : ATOM OPEN_PAREN variableslist CLOSE_PAREN')
        @self.pg.production('formula : ATOM')
        @self.pg.production('formula : BOTTOM')
        def formula(p):
            if len(p) < 3:
                if p[0].gettokentype() == 'ATOM':
                    return p[0], AtomFormula(key=p[0].value)
                elif p[0].gettokentype() == 'BOTTOM':
                    return p[0], AtomFormula(key=p[0].value)
                elif p[0].gettokentype() == 'NOT':
                    result = p[1]
                    return p[0], NegationFormula(formula=result[1])  
                elif type(p[0]) is not tuple:
                  result1 = p[0]
                  result2 = p[1]
                  # Universal Formula
                  if p[0].gettokentype() == 'EXT':  
                    var = p[0].value.split('E')[1]
                    return p[0], ExistentialFormula(variable=var, formula=p[1][1])
                  elif p[0].gettokentype() == 'ALL':  
                    var = p[0].value.split('A')[1]
                    return p[0], UniversalFormula(variable=var, formula=p[1][1])
            elif len(p)==4:
              # Predicate Formula
              varlist = p[2]
              return p[0], PredicateFormula(name=p[0].value,variables=varlist[1])            
            elif len(p) == 3:
              # Binary Formula
              result1 = p[0]
              result2 = p[2]
              if(p[1].value=='&'):
                return result1[0], AndFormula(left=result1[1], right=result2[1])
              elif(p[1].value=='|'):
                return result1[0], OrFormula(left=result1[1], right=result2[1])
              elif(p[1].value=='->'):
                return result1[0], ImplicationFormula(left=result1[1], right=result2[1])
              else:
                return result1[0], BinaryFormula(key=p[1].value, left=result1[1], right=result2[1])

        @self.pg.production('variableslist : VAR')
        @self.pg.production('variableslist : VAR COMMA variableslist')
        def variablesList(p):
             if len(p) == 1:
                 return p[0], [p[0].value]
             else:
                result = p[2]
             return p[0], [p[0].value] + result[1]

        @self.pg.production('formula : OPEN_PAREN formula CLOSE_PAREN')
        def paren_formula(p):
            result = p[1]
            return p[0], result[1]

        @self.pg.error
        def error_handle(token):
            productions = self.state.splitlines()
            error = ''  

            if(productions == ['']):
                error = 'Nenhuma demonstração foi recebida, verifique a entrada.'
            if token.gettokentype() == '$end':
                error = 'Uma das definições não está completa, verifique se todas regras foram aplicadas corretamente. Lembre-se que uma regra de inferência sempre inicia com um número seguido de um . (linha de referência), tem uma fórmula e uma justificativa (premissa, hipóteses ou uma das regras de inferência com suas respectivas referências para fórmulas anteriores).'
            else:
                source_position = token.getsourcepos()
                error = 'Uma das definições não está completa, verifique se todas regras foram aplicadas corretamente.\nLembre-se que uma regra de inferência sempre inicia com um número seguido de um . (linha de referência), tem uma fórmula e uma justificativa (premissa, hipóteses ou uma das regras de inferência com suas respectivas referências para fórmulas anteriores).\n'
                error += "Erro de sintaxe:\n"
                error += productions[source_position.lineno - 1]
                string = '\n'
                for i in range(source_position.colno -1):
                    string += ' '
                string += '^'
                if token.gettokentype() == 'OUT':
                    string += ' Símbolo não pertence a linguagem.'
                error += string
                
            raise ValueError("@@"+error)

    def get_error(self, type_error, token_error, rule):
        return self.error_context.get_error(self.state, type_error, token_error, rule)
    
    def get_parser(self):
        return self.pg.build()

    def get_premisses(self):
      return self.symbol_table.getPremissesFormulas()

    def get_conclustion(self):
      return self.symbol_table.getConclusionFormula()

    def get_theorem(self):
      return self.symbol_table.getPremissesFormulas(), self.symbol_table.getConclusionFormula()

    def theorem_to_string(self,parentheses=False):
      return self.symbol_table.theoremToString(parentheses=parentheses)

    def theorem_to_latex(self,parentheses=False):
      return self.symbol_table.theoremToLatex(parentheses=parentheses)

    @staticmethod
    def getProof(input_text=''):
      lexer = Lexer().get_lexer()
      tokens = lexer.lex(input_text)

      pg = ParserNadia(state=input_text)
      pg.parse()
      parser = pg.get_parser()
      result = parser.parse(tokens)
      return result

    @staticmethod
    def toString(premisses,conclusion,parentheses=False):
      if (premisses==[]):
        return '|- '+conclusion.toString(parentheses=parentheses)
      else:
        return ", ".join(f.toString(parentheses=parentheses) for f in premisses)+' |- '+conclusion.toString(parentheses=parentheses)

    @staticmethod
    def toLatex(premisses,conclusion,parentheses=False):
      if (premisses==[]):
        return '\\vdash '+conclusion.toLatex(parentheses=parentheses)
      else:
        return ", ".join(f.toLatex(parentheses=parentheses) for f in premisses) +' \\vdash '+conclusion.toLatex(parentheses=parentheses)

def check_proof(input_proof, input_theorem=None, display_theorem=True, display_fitch=True, display_gentzen=True):
    try:
        result = ParserNadia.getProof(input_proof)
        r = ''

        if(result.errors==[]):
            s_theorem = ParserNadia.toString(result.premisses, result.conclusion)
            if input_theorem is not None: 
                premisses, conclusion = ParserTheorem.getTheorem(input_theorem)
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

