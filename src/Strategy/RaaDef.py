from NegationFormula.NegationFormula import NegationFormula
from Strategy.Rule import Rule
from Strategy.RuleContext import RuleContext


class RaaDef(Rule):
    """Reductio ad Absurdum"""

    def validate(self, context: RuleContext) -> bool:
        if len(context.references) != 2:
            context.errors.append("RAA requires 2 references (box start and end)")
            return False
        hypo, concl = context.symbol_table.check_scope_delimiter(
            context.references[0].value, context.references[1].value
        )
        if not isinstance(context.formula, NegationFormula):
            context.errors.append("RAA formula must be a negation")
            return False
        if concl.toString() != '@':
            context.errors.append("RAA box must conclude with ⊥ (@)")
            return False
        if context.formula.formula != hypo:
            context.errors.append("RAA hypothesis does not match negated formula")
            return False
        return True

    def get_latex_notation(self, context: RuleContext) -> str:
        start_ref, end_ref = context.references
        hypo_num = str(len(context.hypothesis) + 1)
        context.hypothesis[start_ref.value] = hypo_num
        lhs = context.formula.toLatex()
        latex_r2 = context.symbol_table.get_rule(end_ref.value).toLatex(context.symbol_table)
        return f"\\infer[\\!\\!{{\\text{{raa}}^{{_{hypo_num}}}}}]{{{lhs}}}{{{latex_r2}}}"

    def get_name(self) -> str:
        return "Reductio ad Absurdum"
