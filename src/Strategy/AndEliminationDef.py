from BinaryFormula.BinaryFormula import BinaryFormula
from Strategy.Rule import Rule
from Strategy.RuleContext import RuleContext


class AndEliminationDef(Rule):
    def validate(self, context: RuleContext) -> bool:
        if len(context.references) != 1:
            context.errors.append("AND Elimination requires 1 reference")
            return False
        ref = context.references[0]
        f = context.symbol_table.lookup_formula_by_line(context.line, ref.value)
        if not isinstance(f, BinaryFormula) or not f.is_conjunction():
            context.errors.append("Reference is not a conjunction")
            return False
        if not (f.left == context.formula or f.right == context.formula):
            context.errors.append("Formula does not match left or right of conjunction")
            return False
        return True

    def get_latex_notation(self, context: RuleContext) -> str:
        ref = context.references[0]
        lhs = context.formula.toLatex()
        latex_r = context.symbol_table.get_rule(ref.value).toLatex(context.symbol_table)
        return f"\\infer[\\!\\!{{\\land\\text{{e}}}}]{{{lhs}}}{{{latex_r}}}"

    def get_name(self) -> str:
        return "And Elimination"