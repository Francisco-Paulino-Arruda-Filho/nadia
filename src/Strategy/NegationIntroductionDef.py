from NegationFormula.NegationFormula import NegationFormula
from Strategy.Rule import Rule
from Strategy.RuleContext import RuleContext

class NegationIntroductionDef(Rule):
    def validate(self, context: RuleContext) -> bool:
        if len(context.references) != 2:
            context.errors.append("Negation Introduction requires 2 references")
            return False
        hypo, concl = context.symbol_table.check_scope_delimiter(
            context.references[0].value, context.references[1].value
        )
        if not isinstance(context.formula, NegationFormula):
            context.errors.append("Formula must be a negation")
            return False
        if context.formula.formula != hypo:
            context.errors.append("Hypothesis does not match negation")
            return False
        if concl.toString() != '@':
            context.errors.append("Box conclusion must be bottom (@)")
            return False
        return True

    def get_latex_notation(self, context: RuleContext) -> str:
        r1, r2 = context.references
        hypo_num = str(len(context.hypothesis) + 1)
        context.hypothesis[r1.value] = hypo_num
        lhs = context.formula.toLatex()
        latex_r2 = context.symbol_table.get_rule(r2.value).toLatex(context.symbol_table)
        return f"\\infer[\\!\\!{{\\lnot\\text{{i}}^{{_{hypo_num}}}}}]{{{lhs}}}{{{latex_r2}}}"

    def get_name(self) -> str:
        return "Negation Introduction"
