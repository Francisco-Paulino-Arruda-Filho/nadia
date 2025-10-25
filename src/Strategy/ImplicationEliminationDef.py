from Strategy.InferenceRuleStrategy import InferenceRuleStrategy
from models.BinaryFormula import BinaryFormula
from constants import constants

class ImplicationEliminationDef(InferenceRuleStrategy):
    """Strategy para a regra de Eliminação da Implicação (Modus Ponens)"""
    
    def __init__(self, line, formula, reference1, reference2):
        super().__init__(line, formula, [reference1, reference2])
        self.reference1 = reference1
        self.reference2 = reference2
    
    def evaluation(self, parser, deduction_result):
        """Implementação Strategy específica para eliminação da implicação"""
        # Validações comuns
        if not self.validate_references_before(parser, deduction_result):
            return
        if not self.validate_references_exist(parser, deduction_result):
            return
        
        # Validação específica da estratégia
        formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1.value)
        formula2 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference2.value)
        
        if formula1 is None or formula2 is None:
            return
        
        # Lógica específica do Modus Ponens
        implication1 = BinaryFormula(key='->', left=formula1, right=self.formula)
        implication2 = BinaryFormula(key='->', left=formula2, right=self.formula)
        
        if implication1 != formula2 and implication2 != formula1:
            deduction_result.add_error(
                parser.get_error(constants.INVALID_RESULT, self.reference1, self)
            )
    
    def toLatex(self, symbol_table):
        """Implementação Strategy específica para LaTeX"""
        rule1 = symbol_table.get_rule(self.reference1.value)
        rule2 = symbol_table.get_rule(self.reference2.value)
        return f'\\infer[\\!\\!{{\\rightarrow\\text{{e}}}}]{{{self.formula.toLatex()}}}{{{rule1.toLatex(symbol_table)}&{rule2.toLatex(symbol_table)}}}'
    
    def get_rule_name(self):
        return "Eliminação da Implicação"