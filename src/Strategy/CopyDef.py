from Strategy.Rule import Rule
from Strategy.RuleContext import RuleContext

class CopyDef(Rule):
    """Copia o conteúdo de uma linha já existente"""

    def validate(self, context: RuleContext) -> bool:
        if len(context.references) != 1:
            context.errors.append("Copy requires exactly one reference")
            return False
        ref = context.references[0]
        # Verifica visibilidade
        if not context.symbol_table.check_is_visible(context.line, ref.value):
            context.errors.append(f"Linha {ref.value} não é visível")
            return False
        # Verifica se a fórmula é igual
        formula_ref = context.symbol_table.lookup_formula_by_line(context.line, ref.value)
        if formula_ref != context.formula:
            context.errors.append("Fórmula copiada é diferente da referência")
            return False
        return True

    def get_latex_notation(self, context: RuleContext) -> str:
        ref = context.references[0]
        formula_ref = context.symbol_table.get_rule(ref.value).toLatex(context.symbol_table)
        return f"{{{formula_ref}}}"

    def get_name(self) -> str:
        return "Copy"
