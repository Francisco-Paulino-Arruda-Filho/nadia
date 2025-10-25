from rply import ParserGenerator
from AtomFormula.AtomFormula import AtomFormula
from NegationFormula.NegationFormula import NegationFormula
from ParserInterface import ParserInterface
from PredicatedFormula.PredicatedFormula import PredicateFormula
from QuantifierFormula.ExistentialFormula import ExistentialFormula
from QuantifierFormula.UniversalFormula import UniversalFormula
from models import SymbolTable, constants

# Importações das classes de fórmula
from BinaryFormula.AndFormula import AndFormula
from BinaryFormula.OrFormula import OrFormula
from BinaryFormula.ImplicationFormula import ImplicationFormula
from BinaryFormula.BiImplicationFormula import BiImplicationFormula
from BinaryFormula.BinaryFormula import BinaryFormula

# Importações das definições de regras
from ast import (
    PremisseDef, HypothesisDef, HypothesisFirstOrderDef, WrongDef,
    ImplicationEliminationDef, ImplicationIntroductionDef, 
    DisjunctionIntroductionDef, AndIntroductionDef, AndEliminationDef,
    DisjunctionEliminationDef, NegationIntroductionDef, NegationEliminationDef,
    BottomDef, RaaDef, CopyDef, ForAllEliminationDef, ExistsIntroductionDef,
    ExistsEliminationtionDef, ForAllIntroductiontionDef
)

# Importação do Strategy Pattern (se estiver usando)
from models.natural_deduction_return import natural_deduction_return
from utils.limpaHipotese import limpaHipotese

class ParserNadia(ParserInterface):
    """
    Parser para demonstrações no estilo Fitch/Gentzen
    Suporta: premissas, hipóteses, regras de inferência, escopos, etc.
    """
    
    def __init__(self, state):
        super().__init__(state)
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            ['NUM', 'DOT', 'COMMA', 'OPEN_PAREN', 'CLOSE_PAREN', 'NOT', 'RAA',
             'AND', 'OR', 'OR_INTROD', 'OR_ELIM', 'BOTTOM','BOTTOM_ELIM', 'OPEN_BRACKET', 'AND_INTROD',
             'AND_ELIM', 'NEG_INTROD', 'NEG_ELIM', 'HYPOTHESIS', 'PREMISE', 'ATOM', 'CLOSE_BRACKET',
             'DASH', 'COPY', 'IMP_ELIM', 'IMPLIE', 'IMP_INTROD',
             'VAR', 'EXT', 'ALL', 'ALL_ELIM', 'EXT_INTROD', 'EXT_ELIM', 'ALL_INTROD'],
            # The precedence $\lnot,\forall,\exists,\land,\lor,\rightarrow,\leftrightarrow$
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
        self.deduction_result = natural_deduction_return()
        self._build_parser()

    def _build_parser(self):
        """Constrói todas as regras de produção do parser"""
        
        # Produção principal
        @self.pg.production('program : steps')
        def program(p):
            return self._handle_program(p)

        # Produções para sequência de passos
        @self.pg.production('steps : steps step')
        @self.pg.production('steps : step')
        def steps(p):
            return self._handle_steps(p)

        # Produções para diferentes tipos de passo
        @self.pg.production('step : NUM DOT formula PREMISE')
        def premise_step(p):
            return self._handle_premise(p)

        @self.pg.production('step : NUM DOT OPEN_BRACKET formula HYPOTHESIS')
        @self.pg.production('step : NUM DOT OPEN_BRACKET VAR')
        @self.pg.production('step : NUM DOT OPEN_BRACKET VAR formula HYPOTHESIS')
        def hypothesis_step(p):
            return self._handle_hypothesis(p)

        @self.pg.production('step : NUM DOT formula HYPOTHESIS')
        @self.pg.production('step : NUM DOT formula ATOM')
        @self.pg.production('step : NUM DOT OPEN_BRACKET formula ATOM')
        def wrong_pre_hip_step(p):
            return self._handle_wrong_pre_hip(p)

        # Produções para regras de inferência
        @self.pg.production('step : NUM DOT formula NEG_ELIM NUM COMMA NUM')
        def neg_elim_step(p):
            return self._handle_neg_elim(p)

        @self.pg.production('step : NUM DOT formula IMP_ELIM NUM COMMA NUM')
        def imp_elim_step(p):
            return self._handle_imp_elim(p)

        @self.pg.production('step : NUM DOT formula IMP_INTROD NUM DASH NUM')
        def imp_introd_step(p):
            return self._handle_imp_introd(p)

        @self.pg.production('step : NUM DOT formula OR_INTROD NUM')
        def or_introd_step(p):
            return self._handle_or_introd(p)

        @self.pg.production('step : NUM DOT formula AND_INTROD NUM COMMA NUM')
        def and_introd_step(p):
            return self._handle_and_introd(p)

        @self.pg.production('step : NUM DOT formula AND_ELIM NUM')
        def and_elim_step(p):
            return self._handle_and_elim(p)

        @self.pg.production('step : NUM DOT formula OR_ELIM NUM COMMA NUM DASH NUM COMMA NUM DASH NUM')
        def or_elim_step(p):
            return self._handle_or_elim(p)

        @self.pg.production('step : NUM DOT formula NEG_INTROD NUM DASH NUM')
        def neg_introd_step(p):
            return self._handle_neg_introd(p)

        @self.pg.production('step : NUM DOT formula BOTTOM_ELIM NUM')
        def bottom_step(p):
            return self._handle_bottom(p)

        @self.pg.production('step : NUM DOT formula RAA NUM DASH NUM')
        def raa_step(p):
            return self._handle_raa(p)

        @self.pg.production('step : NUM DOT formula COPY NUM')
        def copy_step(p):
            return self._handle_copy(p)

        @self.pg.production('step : CLOSE_BRACKET')
        def close_box_step(p):
            return self._handle_close_box(p)

        # Produções para lógica de primeira ordem
        @self.pg.production('step : NUM DOT formula ALL_ELIM NUM')
        def forall_elim_step(p):
            return self._handle_forall_elim(p)

        @self.pg.production('step : NUM DOT formula EXT_INTROD NUM')
        def exists_intro_step(p):
            return self._handle_exists_intro(p)

        @self.pg.production('step : NUM DOT formula EXT_ELIM NUM COMMA NUM DASH NUM')
        def exists_elim_step(p):
            return self._handle_exists_elim(p)

        @self.pg.production('step : NUM DOT formula ALL_INTROD NUM DASH NUM')
        def forall_intro_step(p):
            return self._handle_forall_intro(p)

        # Produções para fórmulas (reutilizadas dos outros parsers)
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
            return self._handle_formula(p)

        @self.pg.production('formula : OPEN_PAREN formula CLOSE_PAREN')
        def paren_formula(p):
            result = p[1]
            return p[0], result[1]

        @self.pg.production('variableslist : VAR')
        @self.pg.production('variableslist : VAR COMMA variableslist')
        def variablesList(p):
            return self._handle_variables_list(p)

        # Produções para erros de uso de conectivos
        @self.pg.production('step : NUM DOT formula IMP_ELIM NUM ')
        @self.pg.production('step : NUM DOT formula IMP_ELIM NUM DASH NUM')
        @self.pg.production('step : NUM DOT formula AND_INTROD NUM ')
        @self.pg.production('step : NUM DOT formula AND_INTROD NUM DASH NUM')
        @self.pg.production('step : NUM DOT formula NEG_ELIM NUM ')
        @self.pg.production('step : NUM DOT formula NEG_ELIM NUM DASH NUM')
        def wrong_connective_references(p):
            return self._handle_wrong_connective_references(p)

        @self.pg.production('step : NUM DOT formula AND_ELIM NUM COMMA NUM ')
        @self.pg.production('step : NUM DOT formula AND_ELIM NUM DASH NUM')
        def wrong_connective_reference(p):
            return self._handle_wrong_connective_reference(p)

        @self.pg.error
        def error_handle(token):
            self._handle_error(token)

    # Métodos de manipulação de produções
    def _handle_program(self, p):
        """Processa o programa principal"""
        self.symbol_table.set_lines_visible()
        self.verify_sequence_lines_error(self.deduction_result)
        self.check_is_closed_boxes_by_rule(self.deduction_result)

        rule_info = p[0]
        for i in rule_info:
            rule_line, formula_reference = rule_info[i]
            rule = self.symbol_table.get_rule(rule_line.value)
            
            # Avaliação das regras usando Strategy Pattern se disponível
            if hasattr(rule, 'evaluation'):
                rule.evaluation(self, self.deduction_result)
            elif isinstance(rule, (PremisseDef, HypothesisDef, HypothesisFirstOrderDef)):
                # Essas regras não precisam de avaliação
                pass

        if not self.has_error:
            self._generate_output(rule_info)
        
        self.result = self.deduction_result
        return self.deduction_result

    def _handle_steps(self, p):
        """Processa sequência de passos"""
        if len(p) == 1:
            result = p[0]
            return {result[0].value: result}
        else:
            result = p[1]
            p[0][result[0].value] = result
            return p[0]

    def _handle_premise(self, p):
        """Processa premissa"""
        formula_result = p[2]
        formula = formula_result[1]
        premisse = PremisseDef(p[0].value, formula)
        self.symbol_table.insert(premisse, p[0])
        self.box_latex += "{} & premissa\\\\\n".format(formula.toLatex())
        return p[0], formula_result[0]

    def _handle_hypothesis(self, p):
        """Processa hipótese"""
        formula_result = {}
        if len(p) == 4 and p[3].gettokentype() == 'VAR':
            variable = p[3].value
            self.symbol_table.add_scope(p[0].value, variable=variable)
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
            self.symbol_table.add_scope(p[0].value, variable=variable)
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
        if self.symbol_table.current_scope == "scope_0":
            self.has_error = True
            self.deduction_result.add_error(
                self.get_error(constants.HYPOTHESIS_WITHOUT_BOX, formula_result[0], hypothesis)
            )
        return p[0], formula_result[0]

    def _handle_wrong_pre_hip(self, p):
        """Processa uso incorreto de pre/hip"""
        self.has_error = True
        wrong_rule = WrongDef(p[0].value, p[-2])
        self.deduction_result.add_error(
            self.get_error(constants.INVALID_HIP_PRE_WRITE, p[-1], wrong_rule)
        )
        return p[0], p[-2]

    # Métodos para regras de inferência (padrão similar para todos)
    def _handle_neg_elim(self, p):
        formula_result = p[2]
        formula = formula_result[1]
        negationElimination = NegationEliminationDef(p[0].value, formula, p[4], p[6])
        self.symbol_table.insert(negationElimination, p[0])
        self.box_latex += "{} & $\lnot e$ {}, {}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
        return p[0], formula_result[0]

    def _handle_imp_elim(self, p):
        formula_result = p[2]
        formula = formula_result[1]
        implicationElimination = ImplicationEliminationDef(p[0].value, formula, p[4], p[6])
        self.symbol_table.insert(implicationElimination, p[0])
        self.box_latex += "{} & $\\rightarrow e$ {}, {}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
        return p[0], formula_result[0]

    def _handle_imp_introd(self, p):
        formula_result = p[2]
        formula = formula_result[1]
        implicationIntrod = ImplicationIntroductionDef(p[0].value, formula, p[4], p[6])
        self.symbol_table.insert(implicationIntrod, p[0])
        self.box_latex += "{} & $\\rightarrow i$ {}-{}\\\\\n".format(formula.toLatex(), p[4].value, p[6].value)
        return p[0], formula_result[0]

    # ... métodos similares para outras regras (_handle_or_introd, _handle_and_introd, etc.)

    def _handle_close_box(self, p):
        """Processa fechamento de caixa"""
        rule = self.symbol_table.get_last_rule_from_scope()
        if rule is None:
            self.has_error = True
            self.deduction_result.add_error(
                self.get_error(constants.BOX_MUST_BE_DISPOSED_BY_RULE, p[0], rule)
            )              
            return p[0], rule
        elif self.symbol_table.get_box_start():
            self.symbol_table.end_scope(rule.line)
            self.box_latex = self.box_latex[:-3] + '\n'
            self.box_latex += "\\end{subproof}\n"
        else:
            self.has_error = True
            self.deduction_result.add_error(
                self.get_error(constants.CLOSE_BRACKET_WITHOUT_BOX, p[0], rule)
            )
        token = p[0]
        token.value = rule.line
        return p[0], rule.formula

    def _handle_formula(self, p):
        """Processa fórmulas (reutilizado de FormulaParser)"""
        if len(p) < 3:
            return self._handle_simple_formula(p)
        elif len(p) == 4:
            return self._handle_predicate_formula(p)
        elif len(p) == 3:
            return self._handle_binary_formula(p)
        
        raise ValueError("Estrutura de fórmula inválida")

    def _handle_simple_formula(self, p):
        """Processa fórmulas simples"""
        token = p[0]
        
        if token.gettokentype() == 'ATOM':
            return token, AtomFormula(key=token.value)
        elif token.gettokentype() == 'BOTTOM':
            return token, AtomFormula(key=token.value)
        elif token.gettokentype() == 'NOT':
            result = p[1]
            return token, NegationFormula(formula=result[1])
        else:
            # Quantificadores
            if token.gettokentype() == 'EXT':
                var = token.value.split('E')[1]
                return token, ExistentialFormula(variable=var, formula=p[1][1])
            elif token.gettokentype() == 'ALL':
                var = token.value.split('A')[1]
                return token, UniversalFormula(variable=var, formula=p[1][1])
            
        raise ValueError(f"Tipo de token não reconhecido: {token.gettokentype()}")

    def _handle_predicate_formula(self, p):
        """Processa fórmulas predicadas"""
        varlist = p[2]
        return p[0], PredicateFormula(name=p[0].value, variables=varlist[1])

    def _handle_binary_formula(self, p):
        """Processa fórmulas binárias"""
        result1 = p[0]
        result2 = p[2]
        operator = p[1]
        
        operator_map = {
            '&': AndFormula,
            '|': OrFormula,
            '->': ImplicationFormula,
            '<->': BiImplicationFormula
        }
        
        formula_class = operator_map.get(operator.value)
        if formula_class:
            return result1[0], formula_class(left=result1[1], right=result2[1])
        else:
            return result1[0], BinaryFormula(
                key=operator.value, 
                left=result1[1], 
                right=result2[1]
            )

    def _handle_variables_list(self, p):
        """Processa lista de variáveis"""
        if len(p) == 1:
            return p[0], [p[0].value]
        else:
            result = p[2]
            return p[0], [p[0].value] + result[1]

    def _handle_wrong_connective_references(self, p):
        """Processa uso incorreto de referências"""
        self.has_error = True
        wrong_rule = WrongDef(p[0].value, p[2])
        self.deduction_result.add_error(
            self.get_error(constants.INVALID_RULE, p[3], wrong_rule)
        )
        return p[0], p[2]

    def _handle_wrong_connective_reference(self, p):
        """Processa uso incorreto de referência única"""
        self.has_error = True
        wrong_rule = WrongDef(p[0].value, p[2])
        self.deduction_result.add_error(
            self.get_error(constants.INVALID_RULE_ONE_REFERENCE, p[3], wrong_rule)
        )
        return p[0], p[2]

    def _handle_error(self, token):
        """Trata erros de parsing"""
        productions = self.state.splitlines()
        error = ''  

        if not productions or productions == ['']:
            error = 'Nenhuma demonstração foi recebida, verifique a entrada.'
        elif token.gettokentype() == '$end':
            error = 'Uma das definições não está completa, verifique se todas regras foram aplicadas corretamente.'
        else:
            source_position = token.getsourcepos()
            error = self._build_error_message(productions, source_position, token)
                
        raise ValueError(f"@@{error}")

    def _build_error_message(self, productions, source_position, token):
        """Constrói mensagem de erro detalhada"""
        error_lines = [
            'A definição da demonstração não está correta.',
            'Lembre-se que uma demonstração deve conter:',
            '  - Numeração sequencial das linhas',
            '  - Fórmulas válidas',
            '  - Justificativas corretas (pre, hip, ou regras de inferência)',
            '  - Referências a linhas anteriores quando necessário',
            '  - Escopos bem formados com [ e ]',
            '',
            'Erro de sintaxe:'
        ]
        
        error = '\n'.join(error_lines) + '\n'
        error += productions[source_position.lineno - 1] + '\n'
        
        # Adiciona indicador de posição
        error += ' ' * (source_position.colno - 1) + '^'
        
        if token.gettokentype() == 'OUT':
            error += ' Símbolo não pertence a linguagem.'
            
        return error

    def _generate_output(self, rule_info):
        """Gera saída LaTeX da demonstração"""
        latex = '\\['
        formula_reference = str(sorted(list(map(int, rule_info.keys())))[-1])
        rule = self.symbol_table.get_rule(rule_info[formula_reference][0].value)
        latex += rule.toLatex(self.symbol_table)
        latex += '\\]'
        
        # Limpa hipóteses e configura resultado
        limpaHipotese()
        self.deduction_result.premisses = self.symbol_table.getPremissesFormulas()
        self.deduction_result.conclusion = self.symbol_table.getConclusionFormula()
        self.deduction_result.fitch = self.box_latex[:-3] + '\n\\end{logicproof}'
        self.deduction_result.gentzen = latex + "\n"

    # Métodos de validação (mantidos da implementação original)
    def verify_sequence_lines_error(self, deduction_result):
        """Verifica sequência numérica das linhas"""
        productions = self.state.splitlines()
        i = 1
        for p in productions:
            x = p.split('.')[0]
            if x.isdigit():
                if int(x) != i: 
                    self.has_error = True
                    if i == 1: 
                        deduction_result.add_error(
                            f"{p}\n^, A numeração da linha {x} deveria ser {i}, pois a numeração da prova deve ser sequencial e iniciar em 1.\n"
                        )
                    else: 
                        deduction_result.add_error(
                            f"{p}\n^, A numeração da linha {x} deveria ser {i}, pois a numeração da prova deve ser sequencial.\n"
                        )
                    break
                i += 1

    def check_is_closed_boxes_by_rule(self, deduction_result):
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

    # Métodos da interface
    def parse(self):
        """
        Executa o parsing da demonstração
        
        Returns:
            natural_deduction_return: Resultado do parsing com premissas, conclusão e representações
            
        Raises:
            ValueError: Se houver erro de sintaxe na demonstração
        """
        return self._execute_parsing()

    def get_parser(self):
        """Retorna o parser construído"""
        return self.pg.build()

    def get_result(self):
        """Retorna o resultado do parsing"""
        return self.result

    # Métodos estáticos para compatibilidade
    @staticmethod
    def get_proof(input_text=''):
        """
        Método estático para compatibilidade com código existente
        
        Args:
            input_text: Texto da demonstração a ser parseada
            
        Returns:
            natural_deduction_return: Resultado do parsing
        """
        try:
            parser = ParserNadia(input_text)
            return parser.parse()
        except ValueError:
            result = natural_deduction_return()
            result.add_error("Erro no parsing da demonstração")
            return result

    @staticmethod
    def to_string(premisses, conclusion, parentheses=False):
        """Converte para string no formato padrão"""
        if not premisses:
            return '|- ' + conclusion.toString(parentheses=parentheses)
        else:
            premisses_str = ", ".join(
                f.toString(parentheses=parentheses) for f in premisses
            )
            return f"{premisses_str} |- {conclusion.toString(parentheses=parentheses)}"

    @staticmethod
    def to_latex(premisses, conclusion, parentheses=False):
        """Converte para LaTeX"""
        if not premisses:
            return '\\vdash ' + conclusion.toLatex(parentheses=parentheses)
        else:
            premisses_latex = ", ".join(
                f.toLatex(parentheses=parentheses) for f in premisses
            )
            return f"{premisses_latex} \\vdash {conclusion.toLatex(parentheses=parentheses)}"