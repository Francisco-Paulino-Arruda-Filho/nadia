import copy

from Strategy import ImplicationIntroductionDef
from ParserFactory.BaseParser import BaseParser
from constants import constants
from models.AndFormula import AndFormula
from models.AtomFormula import AtomFormula
from models.BinaryFormula import BinaryFormula
from models.ExistencialFormula import ExistentialFormula
from models.ImplicationFormula import ImplicationFormula
from models.NegationFormula import NegationFormula
from models.OrFormula import OrFormula
from models.UniversalFormula import UniversalFormula
from nadia.Lexer import Lexer
from nadia.nadia_pt_fo import AndEliminationDef, AndIntroductionDef, BottomDef, DisjunctionEliminationDef, DisjunctionIntroductionDef, ExistsEliminationtionDef, ExistsIntroductionDef, ForAllEliminationDef, ForAllIntroductiontionDef, HypothesisDef, HypothesisFirstOrderDef, ImplicationEliminationDef, NegationEliminationDef, NegationIntroductionDef, PredicateFormula, PremisseDef, RaaDef, SymbolTable, WrongDef, limpaHipotese, natural_deduction_return

class ParserNadia(BaseParser):
    def __init__(self, state):
        self.symbol_table = SymbolTable()
        self.box_latex = "\\begin{logicproof}{6}\n"
        self.has_error = False
        super().__init__(state)
    
    def get_tokens(self):
        """Implementação do Template Method - retorna a lista de tokens"""
        return ['NUM', 'DOT', 'COMMA', 'OPEN_PAREN', 'CLOSE_PAREN', 'NOT', 'RAA',
               'AND', 'OR', 'OR_INTROD', 'OR_ELIM', 'BOTTOM','BOTTOM_ELIM', 'OPEN_BRACKET', 'AND_INTROD',
               'AND_ELIM', 'NEG_INTROD', 'NEG_ELIM', 'HYPOTHESIS', 'PREMISE', 'ATOM', 'CLOSE_BRACKET',
               'DASH', 'COPY', 'IMP_ELIM', 'IMPLIE', 'IMP_INTROD',
               'VAR', 'EXT', 'ALL', 'ALL_ELIM', 'EXT_INTROD', 'EXT_ELIM', 'ALL_INTROD']
    
    def get_precedence(self):
        """Implementação do Template Method - retorna a precedência"""
        return [
            ('right', ['IMPLIE']),
            ('right', ['OR']),
            ('right', ['AND']),
            ('right', ['EXT']),
            ('right', ['ALL']),
            ('right', ['NOT']),
        ]

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
        if (rule_next is None or ( not (isinstance(rule_next, NegationIntroductionDef) or isinstance(rule_next, RaaDef)
          or isinstance(rule_next, ImplicationIntroductionDef) or isinstance(rule_next, DisjunctionEliminationDef)
          or isinstance(rule_next, ExistsEliminationtionDef) or isinstance(rule_next, ForAllIntroductiontionDef)))):
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
            deduction_result.add_error(self.get_error(constants.USING_DESCARTED_RULE, rule.reference3, rule))
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
          or isinstance(rule, ImplicationIntroductionDef) or isinstance(rule, ForAllIntroductiontionDef)):
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

        elif (isinstance(rule, ExistsEliminationtionDef)):
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
        """Implementação do Template Method - define as regras de parsing"""
        deduction_result = natural_deduction_return()
        
        @self.pg.production('program : steps')
        def program(p):
            self.symbol_table.set_lines_visible()
            self.verify_sequence_lines_error(deduction_result)
            self.check_is_closed_boxes_by_rule(deduction_result)

            rule_info = p[0]
            for i in rule_info:
                rule_line, formula_reference = rule_info[i]

                formula_reference = self.symbol_table.find_token(rule_line.value)

                rule = self.symbol_table.get_rule(rule_line.value)
                if(isinstance(rule, PremisseDef) ):
                    pass
                elif(isinstance(rule, HypothesisDef)):
                    pass
                elif(isinstance(rule, HypothesisFirstOrderDef)):
                    pass
                elif(isinstance(rule, NegationIntroductionDef)):
                    rule.evaluation(self, deduction_result)
                elif(isinstance(rule, NegationEliminationDef)):
                    rule.evaluation(self, deduction_result)
                elif(isinstance(rule, AndIntroductionDef)):
                    rule.evaluation(self, deduction_result)
                elif(isinstance(rule, AndEliminationDef)):
                    rule.evaluation(self, deduction_result)
                elif isinstance(rule, ImplicationIntroductionDef):
                    rule.evaluation(self, deduction_result)
                elif isinstance(rule, ImplicationEliminationDef):
                    rule.evaluation(self, deduction_result)
                elif(isinstance(rule, DisjunctionEliminationDef)):
                    rule.evaluation(self, deduction_result)
                elif(isinstance(rule, DisjunctionIntroductionDef)):
                    rule.evaluation(self, deduction_result)
                elif(isinstance(rule, RaaDef)):
                    rule.evaluation(self, deduction_result)
                elif(isinstance(rule, BottomDef)):
                    rule.evaluation(self, deduction_result)
                elif(isinstance(rule, ExistsIntroductionDef)):
                    rule.evaluation(self, deduction_result)
                elif(isinstance(rule, ExistsEliminationtionDef)):
                    rule.evaluation(self, deduction_result)
                elif(isinstance(rule, ForAllIntroductiontionDef)):
                    rule.evaluation(self, deduction_result)
                elif(isinstance(rule, ForAllEliminationDef)):
                    rule.evaluation(self, deduction_result)

            if(not self.has_error):
                latex = '\\['
                formula_reference = str(sorted(list(map(int, rule_info.keys())))[-1])
                rule = self.symbol_table.get_rule(rule_info[formula_reference][0].value)
                latex += rule.toLatex(self.symbol_table)
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
            premisse = PremisseDef(p[0].value, formula)
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
                hypothesis = HypothesisDef(p[0].value, formula)
            elif len(p) == 6:
                variable = p[3].value
                formula_result = p[4]
                self.symbol_table.add_scope(p[0].value,variable=variable)
                formula = formula_result[1]
                self.box_latex += "\\begin{subproof}\n"
                self.box_latex += "\\llap{$"+str(variable)+"\\quad$}"+"{} & hipótese\\\\\n".format(formula.toLatex())
                hypothesis = HypothesisFirstOrderDef(p[0].value, variable, formula)
            elif len(p) == 4 and p[3].gettokentype() != 'VAR':
                formula_result = p[2]
                formula = formula_result[1]
                self.box_latex += "{} & hipótese\\\\\n".format(formula.toLatex())
                hypothesis = HypothesisDef(p[0].value, formula)

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

        @self.pg.production('step : NUM DOT formula NEG_ELIM NUM COMMA NUM')
        def Neg_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            negationElimination = NegationEliminationDef(p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(negationElimination, p[0])
            self.box_latex += "{} & $\lnot e$ {}, {}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula IMP_ELIM NUM COMMA NUM')
        def Imp_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            implicationElimination = ImplicationEliminationDef(p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(implicationElimination, p[0])
            self.box_latex += "{} & $\\rightarrow e$ {}, {}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]
            
        @self.pg.production('step : NUM DOT formula IMP_INTROD NUM DASH NUM')
        def Imp_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            implicationIntrod = ImplicationIntroductionDef(p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(implicationIntrod, p[0])
            self.box_latex += "{} & $\\rightarrow i$ {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula OR_INTROD NUM')
        def Or_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            disjunctionIntrod = DisjunctionIntroductionDef(p[0].value, formula, p[4])
            self.symbol_table.insert(disjunctionIntrod, p[0])
            self.box_latex += "{} & $\\lor i$ {}\\\\\n".format(formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula AND_INTROD NUM COMMA NUM')
        def And_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            andIntrod = AndIntroductionDef(p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(andIntrod, p[0])
            self.box_latex += "{} & $\\land i$ {},{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
                
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula AND_ELIM NUM')
        def And_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            andElim = AndEliminationDef(p[0].value, formula, p[4])
            self.symbol_table.insert(andElim, p[0])
            self.box_latex += "{} & $\\land e$ {}\\\\\n".format(formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula OR_ELIM NUM COMMA NUM DASH NUM COMMA NUM DASH NUM')
        def Or_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            orElim = DisjunctionEliminationDef(p[0].value, formula, p[4], p[6], p[8], p[10], p[12])
            self.symbol_table.insert(orElim, p[0])
            self.box_latex += "{} & $\\lor e$ {}, {}-{}, {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value, p[8].value, p[10].value, p[12].value)
            return p[0], formula_result[0]
        
        @self.pg.production('step : NUM DOT formula NEG_INTROD NUM DASH NUM')
        def Neg_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            negationIntrod = NegationIntroductionDef(p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(negationIntrod, p[0])
            self.box_latex += "{} & $\lnot i$ {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula BOTTOM_ELIM NUM')
        def Bottom(p):
            formula_result = p[2]
            formula = formula_result[1]
            bottom = BottomDef(p[0].value, formula, p[4])
            self.symbol_table.insert(bottom, p[0])
            self.box_latex += "{} & $\\bot e$ {}\\\\\n".format(formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula RAA NUM DASH NUM')
        def Raa(p):
            formula_result = p[2]
            formula = formula_result[1]
            raa = RaaDef(p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(raa, p[0])
            self.box_latex += "{} & raa {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]
        
        @self.pg.production('step : NUM DOT formula COPY NUM')
        def Copy(p):
            copied_scope = self.symbol_table.find_scope(p[4].value)
            if self.symbol_table.check_scope_is_valid(copied_scope):
                line = p[4].value
                formula_result = p[2]
                rule = copy.deepcopy(self.symbol_table.get_rule(line))
                rule.is_copied = True
                if(rule is not None):
                    if isinstance(rule, HypothesisDef):
                        rule.copied = rule.line
                    formula = formula_result[1]
                    rule.line = p[0].value 
                    if(rule.formula != formula):
                        formula_diff = rule.formula
                        rule.formula = formula
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.COPY_DIFFERENT_FORMULE, formula_result[0], rule))
                        rule.formula = formula_diff
                    self.box_latex += "{} & copie {}\\\\\n".format(formula.toLatex(), p[4].value)
                else:
                    self.has_error = True
                    deduction_result.add_error(self.get_error(constants.NONE_COPY, p[4], rule))
                self.symbol_table.insert(rule, p[0])
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
            elif(self.symbol_table.get_box_start()):
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
          forAllElimination = ForAllEliminationDef(p[0].value, formula, p[4])
          self.symbol_table.insert(forAllElimination, p[0])
          self.box_latex += "{} & $\\forall e$ {}\\\\\n".format(formula.toLatex(), p[4].value)
          return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula EXT_INTROD NUM')
        def Exists_intro(p):
          formula_result = p[2]
          formula = formula_result[1]
          existsIntroduction = ExistsIntroductionDef(p[0].value, formula, p[4])
          self.symbol_table.insert(existsIntroduction, p[0])
          self.box_latex += "{} & $\\exists i$ {}\\\\\n".format(formula.toLatex(), p[4].value)
          return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula EXT_ELIM NUM COMMA NUM DASH NUM')
        def Exists_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            existsElim = ExistsEliminationtionDef(p[0].value, formula, p[4], p[6], p[8])
            self.symbol_table.insert(existsElim, p[0])
            self.box_latex += "{} & $\\exists e$ {},{}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value, p[8].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula ALL_INTROD NUM DASH NUM')
        def For_all_intro(p):
            formula_result = p[2]
            formula = formula_result[1]
            allIntrod = ForAllIntroductiontionDef(p[0].value, formula, p[4], p[6])
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
            wrong_rule = WrongDef(p[0].value, p[2])
            deduction_result.add_error(self.get_error(constants.INVALID_RULE, p[3], wrong_rule))
            return p[0], p[2]

        @self.pg.production('step : NUM DOT formula AND_ELIM NUM COMMA NUM ')
        @self.pg.production('step : NUM DOT formula AND_ELIM NUM DASH NUM')
        def Wrong_use_conective_reference(p):
            self.has_error = True
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
        productions = self.state.splitlines()
        column_error = token_error.getsourcepos().colno
        erro = "Erro de sintaxe na linha {}:\n".format(token_error.getsourcepos().lineno)
        erro += productions[token_error.getsourcepos().lineno-1] + "\n"
        for i in range(column_error-1):
            erro += ' '
        if type_error == constants.REFERENCED_FORMULE_NONE:## REVER SE NAO EXCLUIR
            erro += '^, A fórmula {} não foi definida anteriormente ou foi descartada.\n'.format(token_error.value)
        elif type_error == constants.INVALID_RESULT:
            erro += "^, A fórmula {} não é um resultado válido para esta regra.".format(rule.formula.toString())
        elif type_error == constants.INVALID_HYPOTHESIS:
            erro += "^, A hipótese da linha {} não corresponde a hipótese esperada para a fórmula da conclusão desta regra.".format(token_error.value)
        elif type_error == constants.INVALID_BOX_RESULT:
            erro += "^, A fórmula da linha {} não corresponde a conclusão esperada desta caixa para esta regra.".format(token_error.value)
        elif type_error == constants.UNEXPECT_RESULT:
            erro += "^, A fórmula {} não é um resultado válido para a regra aplicada.".format(rule.formula.toString())
        elif type_error == constants.IS_NOT_DISJUNCTION:
            erro += "^, A fórmula referenciada na linha {} não é disjunção.".format(token_error.value)
        elif type_error == constants.IS_NOT_CONJUNCTION:
            erro += "^, A fórmula referenciada na linha {} não é conjunção.".format(token_error.value)
        elif type_error == constants.IS_NOT_IMPLICATION:
            erro += "^, A fórmula referenciada na linha {} não é implicação.".format(token_error.value)
        elif type_error == constants.IS_NOT_BOTTOM:
            erro += "^, A fórmula referenciada na linha {} deveria ser @.".format(token_error.value)
        elif type_error == constants.INVALID_NEGATION:
            erro += "^, Nenhuma das fórmulas referencias pelas linhas é a negação da outra fórmula."
        elif type_error == constants.INVALID_LEFT_CONJUNCTION:
            erro += "^, A fórmula à esquerda fórmula da conclusão não é demonstrada por nenhuma das linhas referenciadas nesta regra."
        elif type_error == constants.INVALID_RIGHT_CONJUNCTION:
            erro += "^, A fórmula à direita da fórmula da conclusão não é demonstrada por nenhuma das linhas referenciadas nesta regra."
        elif type_error == constants.INVALID_LEFT_OR_RIGHT_DISJUNCTION:
            erro += "^, A fórmula à direita ou à equerda da fórmula da conclusão deve ser a mesma da fórmula referencia na linha {}.".format(token_error.value)
        elif type_error == constants.INVALID_LEFT_OR_RIGHT_CONJUNCTION:
            erro += "^, A fórmula à direita ou à equerda da fórmula da linha {} deve ser a mesma da fórmula da conclusão da regra.".format(token_error.value)
        elif type_error == constants.NONE_COPY:
            erro += "^, A Fórmula referenciada para cópia não existe."
        elif type_error == constants.COPY_DIFFERENT_FORMULE:
            erro += "^, A Fórmula referenciada para cópia é diferente da definida para essa regra."
        elif type_error == constants.INVALID_HIP_PRE_WRITE:
            erro += "^, uma hipótese só pode ser usado no início de uma caixa e é introduzida apenas por uma regra de inferência."
        elif type_error == constants.INVALID_RULE:
            erro += "^, a regra {} deve ter duas referências separadas por vírgula.".format(token_error.value)
        elif type_error == constants.INVALID_RULE_ONE_REFERENCE:
            erro += "^, a regra {} deve ter uma única referência.".format(token_error.value)
        elif type_error == constants.EXCEDENT_HIP_PRE_WRITE:
            erro += "^, Não é esperado texto depois de pre."
        elif type_error == constants.USING_DESCARTED_RULE:
            erro += "^, a referência a fórmula da linha {} não pode ser utilizada, pois esta fórmula já foi descartada.".format(token_error.value)
        elif type_error == constants.REFERENCED_LINE_NOT_DEFINED:
            erro += "^, a referência a fórmula da linha {} não pode ser utilizada, pois todas as referências devem ocorrer antes desta regra.".format(token_error.value)
        elif type_error == constants.INVALID_SCOPE_DELIMITER:
            erro += "^, esta não é uma caixa (escopo) válida."      
        elif type_error == constants.HYPOTHESIS_WITHOUT_BOX:
            erro += "^, A hipótese definida não está dentro de uma caixa."
        elif type_error == constants.CLOSE_BRACKET_WITHOUT_BOX:
            erro += "^, Fechamento de caixa sem caixa aberta."
        elif type_error == constants.HYPOTHESIS_WITHOUT_CLOSED_BOX:
            erro += "^, É necessário fechar o escopo desta caixa."
        elif type_error == constants.BOX_MUST_BE_DISPOSED:
            erro += "^, A hipótese que foi introduzida por essa caixa dever ser descartada pela regra que a introduziu em linha imediatamente posterior ao fechamento desta caixa."
        elif type_error == constants.BOX_MUST_BE_DISPOSED_BY_RULE:
            erro += "^, Esta caixa dever ser fechada em linha imediatamente posterior pela regra que a introduziu."
        elif type_error == constants.INVALID_SUBSTITUTION_UNIVERSAL:
            erro += "^, A fórmula {} não é uma substituição válida da fórmula universal refenciada na linha {}.".format(rule.formula.toString(), rule.reference1.value)
        elif type_error == constants.INVALID_CONCLUSION_EXISTENTIAL_LAST_RULE:
            erro += "^, A formula da conclusão desta regra deve ser a mesma fórmula refenciada na linha {}.".format(token_error.value)
        elif type_error == constants.INVALID_CONCLUSION_UNIVERSAL_LAST_RULE:
            erro += "^, A formula da conclusão desta regra deve ser a quantificação universal da fórmula refenciada na linha {} com a variável definida neste escopo.".format(token_error.value)
        elif type_error == constants.INVALID_UNIVERSAL_FORMULA:
            erro += "^, A fórmula referenciada na regra do universal não é uma fórmula do tipo universal."
        elif type_error == constants.INVALID_SUBSTITUTION_EXISTENTIAL:
            erro += "^, A fórmula {} não é uma substituição válida da fórmula existencial refenciada na linha {}.".format(rule.formula.toString(), rule.reference1.value)
        elif type_error == constants.VARIABLE_IS_NOT_FRESH_VARIABLE:
            erro += "^, A variável utilizada na linha {} é uma variável livre de uma fórmula definida anteriormente e, portanto, não pode ser utilizada nesta regra.".format(token_error.value)
        elif type_error == constants.BOX_MUST_HAVE_A_VARIABLE:
            erro += "^, A caixa que inicia na linha {} deve iniciar com uma variável para esta regra.".format(token_error.value) 
        elif type_error == constants.BOX_MUST_HAVE_ONLY_A_VARIABLE:
            erro += "^, A caixa que inicia na linha {} não tem hipótese. A caixa deve iniciar com uma variável apenas para a regra da introdução do universal.".format(token_error.value) 
        elif type_error == constants.INVALID_CONCLUSION_EXISTENTIAL:
            erro += "^, A variável utilizada na conclusão dessa regra não pode ser a variável utilizada na caixa que inicia na linha {}.".format(token_error.value)
        elif type_error == constants.INVALID_CONCLUSION_UNIVERSAL:
            erro += "^, A variável utilizada na caixa que inicia na linha {} não pode ocorrer como variável livre na conclusão da fórmula e, portanto, não pode ser utilizada nesta regra.".format(token_error.value)
        
        return erro

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