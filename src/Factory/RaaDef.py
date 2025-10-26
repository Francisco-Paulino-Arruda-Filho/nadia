from Factory.RuleBase import RuleBase
from NegationFormula.NegationFormula import NegationFormula
from models.constants import constants
from utils.HypothesisManager import HypothesisManager

class RaaDef(RuleBase):
    def __init__(self, line: str, formula, reference1, reference2):
        self._line = line
        self._formula = formula
        self.reference1 = reference1
        self.reference2 = reference2
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
        formula_reference = parser.symbol_table.find_token(self.line)
        formula1, formula2 = parser.symbol_table.check_scope_delimiter(self.reference1.value, self.reference2.value)
        if formula1 is None or formula2 is None or formula_reference is None:
            return

        if formula1 != NegationFormula(self.formula):
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.INVALID_HYPOTHESIS, self.reference1, self))
        if formula2.toString() != '@':
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.INVALID_BOX_RESULT, self.reference2, self))

    def toLatex(self, symbol_table) -> str:
        hypothesis_number = HypothesisManager.get_hypothesis_number(self.reference1.value)
        return f'\\infer[\\!\\!{{\\text{{raa}}^{{{hypothesis_number}}}}}]{{{self.formula.toLatex()}}}{{{symbol_table.get_rule(self.reference2.value).toLatex(symbol_table)}}}'