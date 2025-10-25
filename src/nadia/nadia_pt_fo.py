## File symbol_table.py

from AtomFormula.AtomFormula import AtomFormula
from BinaryFormula.AndFormula import AndFormula
from BinaryFormula.BiImplicationFormula import BiImplicationFormula
from BinaryFormula.BinaryFormula import BinaryFormula
from BinaryFormula.ImplicationFormula import ImplicationFormula
from BinaryFormula.OrFormula import OrFormula
from NegationFormula.NegationFormula import NegationFormula
from PredicatedFormula.PredicatedFormula import PredicateFormula
from QuantifierFormula.ExistentialFormula import ExistentialFormula
from QuantifierFormula.UniversalFormula import UniversalFormula
from Strategy.RuleDefinition import RuleDefinition
from Strategy.PremisseDef import PremisseDef
from Strategy.HypothesisDef import HypothesisDef
import rply

from models import constants
from models.lexer import Lexer

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
      if (int(formula1_line) <= int(formula2_line)): return False
      current_scope = None
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['scope_{}'.format(i)]['rules']:
          if rule and (rule.line == formula1_line):
            current_scope = self.symbol_table['scope_{}'.format(i)]
            break
        if current_scope != None: break
      #Check if formula2_line in formula1_line scope 
      while current_scope != None:
        for rule in current_scope['rules']:
          if rule and (rule.line == formula2_line):
            return True
        current_scope = self.symbol_table[current_scope['parent']] if 'parent' in current_scope and current_scope['parent'] is not None else None
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
      variable = self.symbol_table[current_scope]['variable'] if current_scope!= None else None
      return not variable in self.get_free_variables_before_scope(line)

    def get_free_variables_before_scope(self, line):
      free_variables = set()
      #Find formula1_line scope.
      scope = self.find_scope(line)
      scope = self.symbol_table[scope]['parent'] if scope in self.symbol_table and self.symbol_table[scope]['parent'] is not None else None
      while scope != None:
          for rule in self.symbol_table[scope]['rules']:
            if (int(rule.line) < int(line)):
              free_variables = free_variables.union(rule.formula.free_variables())
            #Adds the variable for the universal introduction rule, i.e., if the line does not have a formula
            if ('start_line' in self.symbol_table[scope] and int(self.symbol_table[scope]['start_line'])<int(line) and self.symbol_table[scope]['variable']):
              free_variables = free_variables.union(set(self.symbol_table[scope]['variable']))
          scope = self.symbol_table[scope]['parent'] if self.symbol_table[scope]['parent'] is not None else None
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
        if current_scope != None: break
      #Check if formula2_line in formula1_line scope 
      while current_scope != None:
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
        if scope != None:
          return self.symbol_table[scope]['variable']
        #Verifica se a linha não tem fórmula (introdução do universal)
        for key, scope in self.symbol_table.items():
          if(int(scope['start_line'])==int(line)):
            return scope['variable']            
        return None

    def check_scope_is_valid(self, scope):
        current_scope = self.current_scope
        while current_scope != None:
            if current_scope == scope:
                return True
            current_scope = self.symbol_table[current_scope]['parent']
        return False

    def lookup_formula_by_line(self, symbol_line, line):
        scope = self.find_scope(symbol_line)
        while scope != None:
            for rule in self.symbol_table[scope]['rules']:
                if rule and rule.line == line:
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

    def get_box_end(self, line):
        scope = self.find_scope(line)
        if scope != 'scope_0':
            return self.symbol_table[scope]['end_line']
        return None        

    def get_first_rule_from_scope(self, line):
        scope = self.find_scope(line)
        if self.symbol_table[scope]['rules']==[]: return None
        return self.symbol_table[scope]['rules'][0]
    
    def get_last_rule_from_scope(self):
        if self.symbol_table[self.current_scope]['rules']==[]: return None
        return self.symbol_table[self.current_scope]['rules'][-1]

    def get_rule(self, rule_line):
        for key, scope in self.symbol_table.items():
            for key_rule, line in enumerate(scope['lines']):
                if line.value == rule_line:
                    return scope['rules'][key_rule]
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

## File analisys.py

from rply import ParserGenerator
import sys

from Strategy.RuleFactory import RuleFactory
from Strategy.RuleDefinition import RuleDefinition
from Strategy.RuleContext import RuleContext 

from Strategy.WrongDef import WrongDef
from Strategy.CopyDef import CopyDef
from Strategy.PremisseDef import PremisseDef
from Strategy.HypothesisDef import HypothesisDef
from Strategy.HypothesisFirstOrderDef import HypothesisFirstOrderDef
from Strategy.RaaDef import RaaDef
from Strategy.AndIntroductionDef import AndIntroductionDef
from Strategy.AndEliminationDef import AndEliminationDef
from Strategy.DisjunctionIntroductionDef import DisjunctionIntroductionDef
from Strategy.DisjunctionEliminationDef import DisjunctionEliminationDef
from Strategy.NegationIntroductionDef import NegationIntroductionDef
from Strategy.NegationEliminationDef import NegationEliminationDef
from Strategy.BottomDef import BottomDef
from Strategy.ForAllEliminationDef import ForAllEliminationDef
from Strategy.ForAllIntroductionDef import ForAllIntroductionDef
from Strategy.ExistsIntroductionDef import ExistsIntroductionDef
from Strategy.ExistsEliminationDef import ExistsEliminationDef
from Strategy.ImplicationIntroductionDef import ImplicationIntroductionDef
from Strategy.ImplicationEliminationDef import ImplicationEliminationDef
from Strategy.ExistsEliminationDef import ExistsEliminationDef  
from Strategy.ForAllIntroductionDef import ForAllIntroductionDef

import traceback


deduction_result = natural_deduction_return()

def value_error_handle(exctype, value, tb):
    deduction_result.add_error(str(value))
    traceback.print_tb(tb) 

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
            #The precedence $\lnot,\forall,\exists,\land,\lor,\rightarrow,\leftrightarrow$
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
        self.rule_factory.register_rules({
            'WRONG': WrongDef,
            'COPY': CopyDef,
            'PREMISE': PremisseDef, # Não será usada na validação principal, mas é bom ter
            'HYPOTHESIS': HypothesisDef, # Não será usada na validação principal, mas é bom ter
            'HYPOTHESIS_FO': HypothesisFirstOrderDef, # Não será usada na validação principal, mas é bom ter
            'RAA': RaaDef,
            'AND_INTRO': AndIntroductionDef,
            'AND_ELIM': AndEliminationDef,
            'OR_INTRO': DisjunctionIntroductionDef,
            'OR_ELIM': DisjunctionEliminationDef,
            'NEG_INTRO': NegationIntroductionDef,
            'NEG_ELIM': NegationEliminationDef,
            'BOTTOM_ELIM': BottomDef,
            'IMP_INTRO': ImplicationIntroductionDef,
            'IMP_ELIM': ImplicationEliminationDef,
            'ALL_ELIM': ForAllEliminationDef,
            'ALL_INTRO': ForAllIntroductionDef,
            'EXT_INTRO': ExistsIntroductionDef,
            'EXT_ELIM': ExistsEliminationDef,
        })


    def verify_sequence_lines_error(self, deduction_result):
        productions = self.state.splitlines()
        i = 1
        for p in productions:
          x = p.split('.')[0]
          if x.isdigit():
            if int(x)!=i: 
              self.has_error = True
              if(i==1): deduction_result.add_error("{}\n^, A numeração da linha {} deveria ser {}, pois a numeração da prova deve ser sequencial e iniciar em 1.\n".format(p,x,i))
              else: deduction_result.add_error("{}\n^, A numeração da linha {} deveria ser {}, pois a numeração da prova deve ser sequencial.\n".format(p,x,i))
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
        if (rule_next is None or ( not (isinstance(rule_next, NegationIntroductionDef) or isinstance(rule_next, RaaDef)
          or isinstance(rule_next, ImplicationIntroductionDef) or isinstance(rule_next, DisjunctionEliminationDef)
          or isinstance(rule_next, ExistsEliminationDef) or isinstance(rule_next, ForAllIntroductionDef)))):
          self.has_error = True
          begin_rule = current_scope["rules"][0]
          begin_token =current_scope["lines"][0]
          deduction_result.add_error(self.get_error(constants.BOX_MUST_BE_DISPOSED, begin_token, begin_rule))

    def check_line_reference_before_rule_error(self, deduction_result, rule):
      result = True
      if hasattr(rule, 'reference1'):
        if(int(rule.reference1.value) >= int(rule.line)):
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.REFERENCED_LINE_NOT_DEFINED, rule.reference1, rule))
            result = False
      if hasattr(rule, 'reference2'):
        if(int(rule.reference2.value) >= int(rule.line)):
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.REFERENCED_LINE_NOT_DEFINED, rule.reference2, rule))
            result = False
      if hasattr(rule, 'reference3'):
        if(int(rule.reference3.value) >= int(rule.line)):
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.REFERENCED_LINE_NOT_DEFINED, rule.reference3, rule))
            result = False
      if hasattr(rule, 'reference4'):
        if(int(rule.reference4.value) >= int(rule.line)):
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.REFERENCED_LINE_NOT_DEFINED, rule.reference4, rule))
            result = False
      if hasattr(rule, 'reference5'):
        if(int(rule.reference5.value) >= int(rule.line)):
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.REFERENCED_LINE_NOT_DEFINED, rule.reference5, rule))
            result = False
      return result

    def check_line_scope_reference_error(self, deduction_result, rule, reference1=False, reference2=False, reference3=False, reference4=False, reference5=False):
      result = True
      if reference1:
        if (self.symbol_table.lookup_formula_by_line(rule.line, rule.reference1.value) is None):
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.USING_DESCARTED_RULE, rule.reference1, rule))
            result = False
      if reference2:
        if (self.symbol_table.lookup_formula_by_line(rule.line, rule.reference2.value) is None):
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.USING_DESCARTED_RULE, rule.reference2, rule))
            result = False
      if reference3:
        if (self.symbol_table.lookup_formula_by_line(rule.line, rule.reference3.value) is None):
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.USING_DESCARTED_RULE, rule.reference3, rule))
            result = False
      if reference4:
        if (self.symbol_table.lookup_formula_by_line(rule.line, rule.reference4.value) is None):
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.USING_DESCARTED_RULE, rule.reference4, rule))
            result = False
      if reference5:
        if (self.symbol_table.lookup_formula_by_line(rule.line, rule.reference5.value) is None):
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.USING_DESCARTED_RULE, rule.reference5, rule))
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


    def get_error(self, message, token, rule):
        # Placeholder para a função get_error
        line_num = token.value if token else '?'
        return f"Erro na linha {rule.line} (referência {line_num}, regra {rule.get_name()}): {message}"
    
    def parse(self):
        deduction_result = natural_deduction_return()
        
        @self.pg.production('program : steps')
        def program(p):
            self.symbol_table.set_lines_visible()
            self.verify_sequence_lines_error(deduction_result)

            rule_info = p[0]
            # Validação: Itera sobre todas as regras na ordem de inserção
            for line_number in sorted(list(map(int, rule_info.keys()))):
                rule_line, _ = rule_info[str(line_number)]
                rule = self.symbol_table.get_rule(rule_line.value)
              
                
                # Regras que são RuleDefinition ou regras com um rule_type mapeado
                if isinstance(rule, RuleDefinition) and rule.rule_type in self.rule_factory.rules:
                    
                    # 1. Cria o RuleContext com os dados necessários
                    context = RuleContext(
                        line=rule.line,
                        formula=rule.formula,
                        references=rule.references,
                        symbol_table=self.symbol_table,
                        errors=deduction_result.errors,
                        hypothesis=hypothesis
                    )
                    
                    # 2. Obtém a classe Rule específica da Factory e chama validate
                    rule_strategy = self.rule_factory.get_rule(rule.rule_type)
                    if not rule_strategy().validate(context):
                        self.has_error = True
                
                # Regras especiais (Premisse/Hypothesis) que podem ter lógica de validação própria
                elif isinstance(rule, (PremisseDef, HypothesisDef, HypothesisFirstOrderDef, WrongDef)):
                    # A validação destas regras é geralmente trivial (Hypothesis/Premisse)
                    # ou já feita na inserção (WrongDef).
                    pass
                
                # Se for uma regra desconhecida ou não mapeada, marca erro.
                elif rule.rule_type not in ('PREMISE', 'HYPOTHESIS', 'HYPOTHESIS_FO', 'WRONG'):
                    deduction_result.add_error(f"Erro: Regra desconhecida ou não mapeada na Factory: {rule.rule_type}")
                    self.has_error = True


            if(not self.has_error):
                latex = '\\['
                # Obtém a última regra válida para o Gentzen
                last_line = str(sorted(list(map(int, rule_info.keys())))[-1])
                rule = self.symbol_table.get_rule(rule_info[last_line][0].value)
                
                # Cria um contexto para a notação LaTeX
                context_latex = RuleContext(
                    line=rule.line,
                    formula=rule.formula,
                    references=rule.references,
                    symbol_table=self.symbol_table,
                    errors=[],
                    hypothesis=hypothesis
                )

                # Regra final: obtém a notação LaTeX usando a Strategy correta
                if isinstance(rule, RuleDefinition) and rule.rule_type in self.rule_factory.rules:
                     rule_strategy = self.rule_factory.get_rule(rule.rule_type)
                     latex += rule_strategy().get_latex_notation(context_latex)
                else: # Regras base (Premissa/Hipótese) que não são RuleDefinition
                    latex += rule.get_latex_notation(context_latex)

                latex += '\\]'
                limpaHipotese()
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

        @self.pg.production('step : NUM DOT formula PREMISE')
        def Premisse(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Usa a classe Rule específica (PremisseDef), pois é uma regra base
            premisse = PremisseDef(p[0].value, formula)
            self.symbol_table.insert(premisse, p[0])
            self.box_latex += "{} & premissa\\\\\n".format(formula.toLatex())
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT OPEN_BRACKET formula HYPOTHESIS')
        @self.pg.production('step : NUM DOT OPEN_BRACKET VAR')
        @self.pg.production('step : NUM DOT OPEN_BRACKET VAR formula HYPOTHESIS')
        def Hypothesis(p):
            formula_result = {}
            hypothesis = None
            if len(p) == 4 and p[3].gettokentype() == 'VAR': # Regra FO: [x]
                variable = p[3].value
                self.symbol_table.add_scope(p[0].value,variable=variable)
                self.box_latex += "\\begin{subproof}\n"
                self.box_latex += "\\llap{$"+str(variable)+"\\quad$} &"+"\\\\\n"
                return p[0], None
            elif len(p) == 5: # Regra Prop.: [A]
                formula_result = p[3]
                self.symbol_table.add_scope(p[0].value)
                formula = formula_result[1]
                self.box_latex += "\\begin{subproof}\n"
                self.box_latex += "{} & hipótese\\\\\n".format(formula.toLatex())
                # Usa a classe Rule específica (HypothesisDef)
                hypothesis = HypothesisDef(p[0].value, formula)
            elif len(p) == 6: # Regra FO: [x] A
                variable = p[3].value
                formula_result = p[4]
                self.symbol_table.add_scope(p[0].value,variable=variable)
                formula = formula_result[1]
                self.box_latex += "\\begin{subproof}\n"
                self.box_latex += "\\llap{$"+str(variable)+"\\quad$}"+"{} & hipótese\\\\\n".format(formula.toLatex())
                # Usa a classe Rule específica (HypothesisFirstOrderDef)
                hypothesis = HypothesisFirstOrderDef(p[0].value, formula, variable) # Ajustando a ordem dos parâmetros se necessário

            self.symbol_table.insert(hypothesis, p[0])
            if(self.symbol_table.current_scope == "scope_0"):
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.HYPOTHESIS_WITHOUT_BOX, formula_result[0], hypothesis))
            return p[0], formula_result[0]


        @self.pg.production('step : NUM DOT formula HYPOTHESIS')
        @self.pg.production('step : NUM DOT formula ATOM')
        @self.pg.production('step : NUM DOT OPEN_BRACKET formula ATOM')
        def Wrong_pre_hip(p):
            self.has_error = True
            wrong_rule = WrongDef(p[0].value, p[-2])
            deduction_result.add_error(self.get_error(constants.INVALID_HIP_PRE_WRITE, p[-1], wrong_rule))
            return p[0], p[-2]

        @self.pg.production('step : NUM DOT formula PREMISE ATOM')
        @self.pg.production('step : NUM DOT formula HYPOTHESIS ATOM')
        @self.pg.production('step : NUM DOT OPEN_BRACKET formula HYPOTHESIS ATOM')
        def Wrong_pre_hip_excedent(p):
            self.has_error = True
            wrong_rule = WrongDef(p[0].value, p[-3])
            deduction_result.add_error(self.get_error(constants.EXCEDENT_HIP_PRE_WRITE, p[-1], wrong_rule))
            return p[0], p[-3]

        @self.pg.production('step : NUM DOT formula NEG_ELIM NUM COMMA NUM')
        def Neg_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Cria RuleDefinition com o tipo 'NEG_ELIM'
            rule_def = RuleDefinition(
                line=p[0].value,
                formula=formula,
                rule_type='NEG_ELIM',
                references=[p[4], p[6]]
            )
            self.symbol_table.insert(rule_def, p[0])
            self.box_latex += "{} & $\lnot e$ {}, {}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula IMP_ELIM NUM COMMA NUM')
        def Imp_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Cria RuleDefinition com o tipo 'IMP_ELIM'
            rule_def = RuleDefinition(
                line=p[0].value,
                formula=formula,
                rule_type='IMP_ELIM',
                references=[p[4], p[6]]
            )
            self.symbol_table.insert(rule_def, p[0])
            self.box_latex += "{} & $\\rightarrow e$ {}, {}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]
            
        @self.pg.production('step : NUM DOT formula IMP_INTROD NUM DASH NUM')
        def Imp_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Cria RuleDefinition com o tipo 'IMP_INTRO'
            rule_def = RuleDefinition(
                line=p[0].value,
                formula=formula,
                rule_type='IMP_INTRO',
                references=[p[4], p[6]]
            )
            self.symbol_table.insert(rule_def, p[0])
            self.box_latex += "{} & $\\rightarrow i$ {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula OR_INTROD NUM')
        def Or_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Cria RuleDefinition com o tipo 'OR_INTRO'
            rule_def = RuleDefinition(
                line=p[0].value,
                formula=formula,
                rule_type='OR_INTRO',
                references=[p[4]]
            )
            self.symbol_table.insert(rule_def, p[0])
            self.box_latex += "{} & $\\lor i$ {}\\\\\n".format(formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula AND_INTROD NUM COMMA NUM')
        def And_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Cria RuleDefinition com o tipo 'AND_INTRO'
            rule_def = RuleDefinition(
                line=p[0].value,
                formula=formula,
                rule_type='AND_INTRO',
                references=[p[4], p[6]]
            )
            self.symbol_table.insert(rule_def, p[0])
            self.box_latex += "{} & $\\land i$ {},{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula AND_ELIM NUM')
        def And_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Cria RuleDefinition com o tipo 'AND_ELIM'
            rule_def = RuleDefinition(
                line=p[0].value,
                formula=formula,
                rule_type='AND_ELIM',
                references=[p[4]]
            )
            self.symbol_table.insert(rule_def, p[0])
            self.box_latex += "{} & $\\land e$ {}\\\\\n".format(formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula NEG_INTROD NUM DASH NUM')
        def Neg_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Cria RuleDefinition com o tipo 'NEG_INTRO'
            rule_def = RuleDefinition(
                line=p[0].value,
                formula=formula,
                rule_type='NEG_INTRO',
                references=[p[4], p[6]]
            )
            self.symbol_table.insert(rule_def, p[0])
            self.box_latex += "{} & $\\lnot i$ {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula COPY NUM')
        def Copy(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Cria RuleDefinition com o tipo 'COPY'
            rule_def = RuleDefinition(
                line=p[0].value,
                formula=formula,
                rule_type='COPY',
                references=[p[4]]
            )
            self.symbol_table.insert(rule_def, p[0])
            self.box_latex += "{} & Copy {}\\\\\n".format(formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula RAA NUM DASH NUM')
        def Raa(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Cria RuleDefinition com o tipo 'RAA'
            rule_def = RuleDefinition(
                line=p[0].value,
                formula=formula,
                rule_type='RAA',
                references=[p[4], p[6]]
            )
            self.symbol_table.insert(rule_def, p[0])
            self.box_latex += "{} & RAA {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula BOTTOM_ELIM NUM')
        def Bottom_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Cria RuleDefinition com o tipo 'BOTTOM_ELIM'
            rule_def = RuleDefinition(
                line=p[0].value,
                formula=formula,
                rule_type='BOTTOM_ELIM',
                references=[p[4]]
            )
            self.symbol_table.insert(rule_def, p[0])
            self.box_latex += "{} & $\\bot e$ {}\\\\\n".format(formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula OR_ELIM NUM COMMA NUM DASH NUM COMMA NUM DASH NUM')
        def Or_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Cria RuleDefinition com o tipo 'OR_ELIM'
            rule_def = RuleDefinition(
                line=p[0].value,
                formula=formula,
                rule_type='OR_ELIM',
                references=[p[4], p[6], p[8], p[10], p[12]]
            )
            self.symbol_table.insert(rule_def, p[0])
            self.box_latex += "{} & $\\lor e$ {}, {}-{}, {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value, p[8].value, p[10].value, p[12].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula ALL_ELIM NUM')
        def All_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Cria RuleDefinition com o tipo 'ALL_ELIM'
            rule_def = RuleDefinition(
                line=p[0].value,
                formula=formula,
                rule_type='ALL_ELIM',
                references=[p[4]]
            )
            self.symbol_table.insert(rule_def, p[0])
            self.box_latex += "{} & $\\forall e$ {}\\\\\n".format(formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula ALL_INTROD NUM DASH NUM')
        def All_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Cria RuleDefinition com o tipo 'ALL_INTRO'
            rule_def = RuleDefinition(
                line=p[0].value,
                formula=formula,
                rule_type='ALL_INTRO',
                references=[p[4], p[6]]
            )
            self.symbol_table.insert(rule_def, p[0])
            self.box_latex += "{} & $\\forall i$ {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula EXT_INTROD NUM')
        def Ext_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Cria RuleDefinition com o tipo 'EXT_INTRO'
            rule_def = RuleDefinition(
                line=p[0].value,
                formula=formula,
                rule_type='EXT_INTRO',
                references=[p[4]]
            )
            self.symbol_table.insert(rule_def, p[0])
            self.box_latex += "{} & $\\exists i$ {}\\\\\n".format(formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula EXT_ELIM NUM COMMA NUM DASH NUM')
        def Ext_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            # Cria RuleDefinition com o tipo 'EXT_ELIM'
            rule_def = RuleDefinition(
                line=p[0].value,
                formula=formula,
                rule_type='EXT_ELIM',
                references=[p[4], p[6], p[8]]
            )
            self.symbol_table.insert(rule_def, p[0])
            self.box_latex += "{} & $\\exists e$ {}, {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value, p[8].value)
            return p[0], formula_result[0]


        @self.pg.production('formula : ATOM')
        @self.pg.production('formula : VAR')
        @self.pg.production('formula : OPEN_PAREN formula CLOSE_PAREN')
        @self.pg.production('formula : NOT formula')
        @self.pg.production('formula : formula AND formula')
        @self.pg.production('formula : formula OR formula')
        @self.pg.production('formula : formula IMPLIE formula')
        @self.pg.production('formula : ALL VAR formula')
        @self.pg.production('formula : EXT VAR formula')
        @self.pg.production('formula : ATOM OPEN_PAREN formula_list CLOSE_PAREN')
        @self.pg.production('formula : BOTTOM')
        def parse_formula(p):
            if len(p) == 1:
                if p[0].gettokentype() == 'ATOM':
                    return p[0], AtomFormula(p[0].value)
                elif p[0].gettokentype() == 'VAR':
                    # Variáveis soltas não são bem-formadas, mas mantido para parse
                    return p[0], AtomFormula(p[0].value)
                elif p[0].gettokentype() == 'BOTTOM':
                    return p[0], AtomFormula('@') # Assumindo @ para Bottom

            elif len(p) == 3 and p[0].gettokentype() == 'OPEN_PAREN':
                return p[0], p[1][1]

            elif len(p) == 2 and p[0].gettokentype() == 'NOT':
                return p[0], NegationFormula(p[1][1])

            elif len(p) == 3 and p[1].gettokentype() == 'AND':
                return p[0], AndFormula(p[0][1], p[2][1])
            elif len(p) == 3 and p[1].gettokentype() == 'OR':
                return p[0], OrFormula(p[0][1], p[2][1])
            elif len(p) == 3 and p[1].gettokentype() == 'IMPLIE':
                return p[0], ImplicationFormula(p[0][1], p[2][1])

            elif len(p) == 3 and p[0].gettokentype() == 'ALL':
                # ALL VAR formula
                return p[0], UniversalFormula(p[1].value, p[2][1])
            elif len(p) == 3 and p[0].gettokentype() == 'EXT':
                # EXT VAR formula
                return p[0], ExistentialFormula(p[1].value, p[2][1])

            elif len(p) == 4 and p[0].gettokentype() == 'ATOM':
                # Predicate (R(a, b))
                atom = p[0].value
                args = p[2][1]
                return p[0], PredicateFormula(atom, args)

        @self.pg.production('formula_list : formula COMMA formula_list')
        @self.pg.production('formula_list : formula')
        def parse_formula_list(p):
            if len(p) == 1:
                return p[0], [p[0][1]]
            else:
                return p[0], [p[0][1]] + p[2][1]

        self.parser = self.pg.build()
        
        try:
            return self.parser.parse(Lexer().lex(self.state))
        except rply.errors.LexingError as e:
            deduction_result.add_error("Erro de Lexer: Símbolo inesperado na linha/coluna {}.".format(e.source_pos))
            return deduction_result
        except rply.errors.ParsingError as e:
            deduction_result.add_error("Erro de Parsing: Sequência de tokens inválida próxima ao token {} na linha {}.".format(e.token.name, e.token.source_pos.lineno))
            return deduction_result
        except Exception as e:
            deduction_result.add_error(f"Erro inesperado: {str(e)}")
            return deduction_result


def check_proof(input_proof, input_theorem=None, display_theorem=True, display_fitch=True, display_gentzen=True):
    try:
        result = ParserNadia.getProof(input_proof)
        r = ''

        if(result.errors==[]):
            s_theorem = ParserNadia.toString(result.premisses, result.conclusion)
            if input_theorem!=None: 
                premisses, conclusion = ParserTheorem.getTheorem(input_theorem)
                if conclusion == None:
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



# PARSER DE UM TEOREMA

class ParserTheorem():
    def __init__(self, state):
        self.state = state
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            ['COMMA', 'OPEN_PAREN', 'CLOSE_PAREN', 'NOT',
             'AND', 'OR',  'BOTTOM','ATOM', 'IMPLIE', 'IFF',
             'VAR','EXT','ALL', 'V_DASH' ],
            #The precedence $\lnot,\forall,\exists,\land,\lor,\rightarrow,\leftrightarrow$
            precedence=[
                ('right', ['IFF']),
                ('right', ['IMPLIE']),
                ('right', ['OR']),
                ('right', ['AND']),
                ('right', ['EXT']),
                ('right', ['ALL']),
                ('right', ['NOT']),
            ]
        )

    def parse(self):
        @self.pg.production('program : formulaslist V_DASH formula')
        @self.pg.production('program : V_DASH formula')
        def program(p):
            if len(p) == 2:
              return [], p[1][1]
            else:
              return p[0][1], p[2][1]

        @self.pg.production('formula : EXT formula')
        @self.pg.production('formula : ALL formula')
        @self.pg.production('formula : formula OR formula')
        @self.pg.production('formula : formula AND formula')
        @self.pg.production('formula : formula IMPLIE formula')
        @self.pg.production('formula : formula IFF formula')
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
                elif( not type(p[0]) is tuple):
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
              name = p[0]
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
              elif(p[1].value=='<->'):
                return result1[0], BiImplicationFormula(left=result1[1], right=result2[1])
              else:
                return result1[0], BinaryFormula(key=p[1].value, left=result1[1], right=result2[1])

        @self.pg.production('formula : OPEN_PAREN formula CLOSE_PAREN')
        def paren_formula(p):
            result = p[1]
            return p[0], result[1]

        @self.pg.production('variableslist : VAR')
        @self.pg.production('variableslist : VAR COMMA variableslist')
        def variablesList(p):
             if len(p) == 1:
                 return p[0], [p[0].value]
             else:
                result = p[2]
             return p[0], [p[0].value] + result[1]

        @self.pg.production('formulaslist : formula')
        @self.pg.production('formulaslist : formula COMMA formulaslist')
        def formulasList(p):
             if len(p) == 1:
                 return p[0], [p[0][1]]
             else:
                result = p[2]
             return p[0], [p[0][1]] + result[1]


        @self.pg.error
        def error_handle(token):
            productions = self.state.splitlines()
            error = ''  

            if(productions == ['']):
                error = 'Nenhuma fórmula foi recebida, verifique a entrada.'
            if token.gettokentype() == '$end':
                error = 'Nenhuma fórmula foi recebida, verifique a entrada.'
            else:
                source_position = token.getsourcepos()
                error = 'A definição da fórmula não está correta, verifique se todas regras foram aplicadas corretamente.\nLembre-se que uma uma fórmula é definida pela seguinte BNF:\nF :== P | ~ P | P & Q | P | Q | P -> Q | P <-> Q | (P), onde P,Q são átomos.\n'
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
        productions = self.state.splitlines()
        column_error = token_error.getsourcepos().colno
        erro = "Erro de sintaxe na linha {}:\n".format(token_error.getsourcepos().lineno)
        erro += productions[token_error.getsourcepos().lineno-1] + "\n"
        for i in range(column_error-1):
            erro += ' '
#        if type_error == constants.REFERENCED_FORMULE_NONE:## REVER SE NAO EXCLUIR
#            erro += '^, A fórmula {} não foi definida anteriormente ou foi descartada.\n'.format(token_error.value)
        
        return erro
    
    def get_parser(self):
        return self.pg.build()
    
    @staticmethod
    def getTheorem(input_text=''):
        try:
          lexer = Lexer().get_lexer()
          tokens = lexer.lex(input_text)

          pg = ParserTheorem(state=input_text)
          pg.parse()
          parser = pg.get_parser()
          formulas, conclusion = parser.parse(tokens)
          return formulas, conclusion
        except ValueError:
            s = traceback.format_exc()
            #print (f'Erro ao fazer o parser da fórmula!')
            return [], None
        else:
            return [], None
            pass

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
   