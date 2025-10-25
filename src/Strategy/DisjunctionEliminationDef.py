from Strategy.Rule import Rule
from Strategy.RuleContext import RuleContext
from BinaryFormula.BinaryFormula import BinaryFormula


class DisjunctionEliminationDef(Rule):
    def validate(self, context: RuleContext) -> bool:
        if len(context.references) != 5:
            context.errors.append("OR Elimination requires 5 references")
            return False
        f_disj = context.symbol_table.lookup_formula_by_line(context.line, context.references[0].value)
        if not isinstance(f_disj, BinaryFormula) or not f_disj.is_disjunction():
            context.errors.append("First reference is not a disjunction")
            return False
        # Boxes validation (ref2+ref3 and ref4+ref5) omitted: assume parser.symbol_table.check_scope_delimiter
        hypothesis1, conclusion1 = context.symbol_table.check_scope_delimiter(context.references[1].value, context.references[2].value)
        hypothesis2, conclusion2 = context.symbol_table.check_scope_delimiter(context.references[3].value, context.references[4].value)
        if f_disj.left != hypothesis1 or f_disj.right != hypothesis2:
            context.errors.append("Hypotheses do not match disjunction sides")
            return False
        if context.formula != conclusion1 or context.formula != conclusion2:
            context.errors.append("Box conclusions do not match formula")
            return False
        return True

    def get_latex_notation(self, context: RuleContext) -> str:
        r = context.references
        h1_num = str(len(context.hypothesis) + 1)
        h2_num = str(len(context.hypothesis) + 2)
        context.hypothesis[r[1].value] = h1_num
        context.hypothesis[r[3].value] = h2_num
        lhs = context.formula.toLatex()
        latex_r1 = context.symbol_table.get_rule(r[0].value).toLatex(context.symbol_table)
        latex_r3 = context.symbol_table.get_rule(r[2].value).toLatex(context.symbol_table)
        latex_r5 = context.symbol_table.get_rule(r[4].value).toLatex(context.symbol_table)
        return f"\\infer[\\!\\!{{\\lor\\text{{e}}^{{_{h1_num}, {h2_num}}}}}]{{{lhs}}}{{{latex_r1} & {latex_r3} & {latex_r5}}}"

    def get_name(self) -> str:
        return "Disjunction Elimination"
