from QuantifierFormula.QuantifierFormula import QuantifierFormula
from Strategy.Rule import Rule
from Strategy.RuleContext import RuleContext

class ExistsEliminationDef(Rule):
    def validate(self, context: RuleContext) -> bool:
        if len(context.references) != 3:
            context.errors.append("Exists Elimination requires 3 references")
            return False
        # ref1 = formula exists, ref2+ref3 = box
        hypo, concl = context.symbol_table.check_scope_delimiter(
            context.references[1].value, context.references[2].value
        )
        exists_formula = context.symbol_table.lookup_formula_by_line(context.line, context.references[0].value)
        if not isinstance(exists_formula, QuantifierFormula) or not exists_formula.is_exists():
            context.errors.append("First reference must be existential quantifier")
            return False
        if context.formula != concl:
            context.errors.append("Box conclusion does not match formula")
            return False
        return True

    def get_latex_notation(self, context: RuleContext) -> str:
        r = context.references
        hypo_num = str(len(context.hypothesis) + 1)
        context.hypothesis[r[1].value] = hypo_num
        lhs = context.formula.toLatex()
        latex_r1 = context.symbol_table.get_rule(r[0].value).toLatex(context.symbol_table)
        latex_r3 = context.symbol_table.get_rule(r[2].value).toLatex(context.symbol_table)
        return f"\\infer[\\!\\!{{\\exists e^{{_{hypo_num}}}}}]{{{lhs}}}{{{latex_r1} & {latex_r3}}}"

    def get_name(self) -> str:
        return "Exists Elimination"