from Factory.RuleBase import RuleBase
from BinaryFormula.BinaryFormula import BinaryFormula
from utils.HypothesisManager import HypothesisManager
from models.constants import constants

class DisjunctionEliminationDef(RuleBase):
    def __init__(self, line: str, formula, reference1, reference2, reference3, reference4, reference5):
        self._line = line
        self._formula = formula
        self.reference1 = reference1
        self.reference2 = reference2
        self.reference3 = reference3
        self.reference4 = reference4
        self.reference5 = reference5
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
        
        formula2, formula3 = parser.symbol_table.check_scope_delimiter(self.reference2.value, self.reference3.value)
        formula4, formula5 = parser.symbol_table.check_scope_delimiter(self.reference4.value, self.reference5.value)
        
        if formula1 is None or formula2 is None or formula3 is None or formula4 is None or formula_reference is None:
            return

        if not isinstance(formula1, BinaryFormula) or (isinstance(formula1, BinaryFormula) and not formula1.is_disjunction()):
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.IS_NOT_DISJUNCTION, self.reference1, self))
        else:
            if formula1.left != formula2:
                parser.has_error = True
                deduction_result.add_error(parser.get_error(constants.INVALID_HYPOTHESIS, self.reference2, self))
            if formula1.right != formula4:
                parser.has_error = True
                deduction_result.add_error(parser.get_error(constants.INVALID_HYPOTHESIS, self.reference4, self))
            if self.formula != formula3:
                parser.has_error = True
                deduction_result.add_error(parser.get_error(constants.INVALID_BOX_RESULT, self.reference3, self))
            if self.formula != formula5:
                parser.has_error = True
                deduction_result.add_error(parser.get_error(constants.INVALID_BOX_RESULT, self.reference5, self))

    def toLatex(self, symbol_table) -> str:
        hypothesis_number1 = HypothesisManager.get_hypothesis_number(self.reference2.value)
        hypothesis_number2 = HypothesisManager.get_hypothesis_number(self.reference4.value)
        return f'\\infer[\\!\\!{{\\lor\\text{{e}}^{{{hypothesis_number1}, {hypothesis_number2}}}}}]{{{self.formula.toLatex()}}}{{{symbol_table.get_rule(self.reference1.value).toLatex(symbol_table)}&{symbol_table.get_rule(self.reference3.value).toLatex(symbol_table)}&{symbol_table.get_rule(self.reference5.value).toLatex(symbol_table)}}}'