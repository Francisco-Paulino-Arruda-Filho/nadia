from BinaryFormula.ImplicationFormula import ImplicationFormula
from Strategy.RuleContext import RuleContext
from Strategy.Rule import Rule


class ImplicationEliminationDef(Rule):
    """Regra de Eliminação da Implicação (Modus Ponens)"""
    
    def validate(self, context: RuleContext) -> bool:
        if len(context.references) != 2:
            context.errors.append("Eliminação da implicação requer 2 referências")
            return False
            
        ref1, ref2 = context.references
        
        # Verifica se as referências são visíveis
        if not context.symbol_table.check_is_visible(context.line, ref1.value):
            context.errors.append(f"Linha {ref1.value} não é visível")
            return False
            
        if not context.symbol_table.check_is_visible(context.line, ref2.value):
            context.errors.append(f"Linha {ref2.value} não é visível")
            return False
        
        # Obtém as fórmulas das referências
        formula1 = context.symbol_table.lookup_formula_by_line(context.line, ref1.value)
        formula2 = context.symbol_table.lookup_formula_by_line(context.line, ref2.value)
        
        if not formula1 or not formula2:
            context.errors.append("Fórmula de referência não encontrada")
            return False
        
        # Verifica se uma é implicação e a outra é o antecedente
        is_valid = (
            (isinstance(formula1, ImplicationFormula) and formula1.left == formula2 and formula1.right == context.formula) or
            (isinstance(formula2, ImplicationFormula) and formula2.left == formula1 and formula2.right == context.formula)
        )
        
        if not is_valid:
            context.errors.append("Combinação inválida de implicação e antecedente")
            return False
            
        return True
    
    def get_latex_notation(self, context: RuleContext) -> str:
        ref1, ref2 = context.references
        lhs = context.formula.toLatex()
        r1 = context.symbol_table.get_rule(ref1.value).toLatex(context.symbol_table)
        r2 = context.symbol_table.get_rule(ref2.value).toLatex(context.symbol_table)
        return '\\infer[\\!\\!{\\rightarrow\\text{e}}]{' + lhs + '}{' + r1 + ' & ' + r2 + '}'
    
    def get_name(self) -> str:
        return "Implication Elimination"