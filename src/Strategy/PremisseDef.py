from Strategy.Rule import Rule
from Strategy.RuleContext import RuleContext

class PremisseDef(Rule):
    """Representa uma premissa"""

    def validate(self, context: RuleContext) -> bool:
        # Sempre válida, não precisa de referência
        return True

    def get_latex_notation(self, context: RuleContext) -> str:
        return f"{{{context.formula.toLatex()}}}"

    def get_name(self) -> str:
        return "Premisse"
