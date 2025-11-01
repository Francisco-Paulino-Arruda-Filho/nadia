from Factory.HypothesisFirstOrderDef import HypothesisFirstOrderDef
from Factory.RuleBase import RuleBase
from QuantifierFormula.QuantifierFormula import QuantifierFormula
from models.constants import constants

class ForAllIntroductionDef(RuleBase):
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
        # Valida as referências das caixas
        parser.check_scope_reference_error(deduction_result, self)
        
        variable = parser.symbol_table.find_scope_variable(self.reference1.value)
        first_rule = parser.symbol_table.get_first_rule_from_scope(self.reference1.value)
        
        if variable is None:
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.BOX_MUST_HAVE_A_VARIABLE, self.reference1, self))
            return
        elif isinstance(first_rule, HypothesisFirstOrderDef):
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.BOX_MUST_HAVE_ONLY_A_VARIABLE, self.reference1, self))
            return
        
        if not parser.symbol_table.is_fresh_variable(self.reference1.value):
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.VARIABLE_IS_NOT_FRESH_VARIABLE, self.reference1, self))

        formula_reference = parser.symbol_table.find_token(self.line)
        formula1, formula2 = parser.symbol_table.check_scope_delimiter(self.reference1.value, self.reference2.value)
        if formula1 is None or formula2 is None or formula_reference is None:
            return

        if not isinstance(self.formula, QuantifierFormula) or (isinstance(self.formula, QuantifierFormula) and not self.formula.is_universal()):
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.INVALID_EXISTENTIAL_FORMULA, formula_reference, self))

        if isinstance(self.formula, QuantifierFormula) and self.formula.formula.substitution(self.formula.variable, variable) != formula2:
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.INVALID_CONCLUSION_UNIVERSAL_LAST_RULE, self.reference2, self))

        if variable in self.formula.free_variables():
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.INVALID_CONCLUSION_UNIVERSAL, formula_reference, self))

    def toLatex(self, symbol_table) -> str:
        return f'\\infer[\\!\\!{{\\forall\\text{{i}}}}]{{{self.formula.toLatex()}}}{{{symbol_table.get_rule(self.reference2.value).toLatex(symbol_table)}}}'