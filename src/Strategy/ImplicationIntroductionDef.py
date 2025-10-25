from BinaryFormula.ImplicationFormula import ImplicationFormula
from Strategy.InferenceBase import InferenceRule
from Strategy.InferenceContext import InferenceContext


class ImplicationIntroductionDef(InferenceRule):
    """Regra de Introdução da Implicação"""
    
    def validate(self, context: InferenceContext) -> bool:
        if len(context.references) != 2:
            context.errors.append("Introdução da implicação requer 2 referências")
            return False
            
        start_ref, end_ref = context.references
        
        # Verifica se forma uma caixa válida
        hypothesis, conclusion = context.symbol_table.check_scope_delimiter(
            start_ref.value, end_ref.value
        )
        
        if not hypothesis or not conclusion:
            context.errors.append("Referências não formam uma caixa válida")
            return False
        
        # Verifica se a conclusão é uma implicação
        if not isinstance(context.formula, ImplicationFormula):
            context.errors.append("Fórmula deve ser uma implicação")
            return False
        
        # Verifica se a hipótese é o antecedente e a conclusão da caixa é o consequente
        if context.formula.left != hypothesis:
            context.errors.append("Hipótese não corresponde ao antecedente")
            return False
            
        if context.formula.right != conclusion:
            context.errors.append("Conclusão da caixa não corresponde ao consequente")
            return False
            
        return True
    
    def get_latex_notation(self, context: InferenceContext) -> str:
        start_ref, end_ref = context.references
        hypothesis_number = str(len(context.hypothesis) + 1)
        context.hypothesis[start_ref.value] = hypothesis_number
        return f'\\infer[\\!\\!{{\\rightarrow\\text{{i}}^{{_{hypothesis_number}}}}}]{{{context.formula.toLatex()}}}{{{context.symbol_table.get_rule(end_ref.value).toLatex(context.symbol_table)}}}'
    
    def get_name(self) -> str:
        return "Implication Introduction"