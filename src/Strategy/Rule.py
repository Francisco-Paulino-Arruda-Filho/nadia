from abc import ABC, abstractmethod
from Strategy.RuleContext import RuleContext

class Rule(ABC):
    """Interface Strategy para regras de inferência"""
    
    @abstractmethod
    def validate(self, context: RuleContext) -> bool:
        """Valida se a regra pode ser aplicada corretamente"""
        pass
    
    @abstractmethod
    def get_latex_notation(self, context: RuleContext) -> str:
        """Retorna a notação LaTeX para a regra"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Retorna o nome da regra"""
        pass