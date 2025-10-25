from ParserFactory import ParserNadia, ParserTheorem
from ParserFactory.ParserFormula import ParserFormula
from nadia.Lexer.Lexer import Lexer


class ParserFactory:
    """Factory centralizada para criação de parsers e lexers"""
    
    @staticmethod
    def create_lexer():
        """Factory Method para criar Lexer"""
        lexer = Lexer()
        lexer._add_tokens()
        return lexer.get_lexer()
    
    @staticmethod
    def create_nadia_parser(input_text):
        """Factory Method para criar ParserNadia"""
        return ParserNadia(state=input_text)
    
    @staticmethod
    def create_theorem_parser(input_text):
        """Factory Method para criar ParserTheorem"""
        return ParserTheorem(state=input_text)
    
    @staticmethod
    def create_formula_parser(input_text):
        """Factory Method para criar ParserFormula"""
        return ParserFormula(state=input_text)
    
    @staticmethod
    def create_proof_analyzer(input_text):
        """Factory Method completo para análise de provas"""
        lexer = ParserFactory.create_lexer()
        parser = ParserFactory.create_nadia_parser(input_text)
        return lexer, parser.get_parser()