from abc import ABC, abstractmethod
from models.constants import constants

class InferenceRuleStrategy(ABC):
    """Interface Strategy base para todas as regras de inferência"""

    def __init__(self, line, formula, references=None):
        self.line = line
        self.formula = formula
        self.references = references or []
        self.is_copied = False

    @abstractmethod
    def evaluation(self, parser, deduction_result):
        """Método Strategy - valida a aplicação da regra"""
        pass

    @abstractmethod
    def toLatex(self, symbol_table):
        """Método Strategy - gera representação LaTeX"""
        pass

    @abstractmethod
    def get_rule_name(self):
        """Retorna o nome da regra para identificação"""
        pass

    def validate_references_exist(self, parser, deduction_result):
        """Validação comum - verifica se as referências existem"""
        for i, ref in enumerate(self.references):
            if not hasattr(ref, 'value'):
                continue
            ref_formula = parser.symbol_table.lookup_formula_by_line(self.line, ref.value)
            if ref_formula is None:
                parser.has_error = True
                deduction_result.add_error(
                    parser.get_error(constants.REFERENCED_LINE_NOT_DEFINED, ref, self)
                )
                return False
        return True

    def validate_references_before(self, parser, deduction_result):
        """Validação comum - verifica se referências são anteriores"""
        for ref in self.references:
            if hasattr(ref, 'value') and int(ref.value) >= int(self.line):
                parser.has_error = True
                deduction_result.add_error(
                    parser.get_error(constants.REFERENCED_LINE_NOT_DEFINED, ref, self)
                )
                return False
        return True