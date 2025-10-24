from Observer.InferenceRuleStrategy import InferenceRuleStrategy
from models.BinaryFormula import BinaryFormula
from constants import constants


class ImplicationIntroductionDef(InferenceRuleStrategy):
    """Strategy para a regra de Introdução da Implicação"""
    
    def __init__(self, line, formula, reference1, reference2):
        super().__init__(line, formula, [reference1, reference2])
        self.reference1 = reference1
        self.reference2 = reference2
    
    def evaluation(self, parser, deduction_result):
        """Implementação Strategy específica para introdução da implicação"""
        if not self.validate_references_before(parser, deduction_result):
            return
        
        # Validação de escopo
        valid_box = parser.check_scope_reference_error(deduction_result, self)
        if not valid_box:
            return
        
        formula1, formula2 = parser.symbol_table.check_scope_delimiter(
            self.reference1.value, self.reference2.value
        )
        
        if formula1 is None or formula2 is None:
            return
        
        # Validações específicas da estratégia
        if not isinstance(self.formula, BinaryFormula) or not self.formula.is_implication():
            parser.has_error = True
            deduction_result.add_error(
                parser.get_error(constants.INVALID_RESULT, None, self)
            )
        else:
            if self.formula.left != formula1:
                parser.has_error = True
                deduction_result.add_error(
                    parser.get_error(constants.INVALID_HYPOTHESIS, self.reference1, self)
                )
            if self.formula.right != formula2:
                parser.has_error = True
                deduction_result.add_error(
                    parser.get_error(constants.INVALID_BOX_RESULT, self.reference2, self)
                )
    
    def toLatex(self, symbol_table):
        """Implementação Strategy específica para LaTeX"""
        from ast import hypothesis
        
        hypothesis_number = str(len(hypothesis) + 1)
        hypothesis[self.reference1.value] = hypothesis_number
        
        rule2 = symbol_table.get_rule(self.reference2.value)
        return f'\\infer[\\!\\!{{\\rightarrow\\text{{i}}^{{_{hypothesis_number}}}}}]{{{self.formula.toLatex()}}}{{{rule2.toLatex(symbol_table)}}}'
    
    def get_rule_name(self):
        return "Introdução da Implicação"