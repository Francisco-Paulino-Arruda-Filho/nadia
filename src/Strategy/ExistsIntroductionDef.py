from QuantifierFormula.QuantifierFormula import QuantifierFormula
from Strategy.Rule import Rule
from Strategy.RuleContext import RuleContext

class ExistsIntroductionDef(Rule):
    def validate(self, context: RuleContext) -> bool:
        if len(context.references) != 1:
            context.errors.append("Exists Introduction requires 1 reference")
            return False
        ref = context.references[0]
        f = context.symbol_table.lookup_formula_by_line(context.line, ref.value)
        if not isinstance(context.formula, QuantifierFormula) or not context.formula.is_exists():
            context.errors.append("Formula must be existential quantifier")
            return False
        return True

    def get_latex_notation(self, context: RuleContext) -> str:
        ref = context.references[0]
        lhs = context.formula.toLatex()
        latex_r = context.symbol_table.get_rule(ref.value).toLatex(context.symbol_table)
        return f"\\infer[\\!\\!{{\\exists i}}]{{{lhs}}}{{{latex_r}}}"

    def get_name(self) -> str:
        return "Exists Introduction"
