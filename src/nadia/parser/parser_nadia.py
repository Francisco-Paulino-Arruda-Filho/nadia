

import copy
from rply import ParserGenerator
from AtomFormula.AtomFormula import AtomFormula
from BinaryFormula.AndFormula import AndFormula
from BinaryFormula.BinaryFormula import BinaryFormula
from BinaryFormula.ImplicationFormula import ImplicationFormula
from BinaryFormula.OrFormula import OrFormula
from Factory.RuleFactory import RuleFactory
from NegationFormula.NegationFormula import NegationFormula
from PredicatedFormula.PredicatedFormula import PredicateFormula
from QuantifierFormula.ExistentialFormula import ExistentialFormula
from QuantifierFormula.UniversalFormula import UniversalFormula
from nadia.parser.natural_deduction_return import natural_deduction_return
from nadia.parser.symbol_table import SymbolTable
from nadia.validators.disjunction_elimination_scope_checker import DisjunctionEliminationScopeChecker
from nadia.validators.exists_elimination_scope_checker import ExistsEliminationScopeChecker
from nadia.validators.standard_scope_checker import StandardScopeChecker
from utils.HypothesisManager import HypothesisManager
from models.constants import constants
from nadia.Lexer.lexer import Lexer
from nadia.errors.error_strategy import ErrorContext


class ParserNadia():
    def __init__(self, state):
        self.state = state

        self._scope_checker_map = {
            'NegationIntroductionDef': StandardScopeChecker(self),
            'RaaDef': StandardScopeChecker(self),
            'ImplicationIntroductionDef': StandardScopeChecker(self),
            'ForAllIntroductionDef': StandardScopeChecker(self),
            'ExistsEliminationDef': ExistsEliminationScopeChecker(self),
            'DisjunctionEliminationDef': DisjunctionEliminationScopeChecker(self),
        }

        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            ['NUM', 'DOT', 'COMMA', 'OPEN_PAREN', 'CLOSE_PAREN', 'NOT', 'RAA',
             'AND', 'OR', 'OR_INTROD', 'OR_ELIM', 'BOTTOM', 'BOTTOM_ELIM', 'OPEN_BRACKET', 'AND_INTROD',
             'AND_ELIM', 'NEG_INTROD', 'NEG_ELIM', 'HYPOTHESIS', 'PREMISE', 'ATOM', 'CLOSE_BRACKET',
             'DASH', 'COPY', 'IMP_ELIM', 'IMPLIE', 'IMP_INTROD',
             'VAR', 'EXT', 'ALL', 'ALL_ELIM', 'EXT_INTROD', 'EXT_ELIM', 'ALL_INTROD'],
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
                if int(x) != i:
                    self.has_error = True
                    if (i == 1):
                        deduction_result.add_error(
                            "{}\n^, A numeração da linha {} deveria ser {}, pois a numeração da prova deve ser sequencial e iniciar em 1.\n".format(p, x, i))
                    else:
                        deduction_result.add_error(
                            "{}\n^, A numeração da linha {} deveria ser {}, pois a numeração da prova deve ser sequencial.\n".format(p, x, i))
                    break
                i += 1

    def check_is_closed_boxes_by_rule(self, deduction_result):
        current_scope = None
        for i in range(1, len(self.symbol_table.symbol_table)):
            current_scope = self.symbol_table.symbol_table['scope_{}'.format(
                i)]
            current_scope_parent = self.symbol_table.symbol_table[current_scope['parent']
                                                                  ] if current_scope['parent'] else None
            if (current_scope_parent is None):
                self.has_error = True
                deduction_result.add_error(
                    "Erro no escopo da demontração: escopo pai não encontrado.")
            rule_next = None
            for rule in current_scope_parent['rules']:
                if (int(rule.line) > int(current_scope['end_line'])):
                    rule_next = rule
                    break
            # Verificação genérica usando RuleBase
            if (rule_next is None or not hasattr(rule_next, 'evaluation')):
                self.has_error = True
                begin_rule = current_scope["rules"][0]
                begin_token = current_scope["lines"][0]
                deduction_result.add_error(self.get_error(
                    constants.BOX_MUST_BE_DISPOSED, begin_token, begin_rule))

    def check_line_reference_before_rule_error(self, deduction_result, rule):
        result = True
        for i in range(1, 6):
            ref_attr = f'reference{i}'
            if hasattr(rule, ref_attr):
                ref = getattr(rule, ref_attr)
                if ref and int(ref.value) >= int(rule.line):
                    self.has_error = True
                    deduction_result.add_error(self.get_error(
                        constants.REFERENCED_LINE_NOT_DEFINED, ref, rule))
                    result = False
        return result

    def check_line_scope_reference_error(self, deduction_result, rule, **references):
        result = True
        for ref_name, should_check in references.items():
            if should_check and hasattr(rule, ref_name):
                ref = getattr(rule, ref_name)
                if self.symbol_table.lookup_formula_by_line(rule.line, ref.value) is None:
                    self.has_error = True
                    deduction_result.add_error(self.get_error(
                        constants.USING_DESCARTED_RULE, ref, rule))
                    result = False
        return result

    def _get_scope_checker(self, rule):
        rule_type_str = rule.__class__.__name__
        return self._scope_checker_map.get(rule_type_str, None)

    def check_scope_reference_error(self, deduction_result, rule):
        checker = self._get_scope_checker(rule)

        # 2. Se um verificador foi encontrado, executa o Template Method dele
        if checker:
            return checker.check(rule, deduction_result)

        return True

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
                formula_reference = str(
                    sorted(list(map(int, rule_info.keys())))[-1])
                rule = self.symbol_table.get_rule(
                    rule_info[formula_reference][0].value)
                latex += rule.toLatex(self.symbol_table)
                latex += '\\]'

                HypothesisManager.reset()  # Usando HypothesisManager em vez de limpaHipotese

                deduction_result.premisses = self.symbol_table.getPremissesFormulas()
                deduction_result.conclusion = self.symbol_table.getConclusionFormula()
                deduction_result.fitch = self.box_latex[:-
                                                        3] + '\n\end{logicproof}'
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
            premisse = self.rule_factory.create_rule(
                'premise', p[0].value, formula)
            self.symbol_table.insert(premisse, p[0])
            self.box_latex += "{} & premissa\\\\\n".format(formula.toLatex())
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT OPEN_BRACKET formula HYPOTHESIS')
        @self.pg.production('step : NUM DOT OPEN_BRACKET VAR')
        @self.pg.production('step : NUM DOT OPEN_BRACKET VAR formula HYPOTHESIS')
        def Hypothesis(p):
            formula_result = {}
            hypothesis = None
            if len(p) == 4 and p[3].gettokentype() == 'VAR':
                variable = p[3].value
                self.symbol_table.add_scope(p[0].value, variable=variable)
                self.box_latex += "\\begin{subproof}\n"
                self.box_latex += "\\llap{$" + \
                    str(variable)+"\\quad$} &"+"\\\\\n"
                return p[0], None
            elif len(p) == 5:
                formula_result = p[3]
                self.symbol_table.add_scope(p[0].value)
                formula = formula_result[1]
                self.box_latex += "\\begin{subproof}\n"
                self.box_latex += "{} & hipótese\\\\\n".format(
                    formula.toLatex())
                hypothesis = self.rule_factory.create_rule(
                    'hypothesis', p[0].value, formula)
            elif len(p) == 6:
                variable = p[3].value
                formula_result = p[4]
                self.symbol_table.add_scope(p[0].value, variable=variable)
                formula = formula_result[1]
                self.box_latex += "\\begin{subproof}\n"
                self.box_latex += "\\llap{$"+str(variable)+"\\quad$}" + \
                    "{} & hipótese\\\\\n".format(formula.toLatex())
                hypothesis = self.rule_factory.create_rule(
                    'hypothesis_first_order', p[0].value, formula, variable)
            elif len(p) == 4 and p[3].gettokentype() != 'VAR':
                formula_result = p[2]
                formula = formula_result[1]
                self.box_latex += "{} & hipótese\\\\\n".format(
                    formula.toLatex())
                hypothesis = self.rule_factory.create_rule(
                    'hypothesis', p[0].value, formula)

            if self.symbol_table.current_scope == "scope_0":
                self.has_error = True
                deduction_result.add_error(self.get_error(
                    constants.HYPOTHESIS_WITHOUT_BOX, formula_result[0], hypothesis))
                return p[0], formula_result[0] if 'formula_result' in locals() and formula_result else None

            self.symbol_table.insert(hypothesis, p[0])
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula HYPOTHESIS')
        @self.pg.production('step : NUM DOT formula ATOM')
        @self.pg.production('step : NUM DOT OPEN_BRACKET formula ATOM')
        def Wrong_pre_hip(p):
            self.has_error = True
            wrong_rule = RuleFactory._create_wrong(p[0].value, p[-2])
            deduction_result.add_error(self.get_error(
                constants.INVALID_HIP_PRE_WRITE, p[-1], wrong_rule))
            return p[0], p[-2]

        @self.pg.production('step : NUM DOT formula NEG_ELIM NUM COMMA NUM')
        def Neg_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            negationElimination = self.rule_factory.create_rule(
                'negation_elimination', p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(negationElimination, p[0])
            self.box_latex += "{} & $\lnot e$ {}, {}\\\\\n".format(
                formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula IMP_ELIM NUM COMMA NUM')
        def Imp_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            implicationElimination = self.rule_factory.create_rule(
                'implication_elimination', p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(implicationElimination, p[0])
            self.box_latex += "{} & $\\rightarrow e$ {}, {}\\\\\n".format(
                formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula IMP_INTROD NUM DASH NUM')
        def Imp_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            implicationIntrod = self.rule_factory.create_rule(
                'implication_introduction', p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(implicationIntrod, p[0])
            self.box_latex += "{} & $\\rightarrow i$ {}-{}\\\\\n".format(
                formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula OR_INTROD NUM')
        def Or_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            disjunctionIntrod = self.rule_factory.create_rule(
                'disjunction_introduction', p[0].value, formula, p[4])
            self.symbol_table.insert(disjunctionIntrod, p[0])
            self.box_latex += "{} & $\\lor i$ {}\\\\\n".format(
                formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula AND_INTROD NUM COMMA NUM')
        def And_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            andIntrod = self.rule_factory.create_rule(
                'and_introduction', p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(andIntrod, p[0])
            self.box_latex += "{} & $\\land i$ {},{}\\\\\n".format(
                formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula AND_ELIM NUM')
        def And_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            andElim = self.rule_factory.create_rule(
                'and_elimination', p[0].value, formula, p[4])
            self.symbol_table.insert(andElim, p[0])
            self.box_latex += "{} & $\\land e$ {}\\\\\n".format(
                formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula OR_ELIM NUM COMMA NUM DASH NUM COMMA NUM DASH NUM')
        def Or_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            orElim = self.rule_factory.create_rule(
                'disjunction_elimination', p[0].value, formula, p[4], p[6], p[8], p[10], p[12])
            self.symbol_table.insert(orElim, p[0])
            self.box_latex += "{} & $\\lor e$ {}, {}-{}, {}-{}\\\\\n".format(
                formula.toLatex(), p[4].value, p[6].value, p[8].value, p[10].value, p[12].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula NEG_INTROD NUM DASH NUM')
        def Neg_introd(p):
            formula_result = p[2]
            formula = formula_result[1]
            negationIntrod = self.rule_factory.create_rule(
                'negation_introduction', p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(negationIntrod, p[0])
            self.box_latex += "{} & $\lnot i$ {}-{}\\\\\n".format(
                formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula BOTTOM_ELIM NUM')
        def Bottom(p):
            formula_result = p[2]
            formula = formula_result[1]
            bottom = self.rule_factory.create_rule(
                'bottom_elimination', p[0].value, formula, p[4])
            self.symbol_table.insert(bottom, p[0])
            self.box_latex += "{} & $\\bot e$ {}\\\\\n".format(
                formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula RAA NUM DASH NUM')
        def Raa(p):
            formula_result = p[2]
            formula = formula_result[1]
            raa = self.rule_factory.create_rule(
                'raa', p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(raa, p[0])
            self.box_latex += "{} & raa {}-{}\\\\\n".format(
                formula.toLatex(), p[4].value, p[6].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula COPY NUM')
        def Copy(p):
            copied_scope = self.symbol_table.find_scope(p[4].value)
            if self.symbol_table.check_scope_is_valid(copied_scope):
                line = p[4].value
                formula_result = p[2]
                original_rule = self.symbol_table.get_rule(line)

                if original_rule is not None:
                    rule = copy.deepcopy(original_rule)
                    rule._is_copied = True

                    if hasattr(rule, 'copied'):
                        rule.copied = original_rule.line

                    formula = formula_result[1]

                    if rule.formula != formula:
                        formula_diff = rule.formula
                        rule._formula = formula
                        self.has_error = True
                        deduction_result.add_error(self.get_error(
                            constants.COPY_DIFFERENT_FORMULE, formula_result[0], rule))
                        rule._formula = formula_diff

                    self.box_latex += "{} & copie {}\\\\\n".format(
                        formula.toLatex(), p[4].value)

                    copy_rule = self.rule_factory.create_rule(
                        'copy', p[0].value, formula, p[4])
                    copy_rule._is_copied = True
                    self.symbol_table.insert(copy_rule, p[0])
                else:
                    self.has_error = True
                    deduction_result.add_error(
                        self.get_error(constants.NONE_COPY, p[4], None))
            else:
                self.has_error = True
                deduction_result.add_error(self.get_error(
                    constants.USING_DESCARTED_RULE, p[4], None))

            return p[0], p[2][0]

        @self.pg.production('step : CLOSE_BRACKET')
        def close_box(p):
            rule = self.symbol_table.get_last_rule_from_scope()
            if rule is None:
                self.has_error = True
                deduction_result.add_error(self.get_error(
                    constants.BOX_MUST_BE_DISPOSED_BY_RULE, p[0], rule))
                return p[0], rule
            elif self.symbol_table.get_box_start():
                self.symbol_table.end_scope(rule.line)
                self.box_latex = self.box_latex[:-3] + '\n'
                self.box_latex += "\end{subproof}\n"
            else:
                self.has_error = True
                deduction_result.add_error(self.get_error(
                    constants.CLOSE_BRACKET_WITHOUT_BOX, p[0], rule))
            token = p[0]
            token.value = rule.line
            return p[0], rule.formula

        @self.pg.production('step : NUM DOT formula ALL_ELIM NUM')
        def For_all_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            forAllElimination = self.rule_factory.create_rule(
                'forall_elimination', p[0].value, formula, p[4])
            self.symbol_table.insert(forAllElimination, p[0])
            self.box_latex += "{} & $\\forall e$ {}\\\\\n".format(
                formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula EXT_INTROD NUM')
        def Exists_intro(p):
            formula_result = p[2]
            formula = formula_result[1]
            existsIntroduction = self.rule_factory.create_rule(
                'exists_introduction', p[0].value, formula, p[4])
            self.symbol_table.insert(existsIntroduction, p[0])
            self.box_latex += "{} & $\\exists i$ {}\\\\\n".format(
                formula.toLatex(), p[4].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula EXT_ELIM NUM COMMA NUM DASH NUM')
        def Exists_elim(p):
            formula_result = p[2]
            formula = formula_result[1]
            existsElim = self.rule_factory.create_rule(
                'exists_elimination', p[0].value, formula, p[4], p[6], p[8])
            self.symbol_table.insert(existsElim, p[0])
            self.box_latex += "{} & $\\exists e$ {},{}-{}\\\\\n".format(
                formula.toLatex(), p[4].value, p[6].value, p[8].value)
            return p[0], formula_result[0]

        @self.pg.production('step : NUM DOT formula ALL_INTROD NUM DASH NUM')
        def For_all_intro(p):
            formula_result = p[2]
            formula = formula_result[1]
            allIntrod = self.rule_factory.create_rule(
                'forall_introduction', p[0].value, formula, p[4], p[6])
            self.symbol_table.insert(allIntrod, p[0])
            self.box_latex += "{} & $\\forall i$ {}-{}\\\\\n".format(
                formula.toLatex(), p[4].value, p[6].value)
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
            deduction_result.add_error(self.get_error(
                constants.INVALID_RULE, p[3], wrong_rule))
            return p[0], p[2]

        @self.pg.production('step : NUM DOT formula AND_ELIM NUM COMMA NUM ')
        @self.pg.production('step : NUM DOT formula AND_ELIM NUM DASH NUM')
        def Wrong_use_conective_reference(p):
            self.has_error = True
            from Factory.WrongDef import WrongDef
            wrong_rule = WrongDef(p[0].value, p[2])
            deduction_result.add_error(self.get_error(
                constants.INVALID_RULE_ONE_REFERENCE, p[3], wrong_rule))
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
            elif len(p) == 4:
                # Predicate Formula
                varlist = p[2]
                return p[0], PredicateFormula(name=p[0].value, variables=varlist[1])
            elif len(p) == 3:
                # Binary Formula
                result1 = p[0]
                result2 = p[2]
                if (p[1].value == '&'):
                    return result1[0], AndFormula(left=result1[1], right=result2[1])
                elif (p[1].value == '|'):
                    return result1[0], OrFormula(left=result1[1], right=result2[1])
                elif (p[1].value == '->'):
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

            if (productions == ['']):
                error = 'Nenhuma demonstração foi recebida, verifique a entrada.'
            if token.gettokentype() == '$end':
                error = 'Uma das definições não está completa, verifique se todas regras foram aplicadas corretamente. Lembre-se que uma regra de inferência sempre inicia com um número seguido de um . (linha de referência), tem uma fórmula e uma justificativa (premissa, hipóteses ou uma das regras de inferência com suas respectivas referências para fórmulas anteriores).'
            else:
                source_position = token.getsourcepos()
                error = 'Uma das definições não está completa, verifique se todas regras foram aplicadas corretamente.\nLembre-se que uma regra de inferência sempre inicia com um número seguido de um . (linha de referência), tem uma fórmula e uma justificativa (premissa, hipóteses ou uma das regras de inferência com suas respectivas referências para fórmulas anteriores).\n'
                error += "Erro de sintaxe:\n"
                error += productions[source_position.lineno - 1]
                string = '\n'
                for i in range(source_position.colno - 1):
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

    def theorem_to_string(self, parentheses=False):
        return self.symbol_table.theoremToString(parentheses=parentheses)

    def theorem_to_latex(self, parentheses=False):
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
    def toString(premisses, conclusion, parentheses=False):
        if (premisses == []):
            return '|- '+conclusion.toString(parentheses=parentheses)
        else:
            return ", ".join(f.toString(parentheses=parentheses) for f in premisses)+' |- '+conclusion.toString(parentheses=parentheses)

    @staticmethod
    def toLatex(premisses, conclusion, parentheses=False):
        if (premisses == []):
            return '\\vdash '+conclusion.toLatex(parentheses=parentheses)
        else:
            return ", ".join(f.toLatex(parentheses=parentheses) for f in premisses) + ' \\vdash '+conclusion.toLatex(parentheses=parentheses)
