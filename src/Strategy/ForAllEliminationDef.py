from QuantifierFormula.QuantifierFormula import QuantifierFormula
from Strategy.Rule import Rule
from Strategy.RuleContext import RuleContext

class ForAllEliminationDef(Rule):
    def validate(self, context: RuleContext) -> bool:
        if len(context.references) != 1:
            context.errors.append("ForAll Elimination requires 1 reference")
            return False
        ref = context.references[0]
        f = context.symbol_table.lookup_formula_by_line(context.line, ref.value)
        if not isinstance(f, QuantifierFormula) or not f.is_forall():
            context.errors.append("Reference is not a universal quantifier")
            return False
        return True

    def get_latex_notation(self, context: RuleContext) -> str:
        ref = context.references[0]
        lhs = context.formula.toLatex()
        latex_r = context.symbol_table.get_rule(ref.value).toLatex(context.symbol_table)
        return f"\\infer[\\!\\!{{\\forall e}}]{{{lhs}}}{{{latex_r}}}"

    def get_name(self) -> str:
        return "ForAll Elimination"
