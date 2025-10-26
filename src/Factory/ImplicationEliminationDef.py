from BinaryFormula.BinaryFormula import BinaryFormula
from Factory.RuleBase import RuleBase
from models.constants import constants

class ImplicationEliminationDef(RuleBase):
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
        before = parser.check_line_reference_before_rule_error(deduction_result, self)
        if before:
            parser.check_line_scope_reference_error(deduction_result, self, reference1=True, reference2=True)      

        formula_reference = parser.symbol_table.find_token(self.line)
        formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
        formula2 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference2.value)
        if formula1 is None or formula2 is None or formula_reference is None:
            return

        if (BinaryFormula(key='->', left=formula1, right=self.formula) != formula2
        and BinaryFormula(key='->', left=formula2, right=self.formula) != formula1):
            deduction_result.add_error(parser.get_error(constants.INVALID_RESULT, self.reference1, self))

    def toLatex(self, symbol_table) -> str:
        return f'\\infer[\\!\\!{{\\rightarrow\\text{{e}}}}]{{{self.formula.toLatex()}}}{{{symbol_table.get_rule(self.reference1.value).toLatex(symbol_table)}&{symbol_table.get_rule(self.reference2.value).toLatex(symbol_table)}}}'