from abc import ABC, abstractmethod

from rply import ParserGenerator

class BaseParser(ABC):
    """Classe base com Template Method pattern"""
    
    def __init__(self, state):
        self.state = state
        self.pg = ParserGenerator(self.get_tokens(), self.get_precedence())
        self.parse()
    
    @abstractmethod
    def get_tokens(self):
        """Template Method - deve ser implementado pelas subclasses"""
        pass
    
    @abstractmethod
    def get_precedence(self):
        """Template Method - deve ser implementado pelas subclasses"""
        pass
    
    @abstractmethod
    def parse(self):
        """Template Method - deve ser implementado pelas subclasses"""
        pass
    
    def get_parser(self):
        """Factory Method comum a todos os parsers"""
        return self.pg.build()