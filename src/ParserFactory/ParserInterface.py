from abc import ABC, abstractmethod

class ParserInterface(ABC):
    """Interface comum para todos os parsers"""
    
    @abstractmethod
    def parse(self):
        """Executa o parsing do texto"""
        pass
    
    @abstractmethod
    def get_parser(self):
        """Retorna o parser construído"""
        pass
    
    @abstractmethod
    def get_result(self):
        """Retorna o resultado do parsing"""
        pass