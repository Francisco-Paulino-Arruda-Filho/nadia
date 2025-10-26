from Factory.RuleBase import RuleBase

class PremisseDef(RuleBase):
    def __init__(self, line: str, formula):
        self._line = line
        self._formula = formula
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
        return '{' + self._formula.toLatex() + '}'