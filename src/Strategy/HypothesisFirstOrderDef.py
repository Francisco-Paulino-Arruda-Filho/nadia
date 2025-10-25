
from Strategy.Rule import Rule
from Strategy.RuleContext import RuleContext

class HypothesisFirstOrderDef(Rule):
    """Representa uma hipótese de primeira ordem"""

    def validate(self, context: RuleContext) -> bool:
        # Hipótese FO sempre válida
        return True

    def get_latex_notation(self, context: RuleContext) -> str:
        line = context.line
        if line not in context.hypothesis:
            context.hypothesis[line] = str(len(context.hypothesis) + 1)
        return f"\\big[{context.formula.toLatex()}\\big]^{{_{context.hypothesis[line]}}}"

    def get_name(self) -> str:
        return "Hypothesis FO"
