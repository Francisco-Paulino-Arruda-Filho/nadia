from abc import ABC, abstractmethod
from typing import Any

class RuleBase(ABC):
    """Interface base para todas as regras de inferência"""
    
    @abstractmethod
    def evaluation(self, parser, deduction_result) -> None:
        pass
    
    @abstractmethod
    def toLatex(self, symbol_table) -> str:
        pass
    
    @property
    @abstractmethod
    def line(self) -> str:
        pass
    
    @property
    @abstractmethod
    def formula(self) -> Any:
        pass
    
    @property
    @abstractmethod
    def is_copied(self) -> bool:
        pass
    
    @is_copied.setter
    @abstractmethod
    def is_copied(self, value: bool) -> None:
        pass