from ParserFactory.ParserType import ParserType
from ParserFactory.ParserFactory import ParserFactory

class DeductionSystem:
    """Fachada principal do sistema de dedução"""
    
    @staticmethod
    def parse_theorem(theorem_text: str):
        """Parseia um teorema no formato 'premissas conclusão'"""
        parser = ParserFactory.create_parser(ParserType.THEOREM, theorem_text)
        return parser.parse()
    
    @staticmethod
    def parse_formula(formula_text: str):
        """Parseia uma fórmula lógica individual"""
        parser = ParserFactory.create_parser(ParserType.FORMULA, formula_text)
        return parser.parse()
    
    @staticmethod
    def parse_proof(proof_text: str):
        """Parseia uma demonstração completa"""
        parser = ParserFactory.create_parser(ParserType.PROOF, proof_text)
        return parser.parse()
    
    @staticmethod
    def auto_parse(input_text: str):
        """Detecta automaticamente o tipo e parseia"""
        parser = ParserFactory.create_parser_by_content(input_text)
        return parser.parse(), type(parser).__name__
    
    @staticmethod
    def check_proof(proof_text: str, theorem_text: str = None):
        """Verifica uma prova opcionalmente contra um teorema"""
        proof_parser = ParserFactory.create_parser(ParserType.PROOF, proof_text)
        proof_result = proof_parser.parse()
        
        if theorem_text:
            theorem_parser = ParserFactory.create_parser(ParserType.THEOREM, theorem_text)
            theorem_premisses, theorem_conclusion = theorem_parser.parse()
            
            # Lógica de verificação aqui...
            return proof_result, theorem_premisses, theorem_conclusion
        
        return proof_result