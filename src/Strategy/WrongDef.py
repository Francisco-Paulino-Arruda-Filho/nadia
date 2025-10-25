from Strategy.Rule import Rule
from Strategy.RuleContext import RuleContext

class WrongDef(Rule):
    """Regra que representa uma linha incorreta ou inválida"""

    def validate(self, context: RuleContext) -> bool:
        # Sempre inválida
        context.errors.append("Linha marcada como incorreta")
        return False

    def get_latex_notation(self, context: RuleContext) -> str:
        return f"{{{context.formula.toLatex()}}}"

    def get_name(self) -> str:
        return "Wrong"
