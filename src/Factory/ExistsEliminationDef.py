from Factory.RuleBase import RuleBase
from QuantifierFormula.QuantifierFormula import QuantifierFormula
from models.constants import constants
from utils.HypothesisManager import HypothesisManager

class ExistsEliminationDef(RuleBase):
    def __init__(self, line: str, formula, reference1, reference2, reference3):
        self._line = line
        self._formula = formula
        self.reference1 = reference1
        self.reference2 = reference2
        self.reference3 = reference3
        self._is_copied = False

    @property
    def line(self) -> str:
        return self._line

    @property
    def formula(self):
        return self._formula

    @property
    def is_copied(self) -> bool:
        return self._is_copied

    @is_copied.setter
    def is_copied(self, value: bool) -> None:
        self._is_copied = value

    def evaluation(self, parser, deduction_result) -> None:
        before = parser.check_line_reference_before_rule_error(deduction_result, self)
        if before:
            parser.check_line_scope_reference_error(deduction_result, self, reference1=True)      

        variable = parser.symbol_table.find_scope_variable(self.reference2.value)
        if variable is None:
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.BOX_MUST_HAVE_A_VARIABLE, self.reference2, self))
            return

        if not parser.symbol_table.is_fresh_variable(self.reference2.value):
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.VARIABLE_IS_NOT_FRESH_VARIABLE, self.reference2, self))

        formula_reference = parser.symbol_table.find_token(self.line)
        formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
        formula2, formula3 = parser.symbol_table.check_scope_delimiter(self.reference2.value, self.reference3.value)
        
        if formula1 is None or formula2 is None or formula3 is None or formula_reference is None:
            return

        if self.formula != formula3:
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.INVALID_CONCLUSION_EXISTENTIAL_LAST_RULE, self.reference3, self))

        if not isinstance(formula1, QuantifierFormula) or (isinstance(formula1, QuantifierFormula) and not formula1.is_existential()):
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.INVALID_EXISTENTIAL_FORMULA, formula_reference, self))

        if isinstance(formula1, QuantifierFormula) and formula1.formula.substitution(formula1.variable, variable) != formula2:
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.INVALID_SUBSTITUTION_EXISTENTIAL, self.reference2, self))

        if variable in formula3.free_variables():
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.INVALID_CONCLUSION_EXISTENTIAL, self.reference2, self))

    def toLatex(self, symbol_table) -> str:
        hypothesis_number = HypothesisManager.get_hypothesis_number(self.reference2.value)
        return f'\\infer[\\!\\!{{\\exists\\text{{e}}^{{{hypothesis_number}}}}}]{{{self.formula.toLatex()}}}{{{symbol_table.get_rule(self.reference1.value).toLatex(symbol_table)} & {symbol_table.get_rule(self.reference3.value).toLatex(symbol_table)}}}'