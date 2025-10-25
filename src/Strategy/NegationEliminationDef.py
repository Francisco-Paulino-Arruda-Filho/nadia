from NegationFormula.NegationFormula import NegationFormula
from Strategy.Rule import Rule
from Strategy.RuleContext import RuleContext

class NegationEliminationDef(Rule):
    def validate(self, context: RuleContext) -> bool:
        if len(context.references) != 2:
            context.errors.append("Negation Elimination requires 2 references")
            return False
        ref1, ref2 = context.references
        f1 = context.symbol_table.lookup_formula_by_line(context.line, ref1.value)
        f2 = context.symbol_table.lookup_formula_by_line(context.line, ref2.value)
        if context.formula.toString() != '@':
            context.errors.append("Result must be bottom (@)")
            return False
        if not (NegationFormula(f2) == f1 or NegationFormula(f1) == f2):
            context.errors.append("References do not match negation")
            return False
        return True

    def get_latex_notation(self, context: RuleContext) -> str:
        ref1, ref2 = context.references
        lhs = context.formula.toLatex()
        latex_r1 = context.symbol_table.get_rule(ref1.value).toLatex(context.symbol_table)
        latex_r2 = context.symbol_table.get_rule(ref2.value).toLatex(context.symbol_table)
        return f"\\infer[\\!\\!{{\\lnot\\text{{e}}}}]{{{lhs}}}{{{latex_r1} & {latex_r2}}}"

    def get_name(self) -> str:
        return "Negation Elimination"