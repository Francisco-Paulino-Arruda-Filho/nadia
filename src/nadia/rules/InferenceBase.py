from abc import ABC, abstractmethod
from Strategy.InferenceContext import InferenceContext


class InferenceRule(ABC):
    @abstractmethod
    def evaluation(self, context: InferenceContext) -> bool:
        """Valida se a regra pode ser aplicada corretamente"""
        pass

    @abstractmethod
    def toLatex(self, context: InferenceContext) -> str:
        """Retorna a notação LaTeX para a regra"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Retorna o nome da regra"""
        pass
