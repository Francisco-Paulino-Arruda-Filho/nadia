from Factory.RuleBase import RuleBase
from utils.HypothesisManager import HypothesisManager

class HypothesisDef(RuleBase):
    def __init__(self, line: str, formula):
        self._line = line
        self._formula = formula
        self.copied = None
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
        return

    def toLatex(self, symbol_table) -> str:
        line = self.copied if self.copied else self.line
        hypothesis_number = HypothesisManager.get_hypothesis_number(line)
        return f'\\big[{self.formula.toLatex()}\\big]^{{{hypothesis_number}}}'