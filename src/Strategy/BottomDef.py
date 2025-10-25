from NegationFormula.NegationFormula import NegationFormula
from Strategy.Rule import Rule
from Strategy.RuleContext import RuleContext

class BottomDef(Rule):
    def validate(self, context: RuleContext) -> bool:
        if len(context.references) != 1:
            context.errors.append("Bottom requires 1 reference")
            return False
        f = context.symbol_table.lookup_formula_by_line(context.line, context.references[0].value)
        if f.toString() != '@':
            context.errors.append("Reference is not bottom (@)")
            return False
        return True

    def get_latex_notation(self, context: RuleContext) -> str:
        ref = context.references[0]
        lhs = context.formula.toLatex()
        latex_r = context.symbol_table.get_rule(ref.value).toLatex(context.symbol_table)
        return f"\\infer[\\!\\!{{\\bot e}}]{{{lhs}}}{{{latex_r}}}"

    def get_name(self) -> str:
        return "Bottom"