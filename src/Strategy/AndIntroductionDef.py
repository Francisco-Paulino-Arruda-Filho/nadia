from Strategy.Rule import Rule
from Strategy.RuleContext import RuleContext
from BinaryFormula.BinaryFormula import BinaryFormula


class AndIntroductionDef(Rule):
    def validate(self, context: RuleContext) -> bool:
        if len(context.references) != 2:
            context.errors.append("AND Introduction requires 2 references")
            return False
        ref1, ref2 = context.references
        f1 = context.symbol_table.lookup_formula_by_line(context.line, ref1.value)
        f2 = context.symbol_table.lookup_formula_by_line(context.line, ref2.value)
        if not isinstance(context.formula, BinaryFormula) or not context.formula.is_conjunction():
            context.errors.append("Formula must be a conjunction")
            return False
        if not (context.formula.left == f1 or context.formula.left == f2):
            context.errors.append("Left side of conjunction does not match references")
            return False
        if not (context.formula.right == f1 or context.formula.right == f2):
            context.errors.append("Right side of conjunction does not match references")
            return False
        return True

    def get_latex_notation(self, context: RuleContext) -> str:
        r1, r2 = context.references
        lhs = context.formula.toLatex()
        latex_r1 = context.symbol_table.get_rule(r1.value).toLatex(context.symbol_table)
        latex_r2 = context.symbol_table.get_rule(r2.value).toLatex(context.symbol_table)
        return f"\\infer[\\!\\!{{\\land\\text{{i}}}}]{{{lhs}}}{{{latex_r1} & {latex_r2}}}"

    def get_name(self) -> str:
        return "And Introduction"