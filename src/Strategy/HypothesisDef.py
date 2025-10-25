from Strategy.Rule import Rule
from Strategy.RuleContext import RuleContext


class HypothesisDef(Rule):
    """Representa uma hipótese"""

    def validate(self, context: RuleContext) -> bool:
        # Hipótese sempre válida no início de uma caixa
        return True

    def get_latex_notation(self, context: RuleContext) -> str:
        return f"{{{context.formula.toLatex()}}}"

    def get_name(self) -> str:
        return "Hypothesis"
