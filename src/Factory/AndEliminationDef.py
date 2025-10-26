from Factory.RuleBase import RuleBase
from BinaryFormula.BinaryFormula import BinaryFormula
from models.constants import constants

class AndEliminationDef(RuleBase):
    def __init__(self, line: str, formula, reference1):
        self._line = line
        self._formula = formula
        self.reference1 = reference1
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

        formula_reference = parser.symbol_table.find_token(self.line)
        formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
        if formula1 is None:
            return

        if not isinstance(formula1, BinaryFormula) or (isinstance(formula1, BinaryFormula) and not formula1.is_conjunction()):
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.IS_NOT_CONJUNCTION, formula_reference, self))
        else:
            if not (formula1.left == self.formula or formula1.right == self.formula):
                parser.has_error = True
                deduction_result.add_error(parser.get_error(constants.INVALID_LEFT_OR_RIGHT_CONJUNCTION, self.reference1, self))

    def toLatex(self, symbol_table) -> str:
        return f'\\infer[\\!\\!{{\\land\\text{{e}}}}]{{{self.formula.toLatex()}}}{{{symbol_table.get_rule(self.reference1.value).toLatex(symbol_table)}}}'